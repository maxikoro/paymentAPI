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
    # producer = AIOKafkaProducer(bootstrap_servers='localhost:9094')
    # await producer.start()
    consumer = AIOKafkaConsumer("paymentsResults", bootstrap_servers='localhost:9094', group_id="paymentsResultsGroup")
    await consumer.start()
    asyncio.create_task(consume(consumer))
    yield
    # await producer.stop()
    await consumer.stop()
    await db_pool.close()

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def read_root():
    return {"message": "Hello my friend :) It's a updater service"}
