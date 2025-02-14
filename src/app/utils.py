import httpx
from langdetect import detect

from src.settings.config import logger


async def callback(callback_url, status, data):
    async with httpx.AsyncClient() as client:
        try:
            data["status"] = status
            response = await client.post(callback_url, json=data)
            response.raise_for_status()
            return {"status": status}

        except Exception as e:
            logger.error(e)
            await client.post(callback_url, json={"error": str(e)})


def is_eng_text(text: str) -> bool:
    part_of_text = text[0:100] if len(text) > 100 else text
    return True if detect(part_of_text) == "en" else False
