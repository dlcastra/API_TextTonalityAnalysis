import tempfile

from botocore.exceptions import ClientError

from src.settings.aws_confing import s3_client
from src.settings.config import settings
from src.app.services.analysis import TextTonalityAnalysisService
from src.app.models.res_statuses import Status


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
