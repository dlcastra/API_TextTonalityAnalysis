def get_analysis_service():
    from src.app.services.analysis import TextTonalityAnalysisService

    return TextTonalityAnalysisService()


def get_text_extractor_service():
    from src.app.services.text_extractor import TextExtractorService

    return TextExtractorService()


def get_translator_service():
    from src.app.services.translator import TranslatorService

    return TranslatorService()
