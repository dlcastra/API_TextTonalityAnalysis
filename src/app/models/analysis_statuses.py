from enum import Enum


class PolarityStatus(str, Enum):
    """Represents the sentiment polarity of a text, ranging from extremely negative to extremely positive."""

    EXTREMELY_NEGATIVE = "Extremely negative"  # [-1.0, -0.75]
    VERY_NEGATIVE = "Very negative"  # (-0.75, -0.5]
    NEGATIVE = "Negative"  # (-0.5, -0.1]
    NEUTRAL = "Neutral"  # (-0.1, 0.1]
    POSITIVE = "Positive"  # (0.1, 0.5]
    VERY_POSITIVE = "Very positive"  # (0.5, 0.75]
    EXTREMELY_POSITIVE = "Extremely positive"  # (0.75, 1.0]


class SubjectivityStatus(str, Enum):
    """Represents how objective or subjective a text is, from completely objective to completely subjective."""

    COMPLETELY_OBJECTIVE = "Completely objective"  # [0.0, 0.1]
    RATHER_OBJECTIVE = "Rather objective"  # (0.1, 0.3]
    MIXED = "Mixed"  # (0.3, 0.6]
    RATHER_SUBJECTIVE = "Rather subjective"  # (0.6, 0.8]
    COMPLETELY_SUBJECTIVE = "Completely subjective"  # (0.8, 1.0]


class ObjectiveSentimentStatus(str, Enum):
    """Represents how objectively strong the sentiment of a text is."""

    OBJECTIVE_STRONG_OPINION = "Objective strong opinion"  # [0.75, 1.0]
    RATHER_OBJECTIVE_OPINION = "Rather objective opinion"  # (0.5, 0.75]
    MIXED_OPINION = "Mixed"  # (0.25, 0.5]
    RATHER_SUBJECTIVE_OPINION = "Rather subjective opinion"  # (0.1, 0.25]
    SUBJECTIVE_OPINION = "Completely subjective"  # (0.0, 0.1]


POLARITY_DESCRIPTIONS = {
    "EXTREMELY_NEGATIVE": "Extremely negative sentiment, harsh criticism.",
    "VERY_NEGATIVE": "Strongly negative tone.",
    "NEGATIVE": "Negative sentiment, but not too strong.",
    "NEUTRAL": "No significant emotional tone.",
    "POSITIVE": "Slightly positive tone.",
    "VERY_POSITIVE": "Clearly positive tone.",
    "EXTREMELY_POSITIVE": "Extremely positive sentiment, highly enthusiastic review.",
}

SUBJECTIVITY_DESCRIPTIONS = {
    "COMPLETELY_OBJECTIVE": "Purely factual statements without subjective opinions.",
    "RATHER_OBJECTIVE": "Mostly factual statements with a slight hint of subjectivity.",
    "MIXED": "A mix of subjective and objective statements.",
    "RATHER_SUBJECTIVE": "Mostly subjective statements with some factual elements.",
    "COMPLETELY_SUBJECTIVE": "Entirely opinion-based statements with no factual basis.",
}

OBJECTIVE_SENTIMENT_DESCRIPTIONS = {
    "OBJECTIVE_STRONG_OPINION": "The sentiment is clearly defined and based on facts.",
    "RATHER_OBJECTIVE_OPINION": "The sentiment is noticeable and partly based on facts.",
    "MIXED_OPINION": "A mix of subjective and objective elements, but lacks clear factual argumentation.",
    "RATHER_SUBJECTIVE_OPINION": "The sentiment is present but leans more toward subjectivity.",
    "SUBJECTIVE_OPINION": "Purely opinion-based statement with weak factual support or overly neutral.",
}

POLARITY_RANGES = [
    (-1.0, -0.75, PolarityStatus.EXTREMELY_NEGATIVE),
    (-0.75, -0.5, PolarityStatus.VERY_NEGATIVE),
    (-0.5, -0.1, PolarityStatus.NEGATIVE),
    (-0.1, 0.1, PolarityStatus.NEUTRAL),
    (0.1, 0.5, PolarityStatus.POSITIVE),
    (0.5, 0.75, PolarityStatus.VERY_POSITIVE),
    (0.75, 1.0, PolarityStatus.EXTREMELY_POSITIVE),
]

SUBJECTIVITY_RANGES = [
    (0.0, 0.1, SubjectivityStatus.COMPLETELY_OBJECTIVE),
    (0.1, 0.3, SubjectivityStatus.RATHER_OBJECTIVE),
    (0.3, 0.6, SubjectivityStatus.MIXED),
    (0.6, 0.8, SubjectivityStatus.RATHER_SUBJECTIVE),
    (0.8, 1.0, SubjectivityStatus.COMPLETELY_SUBJECTIVE),
]

OBJECTIVE_SENTIMENT_RANGES = [
    (0.75, 1.0, ObjectiveSentimentStatus.OBJECTIVE_STRONG_OPINION),
    (0.5, 0.75, ObjectiveSentimentStatus.RATHER_OBJECTIVE_OPINION),
    (0.25, 0.5, ObjectiveSentimentStatus.MIXED_OPINION),
    (0.1, 0.25, ObjectiveSentimentStatus.RATHER_SUBJECTIVE_OPINION),
    (0.0, 0.1, ObjectiveSentimentStatus.SUBJECTIVE_OPINION),
]
