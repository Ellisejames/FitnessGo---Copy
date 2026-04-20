# intent_detector.py

import re
from chatbot.intents import INTENTS
from chatbot.data_extractors import (
    extract_height_weight,
    extract_activity_level
)
from chatbot.workout_handler import (
    extract_goal_from_text,
    extract_level_from_text
)

# =========================
# EMOTION SUPPORT KEYWORDS
# =========================
EMOTION_SUPPORT_KEYWORDS = [
    "i feel",
    "i am feeling",
    "frustrated",
    "overwhelmed",
    "tired",
    "sad",
    "burnt out",
    "unmotivated",
    "giving up",
]


def detect_intent(message: str) -> str:
    message = message.lower().strip()

    # ✅ punctuation-safe word list
    words = re.findall(r'\b\w+\b', message)

    # =========================
    # CANCEL / RESET
    # =========================
    if message in ["cancel", "stop", "reset"]:
        return "CANCEL"
    # =========================
    # READ FULL ARTICLE
    # =========================
    if any(phrase in message for phrase in [
        "read more",
        "more details",
        "full article",
        "continue reading",
        "show full article"
    ]):
        return "READ_MORE_ARTICLE"

    # =========================
    # ARTICLES
    # =========================
    if any(word in message for word in ["article", "articles", "tips", "guide"]):
        return "ARTICLES"

    # =========================
    # MOTIVATION
    # =========================
    if any(word in message for word in [
        "motivate", "motivation", "inspire",
        "motivated", "quote", "quotes"
    ]):
        return "MOTIVATION"

    # =========================
    # HELP
    # =========================

    if any(word in words for word in [
        "hi", "hey", "hello", "yo", "sup", "hiya", "kamusta"
    ]):
        return "HELP"

    if any(phrase in message for phrase in [
        "good morning",
        "good afternoon",
        "good evening",
        "what's up",
        "whats up"
    ]):
        return "HELP"
    # =========================
    # BMI AUTO-DETECTION
    # =========================
    bmi_data = extract_height_weight(message)
    if bmi_data.get("height") or bmi_data.get("weight"):
        return "BMI"

    if any(word in message for word in ["bmi", "body mass index"]):
        return "BMI"

    # =========================
    # CALORIES AUTO-DETECTION
    # =========================
    if extract_activity_level(message):
        return "CALORIES"

    if any(word in message for word in ["calorie", "calories", "eat"]):
        return "CALORIES"

    # =========================
    # WORKOUT AUTO-DETECTION
    # =========================
    if extract_goal_from_text(message) or extract_level_from_text(message):
        return "WORKOUT"

    workout_keywords = [
        "workout", "exercise", "training",
        "build muscle", "gain muscle",
        "build muscles", "gain muscles",
        "lose weight", "weight loss",
        "get fit", "fitness plan",
        "exercise plan", "routine"
    ]
    if any(keyword in message for keyword in workout_keywords):
        return "WORKOUT"

    # =========================
    # EMOTION SUPPORT
    # =========================

    if any(keyword in message for keyword in EMOTION_SUPPORT_KEYWORDS):
        return "EMOTION_SUPPORT"

    # =========================
    # FALLBACK
    # =========================
    return "UNKNOWN"