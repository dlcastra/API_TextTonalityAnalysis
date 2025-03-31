import re

from googletrans import Translator

from src.settings.config import logger


class TranslatorService:
    def __init__(self):
        self.translator = Translator()
        self.to_lang = "en"
        self.text = ""

    async def translate_text(self, text: str) -> str | None:
        self.text = text
        cleaned_text = await self.clean_text()

        try:
            result = await self.translator.translate(cleaned_text, dest=self.to_lang)
            logger.info(f"Text translated successfully")
            return result.text
        except Exception as e:
            logger.error(f"TranslatorService {str(e)}")
            return None

    async def clean_text(self) -> str:
        cleaning_args = ["\n", "\t", "\r", "\b"]
        for arg in cleaning_args:
            self.text = re.sub(rf"\s*{re.escape(arg)}\s*", " ", self.text)

        logger.info(f"Text cleaned successfully")
        return self.text
