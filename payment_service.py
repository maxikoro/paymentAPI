import asyncio
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
import random
from model import Payment, PaymentState
from datetime import datetime
import os
import logging

KAFKA_URL = os.getenv("KAFKA_URL", 'localhost:9094')

logging.basicConfig(level=logging.INFO)

async def consume_and_produce():
    consumer = AIOKafkaConsumer(
        'payments',
        bootstrap_servers=KAFKA_URL,
        group_id='paymentsGroup'
    )
    producer = AIOKafkaProducer(
        bootstrap_servers=KAFKA_URL
    )

    await consumer.start()
    await producer.start()
    try:
        async def handle_message(message):
            logging.info("consumed: %s", message.value)
            payment = Payment.model_validate_json(message.value)

            ### здесь имитируется вызов внешнего АПИ для обработки платежа, 
            # которая занимает случайное время от 3 до 25 секунд и 
            # возвращает случайный статус с вероятностью 80% успешно и 20% неуспешно
            delay = random.randint(3, 25)
            if random.random() < 0.8:
                payment.state = PaymentState.COMPLETED
                payment.extPaymentDetails = f"Payment processed in {delay} seconds"
            else:
                payment.state = PaymentState.REJECTED
                payment.extPaymentDetails = f"Payment rejected after {delay} seconds"
            await asyncio.sleep(delay)
            payment.processed = datetime.now().isoformat()

            await producer.send_and_wait('paymentsResults', payment.model_dump_json().encode('utf-8'))
            logging.info("produced: %s", payment)

        tasks = []
        async for message in consumer:
            task = asyncio.create_task(handle_message(message))
            tasks.append(task)

        await asyncio.gather(*tasks)
    finally:
        await consumer.stop()
        await producer.stop()

if __name__ == "__main__":
    asyncio.run(consume_and_produce())