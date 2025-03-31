from fastapi import APIRouter
from pydantic import BaseModel
from starlette.responses import JSONResponse

from src.app.handlers import text_tonality_analysis_handler
from src.app.models.res_statuses import Status
from src.app.utils import callback

router = APIRouter()


class AnalysisRequest(BaseModel):
    s3_key: str
    callback_url: str


@router.post("/tonality")
async def analyse_text_tonality(request: AnalysisRequest) -> JSONResponse:
    try:
        result, status = await text_tonality_analysis_handler(request.s3_key)
        result["s3_key"] = request.s3_key
        response: dict = await callback(request.callback_url, status=status, data=result)
        if response["status"] == Status.SUCCESS:
            return JSONResponse(status_code=201, content={"status": Status.SUCCESS})
        return JSONResponse(status_code=500, content=response)
    except Exception as e:
        return JSONResponse(status_code=500, content={"status": "error", "message": str(e)})
