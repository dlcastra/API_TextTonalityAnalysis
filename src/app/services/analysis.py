import asyncio
import re
from typing import Tuple, Dict, Union

from textblob import TextBlob

from src.app.models.analysis_statuses import (
    POLARITY_DESCRIPTIONS,
    POLARITY_RANGES,
    SUBJECTIVITY_DESCRIPTIONS,
    SUBJECTIVITY_RANGES,
    OBJECTIVE_SENTIMENT_DESCRIPTIONS,
    OBJECTIVE_SENTIMENT_RANGES,
)
from src.app.services import get_text_extractor_service, get_translator_service
from src.app.utils import is_eng_text
from src.settings.config import logger


class TextTonalityAnalysisService:
    def __init__(self):
        self.text_extractor = get_text_extractor_service()
        self.translator = get_translator_service()

    async def file_processing(self, s3_key, file_bytes) -> Tuple[Union[Dict, str], bool]:
        """
        Extracts text from a file and performs sentiment analysis.

        :param s3_key: File name (or key) in the S3 bucket.
        :param file_bytes: File content as a BytesIO object.
        :return:
            - Tuple (`Dict`, `True`) if the analysis is successful. The dictionary contains sentiment metrics.
            - Tuple (`str`, `False`) if an error occurs, with an error message.
        """

        try:
            text, is_extracted = await self.text_extractor.extract_text(s3_key, file_bytes)
            if not is_extracted:
                logger.error(f"TextTonalityAnalysisService: An error occurred while extracting the text")
                return "An error occurred while extracting the text", False

            return await self._sentiment_analysis(text), True
        except Exception as e:
            logger.error(f"TextTonalityAnalysisService {str(e)}")
            return "Internal Error", False

    async def _sentiment_analysis(self, text: str) -> Dict[str, Union[str, float]]:
        """
        Cleans the text, detects the language, translates it if necessary, and then performs sentiment analysis.

        :param text: The input text to be analyzed.
        :return: A dictionary containing:
            - `polarity` (float): Sentiment polarity (-1 to 1, where -1 is negative, 1 is positive).
            - `subjectivity` (float): Subjectivity score (0 to 1, where 0 is objective and 1 is subjective).
            - `objective_sentiment_score` (float): A calculated metric for objective sentiment.
            - `polarity_status` (str): A categorized label describing the polarity.
            - `polarity_description` (str): A human-readable explanation of the polarity score.
            - `subjectivity_status` (str): A categorized label describing the subjectivity.
            - `subjectivity_description` (str): A human-readable explanation of the subjectivity score.
            - `objective_sentiment_status` (str): A categorized label for the objective sentiment score.
            - `objective_sentiment_description` (str): A human-readable explanation of the objective sentiment score.
        """
        logger.info(f"Performing sentiment analysis on the text")

        cleared_text = re.sub(r"\s*\n\s*", " ", text)
        if not await asyncio.to_thread(is_eng_text, cleared_text):
            (cleared_text,) = await self.translator.translate_text(cleared_text)

        analysed_text = TextBlob(cleared_text)
        polarity = analysed_text.sentiment.polarity
        subjectivity = analysed_text.sentiment.subjectivity
        objective_sentiment_score = await self._calculate_objective_sentiment(polarity, subjectivity)

        analyse_data = await self._generate_status_and_description(polarity, subjectivity, objective_sentiment_score)
        response = {
            "polarity": polarity,
            "subjectivity": subjectivity,
            "objective_sentiment_score": objective_sentiment_score,
        }
        response.update(analyse_data)

        logger.info(f"Sentiment analysis completed successfully")
        return response

    async def _generate_status_and_description(
        self, polarity_score, subjectivity_score, objective_sentiment_score
    ) -> Dict[str, str]:
        """
        Converts numerical sentiment scores into categorized labels and descriptions.

        :param polarity_score: Sentiment polarity score.
        :param subjectivity_score: Subjectivity score.
        :param objective_sentiment_score: Objective sentiment score.
        :return: A dictionary containing:
            - `polarity_status`: A categorized label for the polarity.
            - `polarity_description`: A description of the polarity score.
            - `subjectivity_status`: A categorized label for the subjectivity.
            - `subjectivity_description`: A description of the subjectivity score.
            - `objective_sentiment_status`: A categorized label for the objective sentiment.
            - `objective_sentiment_description`: A description of the objective sentiment score.
        """

        logger.info(f"Starting to generate status and description for sentiment scores")

        def get_status(score, ranges):
            logger.info(f"Calculating status for score: {score}")
            return next((status for min_val, max_val, status in ranges if min_val <= score < max_val), None)

        logger.info(f"Generating status and description for sentiment scores")
        polarity_status = get_status(polarity_score, POLARITY_RANGES)
        subjectivity_status = get_status(subjectivity_score, SUBJECTIVITY_RANGES)
        objective_sentiment_status = get_status(objective_sentiment_score, OBJECTIVE_SENTIMENT_RANGES)

        logger.info(f"Status and description generated successfully")
        return {
            "polarity_status": polarity_status.value,
            "polarity_description": POLARITY_DESCRIPTIONS.get(polarity_status.name),
            "subjectivity_status": subjectivity_status.value,
            "subjectivity_description": SUBJECTIVITY_DESCRIPTIONS.get(subjectivity_status.name),
            "objective_sentiment_status": objective_sentiment_status.value,
            "objective_sentiment_description": OBJECTIVE_SENTIMENT_DESCRIPTIONS.get(objective_sentiment_status.name),
        }

    async def _calculate_objective_sentiment(self, polarity_score, subjectivity_score) -> float:
        """
        Calculates an objective sentiment score based on polarity and subjectivity.

        :param polarity_score: Sentiment polarity (-1 to 1).
        :param subjectivity_score: Subjectivity score (0 to 1).
        :return: A float representing the objective sentiment score, where higher values indicate
                 stronger objective sentiment.
        """

        logger.info(f"Calculating objective sentiment score")
        if subjectivity_score == 1:
            return 0.0

        adjusted_polarity = abs(polarity_score) ** 0.8
        adjusted_subjectivity = 1 - subjectivity_score**2

        logger.info(f"Objective sentiment score calculated successfully")
        return adjusted_polarity * adjusted_subjectivity
