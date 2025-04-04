import asyncio
import threading

from fastapi import FastAPI, APIRouter

from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

from src.app.aws.handlers import process_sqs_messages
from src.app.routers import analysis
from src.app.aws.clients import sqs_client

app = FastAPI()
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(analysis.router, prefix="/analysis", tags=["Analysis"])
app.include_router(api_router)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = [{"field": err["loc"][-1], "msg": err["msg"]} for err in exc.errors()]
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": errors},
    )


@app.on_event("startup")
async def startup_event():
    thread = threading.Thread(target=asyncio.run, args=(process_sqs_messages(sqs_client),))
    thread.daemon = True
    thread.start()
