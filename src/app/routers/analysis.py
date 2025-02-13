from fastapi import APIRouter
from pydantic import BaseModel

from src.app.handlers import text_tonality_analysis_handler
from src.app.utils import callback

router = APIRouter()


class AnalysisRequest(BaseModel):
    s3_key: str
    callback_url: str


@router.post("/tonality")
async def analyse_text_tonality(request: AnalysisRequest):
    result, status = await text_tonality_analysis_handler(request.s3_key)
    return await callback(callback_url=request.callback_url, status=status, data=result)
