from typing import Tuple, Dict

from botocore.exceptions import ClientError

from src.app.aws.utils import download_file_as_bytes
from src.app.models.res_statuses import Status
from src.app.services import get_analysis_service
from src.settings.config import settings, logger


async def text_tonality_analysis_handler(s3_key) -> Tuple[Dict, str]:
    """
    Handles the text tonality analysis process.

    :param s3_key: File name (or key) in the S3 bucket.
    :return:
        - Tuple (`Dict`, `str`) where the dictionary contains sentiment metrics and the string is the status message.
    """

    analysis_service = get_analysis_service()
    bucket = settings.AWS_S3_BUCKET_NAME

    try:
        download_result, is_downloaded = await download_file_as_bytes(bucket, s3_key)
        if not is_downloaded:
            logger.error(f"File download failed. Details: {download_result}")
            return {"message": download_result}, Status.ERROR

        result, is_processed = await analysis_service.file_processing(s3_key, download_result)
        if not is_processed:
            return {"message": result}, Status.ERROR.value

        return result, Status.SUCCESS.value

    except ClientError as error:
        return {"message": error.response["Error"]["Message"]}, Status.ERROR.value
