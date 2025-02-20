import aiofiles
import fitz
from docx import Document


class ExtractTextorService:
    async def extract_text(self, file_path) -> tuple[str, None or True]:
        try:
            if file_path.endswith(".txt"):
                return await self._extract_text_from_txt(file_path), True
            elif file_path.endswith(".docx"):
                return await self._extract_text_from_docx(file_path), True
            elif file_path.endswith(".pdf"):
                return await self._extract_text_from_pdf(file_path), True
        except Exception as e:
            return f"ExtractTextorService {str(e)}", None

        return "Unsupported file type", None

    async def _extract_text_from_txt(self, file_path):
        async with aiofiles.open(file=file_path, mode="r", encoding="utf-8") as file:
            result = await file.read()
            return result

    async def _extract_text_from_docx(self, file_path):
        doc = Document(file_path)
        result = " ".join([para.text for para in doc.paragraphs if para.text.strip()])
        return result

    async def _extract_text_from_pdf(self, file_path):
        doc = fitz.open(file_path)
        result = " ".join([page.get_text() for page in doc.pages()])
        return result
