from fastapi import FastAPI, status
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

# Consume and save messages to PostgreSQL
async def consume(consumer: AIOKafkaConsumer):
    async with db_pool.acquire() as connection:
        while True:
            async for msg in consumer:
                print("consumed: ", msg.value)
                payment = Payment.model_validate_json(msg.value)
                await connection.execute(
                    "UPDATE payment SET state = $2, processed = $3, ext_payment_details = $4 WHERE payment_id = $1",
                    payment.paymentId, payment.state, datetime.fromisoformat(payment.processed), payment.extPaymentDetails
                )

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, producer
    db_pool = await asyncpg.create_pool(dsn="postgresql://paymentuser:s3cure@localhost:35432/paymentdb")
    producer = AIOKafkaProducer(bootstrap_servers='localhost:9094')
    await producer.start()
    consumer = AIOKafkaConsumer("paymentsResults", bootstrap_servers='localhost:9094', group_id="paymentsResultsGroup")
    await consumer.start()
    asyncio.create_task(consume(consumer))
    yield
    await producer.stop()
    await consumer.stop()
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello my friend :) It's a payment service"}

@app.post("/payments/")
async def read_item(payment: Payment):
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
        return {"error": "Payment not found"}