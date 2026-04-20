# emotion_detector.py
import re


def detect_emotion(message: str) -> str:
    """
    Detects the user's emotional state based on keywords/phrases.
    Returns one of: 'fatigued', 'frustrated', 'discouraged', 'anxious', 'motivated', 'neutral'.
    """
    text = message.lower()

    # --------------------------
    # Fatigue / Worn out
    # --------------------------
    if re.search(r'\b(tired|exhausted|burnt out|overwhelmed|sleepy)\b', text):
        return "fatigued"

    # --------------------------
    # Frustration / Anger
    # --------------------------
    if re.search(r'\b(frustrated|annoyed|angry|irritated|upset|mad)\b', text):
        return "frustrated"

    # --------------------------
    # Discouragement / Sadness
    # --------------------------
    if re.search(r'\b(sad|discouraged|giving up|hopeless|disappointed|unmotivated)\b', text):
        return "discouraged"

    # --------------------------
    # Anxiety / Worry / Stress
    # --------------------------
    if re.search(r'\b(anxious|worried|scared|nervous|stressed)\b', text):
        return "anxious"

    # --------------------------
    # Motivation / Excitement
    # --------------------------
    if re.search(r'\b(excited|motivated|ready|determined|energized|energetic)\b', text):
        return "motivated"

    # --------------------------
    # Default / Neutral
    # --------------------------
    return "neutral"
