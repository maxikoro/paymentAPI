from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import uuid
from contextlib import asynccontextmanager
import asyncio
import asyncpg
from datetime import datetime
from model import Payment


# Глобальные переменные для пула подключений и продюсера
db_pool = None
producer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, producer
    db_pool = await asyncpg.create_pool(dsn="postgresql://paymentuser:s3cure@localhost:35432/paymentdb")
    producer = AIOKafkaProducer(bootstrap_servers='localhost:9094')
    await producer.start()
    # consumer = AIOKafkaConsumer("paymentsResults", bootstrap_servers='localhost:9094', group_id="paymentsResultsGroup")
    # await consumer.start()
    # asyncio.create_task(consume(consumer))
    yield
    await producer.stop()
    # await consumer.stop()
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello my friend :) It's a payment service"}

@app.post("/payments/")
async def create_payment(payment: Payment):
    payment.paymentId = str(uuid.uuid4())
    created = datetime.now()
    payment.created = created.isoformat()
    async with db_pool.acquire() as connection:
        await connection.execute(
            "INSERT INTO payment(payment_id, user_id, created, state, account_number, amount, description) VALUES($1, $2, $3, $4, $5, $6, $7)",
            payment.paymentId, payment.userId, created, payment.state, payment.accountNumber, payment.amount, payment.description
        )
    await producer.send_and_wait("payments", payment.model_dump_json().encode("utf-8"))
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=payment.model_dump())

@app.get("/payments/{payment_id}")
async def get_payment(payment_id: str):
    async with db_pool.acquire() as connection:
        result = await connection.fetchrow("SELECT * FROM payment WHERE payment_id = $1", payment_id)
        if result:
            return dict(result)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")

@app.get("/payments/lp/{payment_id}")
async def long_poll_payment(payment_id: str):
    timeout = 10  # seconds
    start_time = datetime.now()

    while (datetime.now() - start_time).seconds < timeout:
        async with db_pool.acquire() as connection:
            result = await connection.fetchrow("SELECT * FROM payment WHERE payment_id = $1", payment_id)
            if result:
                payment = dict(result)
                if payment['state'] != 'pending':
                    return payment
            else:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment not found")
        await asyncio.sleep(1)  # wait for 1 second before next check

    raise HTTPException(status_code=status.HTTP_408_REQUEST_TIMEOUT, detail="Timeout: Payment status did not change from pending within 10 seconds")