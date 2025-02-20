import asyncio
import json
import tempfile

from botocore.exceptions import ClientError

from src.app.models.res_statuses import Status
from src.app.services.analysis import TextTonalityAnalysisService
from src.app.utils import callback
from src.settings.aws_confing import s3_client
from src.settings.config import settings


def get_analysis_service() -> TextTonalityAnalysisService:
    return TextTonalityAnalysisService()


async def text_tonality_analysis_handler(s3_key):
    service = TextTonalityAnalysisService()

    with tempfile.TemporaryDirectory() as tmpdir:
        file_path = f"{tmpdir}/{s3_key}"
        try:
            s3_client.download_file(settings.AWS_S3_BUCKET_NAME, s3_key, file_path)
        except ClientError as error:
            return error.response["Error"]["Message"], Status.ERROR.value

        result, is_processed = await service.file_processing(file_path)
        if not is_processed:
            return result, Status.ERROR.value

        return result, Status.SUCCESS.value


async def process_sqs_messages(sqs_client):
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


async def handle_message(sqs_client, message: dict, s3_key: str, callback_url: str):
    result, status = await text_tonality_analysis_handler(s3_key)
    await callback(callback_url=callback_url, status=status, data=result)
    sqs_client.delete_message(QueueUrl=settings.AWS_SQS_QUEUE_URL, ReceiptHandle=message["ReceiptHandle"])
