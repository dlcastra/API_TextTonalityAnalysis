import asyncio
import re

import aiofiles
import fitz
from docx import Document
from textblob import TextBlob

from src.app.utils import is_eng_text
from src.app.services.translator import TranslatorService
from src.app.models.analysis_statuses import (
    POLARITY_DESCRIPTIONS,
    POLARITY_RANGES,
    SUBJECTIVITY_DESCRIPTIONS,
    SUBJECTIVITY_RANGES,
    OBJECTIVE_SENTIMENT_DESCRIPTIONS,
    OBJECTIVE_SENTIMENT_RANGES,
)


class TextTonalityAnalysisService:
    def __init__(self):
        self.translator = TranslatorService()

    async def file_processing(self, file_path):
        try:
            if file_path.endswith(".txt"):
                return await self._analyse_text_from_txt(file_path), True
            elif file_path.endswith(".docx"):
                return await self._analyse_text_from_docx(file_path), True
            elif file_path.endswith(".pdf"):
                return await self._analyse_text_from_pdf(file_path), True
        except Exception as e:
            return str(e), None

        return "Unsupported file type", None

    async def _analyse_text_from_txt(self, file_path):
        async with aiofiles.open(file=file_path, mode="r", encoding="utf-8") as file:
            result = await file.read()
            return await self._sentiment_analysis(result)

    async def _analyse_text_from_docx(self, file_path):
        doc = Document(file_path)
        result = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
        return await self._sentiment_analysis(result)

    async def _analyse_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        result = " ".join([page.get_text() for page in doc.pages()])
        return await self._sentiment_analysis(result)

    async def _sentiment_analysis(self, text):
        cleared_text = re.sub(r"\s*\n\s*", " ", text)

        if not await asyncio.to_thread(is_eng_text, cleared_text):
            cleared_text = await self.translator.translate_text(cleared_text)

        analysed_text = TextBlob(cleared_text[0])
        polarity = analysed_text.sentiment.polarity
        subjectivity = analysed_text.sentiment.subjectivity
        objective_sentiment_score = self._calculate_objective_sentiment(polarity, subjectivity)

        analyse_data = await self._generate_status_and_description(polarity, subjectivity, objective_sentiment_score)
        response = {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "objective_sentiment_score": objective_sentiment_score,
        }
        response.update(analyse_data)

        return response

    async def _generate_status_and_description(self, polarity_score, subjectivity_score, objective_sentiment_score):
        def get_status(score, ranges):
            return next((status for min_val, max_val, status in ranges if min_val <= score < max_val), None)

        polarity_status = get_status(polarity_score, POLARITY_RANGES)
        subjectivity_status = get_status(subjectivity_score, SUBJECTIVITY_RANGES)
        objective_sentiment_status = get_status(objective_sentiment_score, OBJECTIVE_SENTIMENT_RANGES)

        return {
            "polarity_status": polarity_status.value,
            "polarity_description": POLARITY_DESCRIPTIONS.get(polarity_status.name),
            "subjectivity_status": subjectivity_status.value,
            "subjectivity_description": SUBJECTIVITY_DESCRIPTIONS.get(subjectivity_status.name),
            "objective_sentiment_status": objective_sentiment_status.value,
            "objective_sentiment_description": OBJECTIVE_SENTIMENT_DESCRIPTIONS.get(objective_sentiment_status.name),
        }

    def _calculate_objective_sentiment(self, polarity_score, subjectivity_score):
        if subjectivity_score == 1:
            return 0.0

        adjusted_polarity = abs(polarity_score) ** 0.8
        adjusted_subjectivity = 1 - subjectivity_score**2
        return adjusted_polarity * adjusted_subjectivity
