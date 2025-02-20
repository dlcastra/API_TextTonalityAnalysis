import asyncio
import re

from textblob import TextBlob

from src.app.models.analysis_statuses import (
    POLARITY_DESCRIPTIONS,
    POLARITY_RANGES,
    SUBJECTIVITY_DESCRIPTIONS,
    SUBJECTIVITY_RANGES,
    OBJECTIVE_SENTIMENT_DESCRIPTIONS,
    OBJECTIVE_SENTIMENT_RANGES,
)
from src.app.services.text_extractor import ExtractTextorService
from src.app.services.translator import TranslatorService
from src.app.utils import is_eng_text


class TextTonalityAnalysisService:
    def __init__(self):
        self.text_extractor = ExtractTextorService()
        self.translator = TranslatorService()

    async def file_processing(self, file_path):
        text, is_extracted = await self.text_extractor.extract_text(file_path)
        if not is_extracted:
            return "An error occurred while extracting the text", None

        try:
            return await self._sentiment_analysis(text), True
        except Exception as e:
            return f"TextTonalityAnalysisService {str(e)}", None

    async def _sentiment_analysis(self, text):
        cleared_text = re.sub(r"\s*\n\s*", " ", text)
        if not await asyncio.to_thread(is_eng_text, cleared_text):
            cleared_text = await self.translator.translate_text(cleared_text)

        analysed_text = TextBlob(cleared_text)
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
