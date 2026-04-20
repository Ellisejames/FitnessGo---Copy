import random

EMPATHY_TEMPLATES = {
    "frustrated": [
        "I know this can feel frustrating.",
        "It’s understandable to feel stuck sometimes.",
        "This part can be challenging, and that’s okay."
    ],
    "discouraged": [
        "You’re not failing—progress isn’t always linear.",
        "It’s okay to slow down when things feel heavy.",
        "I’m really glad you’re still showing up."
    ],
    "anxious": [
        "No pressure—we’ll take this one step at a time.",
        "You don’t need to rush. We can go at your pace.",
        "It’s okay to feel unsure sometimes."
    ],
    "fatigued": [
        "It sounds like you’re feeling worn out.",
        "Let’s keep things simple and manageable today.",
        "Rest and balance are part of progress too."
    ],
    "motivated": [
        "I love that energy!",
        "That motivation will really support your goals.",
        "Let’s put that momentum to good use."
    ],
    "neutral": []
}


def get_empathy_phrase(emotion: str) -> str:
    options = EMPATHY_TEMPLATES.get(emotion, [])
    return random.choice(options) + "\n\n" if options else ""
