# emotion_support_flow.py
from chatbot.empathy_templates import get_empathy_phrase
from chatbot.conversation_manager import ConversationState


def start_emotion_support_flow(user_id, session, emotion):
    empathy_prefix = get_empathy_phrase(emotion)
    response = (
        f"{empathy_prefix}"
        "It’s alright to feel this way.\n\n"
        "Emotions can affect motivation, energy, and focus—and that’s completely normal.\n\n"
        "Here’s what I can help you with right now:\n"
        "• Read wellness and fitness articles\n"
        "• Get motivation (type: 'motivate me')\n"
        "• Use fitness features like BMI, calories, or workouts\n\n"
        "Just tell me what you’d like to do next."
    )

    session.reset()
    return response
