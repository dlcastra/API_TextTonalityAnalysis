from io import BytesIO
from typing import Tuple, Union

import fitz
from docx import Document

from src.settings.config import logger


class TextExtractorService:
    async def extract_text(self, s3_key, file_bytes) -> Tuple[Union[str, None], bool]:
        """
        Extracts text from a file bytes steam based on the file extension.

        :param s3_key: File name (or key) in the S3 bucket.
        :param file_bytes: File content as a BytesIO object.
        :return:
        """

        try:
            if s3_key.endswith(".txt"):
                return await self._extract_text_from_txt(file_bytes)
            elif s3_key.endswith(".docx"):
                return await self._extract_text_from_docx(file_bytes)
            elif s3_key.endswith(".pdf"):
                return await self._extract_text_from_pdf(file_bytes)
        except Exception as e:
            logger.error(f"TextExtractorService {str(e)}")
            return None, False

        return "Unsupported file type", False

    async def _extract_text_from_txt(self, file_bytes: BytesIO) -> Tuple[Union[str, None], bool]:
        """
        Extracts text from a text file.

        :param file_bytes: File content as a BytesIO object.
        :return:
            - Tuple (`str`, `True`) if the text is extracted successfully.
            - Tuple (`None`, `False`) if an error occurs.
        """

        try:
            logger.info(f"Extracting text from TXT file")
            return file_bytes.getvalue().decode("utf-8"), True
        except Exception as e:
            logger.error(f"TextExtractorService {str(e)}")
            return None, False

    async def _extract_text_from_docx(self, file_bytes: BytesIO) -> Tuple[Union[str, None], bool]:
        """
        Extracts text from a DOCX file bytes using the `python-docx` library.

        :param file_bytes:  File content as a BytesIO object.
        :return:
            - Tuple (`str`, `True`) if the text is extracted successfully.
            - Tuple (`None`, `False`) if an error occurs.
        """

        try:
            logger.info(f"Starting text extraction from DOCX file")
            doc = Document(file_bytes)
            result = " ".join([para.text for para in doc.paragraphs if para.text.strip()])

            logger.info(f"Text extracted successfully")
            return result, True
        except Exception as e:
            logger.error(f"TextExtractorService {str(e)}")
            return None, False

    async def _extract_text_from_pdf(self, file_bytes: BytesIO) -> Tuple[Union[str, None], bool]:
        """
        Extracts text from a PDF file bytes using the `PyMuPDF` library.

        :param file_bytes: File content as a BytesIO object.
        :return:
            - Tuple (`str`, `True`) if the text is extracted successfully.
            - Tuple (`None`, `False`) if an error occurs
        """

        try:
            logger.info(f"Starting text extraction from PDF file")
            doc = fitz.open("pdf", file_bytes.read())
            result = " ".join([page.get_text() for page in doc.pages()])

            logger.info(f"Text extracted successfully")
            return result, True
        except Exception as e:
            logger.error(f"TextExtractorService {str(e)}")
            return None, False
