import asyncio
import json

from src.app.handlers import text_tonality_analysis_handler
from src.app.utils import callback
from src.settings.config import settings


async def process_sqs_messages(sqs_client) -> None:
    while True:
        response = sqs_client.receive_message(
            QueueUrl=settings.AWS_SQS_QUEUE_URL, MaxNumberOfMessages=10, WaitTimeSeconds=20, VisibilityTimeout=30
        )

        if "Messages" in response:
            tasks = []
            for message in response["Messages"]:
                message_body = json.loads(message["Body"])
                s3_key = message_body.get("s3_key")
                callback_url = message_body.get("callback_url")

                if s3_key and callback_url:
                    tasks.append(asyncio.create_task(handle_message(sqs_client, message, s3_key, callback_url)))

            await asyncio.gather(*tasks)

        else:
            await asyncio.sleep(0.5)


async def handle_message(sqs_client, message: dict, s3_key: str, callback_url: str) -> None:
    result, status = await text_tonality_analysis_handler(s3_key)
    result["s3_key"] = s3_key
    await callback(callback_url=callback_url, status=status, data=result)
    sqs_client.delete_message(QueueUrl=settings.AWS_SQS_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])
