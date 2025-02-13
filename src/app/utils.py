import httpx

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
