from fastapi import FastAPI, status, HTTPException
from fastapi.responses import JSONResponse
from aiokafka import AIOKafkaProducer, AIOKafkaConsumer
import uuid
from contextlib import asynccontextmanager
import asyncio
import asyncpg
from datetime import datetime
from model import Payment
import os
import logging

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://paymentuser:s3cure@localhost:35432/paymentdb")
KAFKA_URL = os.getenv("KAFKA_URL", 'localhost:9094')

logging.basicConfig(level=logging.INFO)

# Глобальные переменные для пула подключений и продюсера
db_pool = None
producer = None

# Consume and save messages to PostgreSQL
async def consume(consumer: AIOKafkaConsumer):
    async with db_pool.acquire() as connection:
        while True:
            async for msg in consumer:
                logging.info("consumed: %s", msg.value)
                payment = Payment.model_validate_json(msg.value)
                await connection.execute(
                    "UPDATE payment SET state = $2, processed = $3, ext_payment_details = $4 WHERE payment_id = $1",
                    payment.paymentId, payment.state, datetime.fromisoformat(payment.processed), payment.extPaymentDetails
                )

@asynccontextmanager
async def lifespan(app: FastAPI):
    global db_pool, producer
    db_pool = await asyncpg.create_pool(dsn=DATABASE_URL)
    # producer = AIOKafkaProducer(bootstrap_servers=KAFKA_URL)
    # await producer.start()
    consumer = AIOKafkaConsumer("paymentsResults", bootstrap_servers=KAFKA_URL, group_id="paymentsResultsGroup")
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
