import asyncio
from concurrent import futures
from io import BytesIO
from typing import Tuple, Union

from botocore.exceptions import BotoCoreError, ClientError

from src.app.aws.clients import s3_client
from src.app.aws.responses import AWSErrorResponse
from src.settings.config import logger


def sync_download_file_as_bytes(bucket: str, s3_key: str) -> Tuple[Union[BytesIO, str], bool]:
    """
    Downloads a file from S3 and returns it as BytesIO object.

    :param bucket: S3 bucket name.
    :param s3_key: Destination file name in S3.
    :return: A Tuple (`BytesIO`, `True`) if the download is successful.
             A Tuple (`str`, `False`) if the download fails.
    """

    try:
        response = s3_client.get_object(Bucket=bucket, Key=s3_key)
        logger.info(f"File {s3_key} downloaded from S3")
        return BytesIO(response["Body"].read()), True
    except (BotoCoreError, ClientError) as e:
        logger.error(f"Failed to download file from S3: {str(e)}")
        return AWSErrorResponse.ERROR_DOWNLOAD_FILE, False


async def download_file_as_bytes(bucket: str, s3_key: str) -> Tuple[Union[BytesIO, str], bool]:
    """
    Downloads a file from S3 and returns it as BytesIO object.

    :param bucket: S3 bucket name.
    :param s3_key: Destination file name in S3.
    :return: A Tuple (`BytesIO`, True) if the download is successful.
             A Tuple (None, False) if the download fails.
    """

    loop = asyncio.get_event_loop()
    with futures.ThreadPoolExecutor() as pool:
        result = await loop.run_in_executor(pool, sync_download_file_as_bytes, bucket, s3_key)

    return result
