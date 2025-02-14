import re

from googletrans import Translator


class TranslatorService:
    def __init__(self):
        self.translator = Translator()
        self.to_lang = "en"
        self.text = ""

    async def translate_text(self, text: str):
        self.text = text
        cleaned_text = await self.clean_text()

        try:
            result = await self.translator.translate(cleaned_text, dest=self.to_lang)
            return result.text, True
        except Exception as e:
            return str(e), None

    async def clean_text(self):
        cleaning_args = ["\n", "\t", "\r", "\b"]
        for arg in cleaning_args:
            self.text = re.sub(rf"\s*{re.escape(arg)}\s*", " ", self.text)

        return self.text
