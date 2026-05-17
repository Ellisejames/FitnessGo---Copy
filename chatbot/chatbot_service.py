# chatbot/chatbot_service.py
from chatbot.emotion_support_flow import start_emotion_support_flow
from chatbot.empathy_templates import get_empathy_phrase
from chatbot.emotion_detector import detect_emotion
import re
from typing import Optional
import logging

from chatbot.intent_detector import detect_intent
from chatbot.conversation_manager import conversation_manager
from chatbot.data_extractors import (
    extract_height_weight, extract_activity_level,
    calculate_bmi, extract_numbers
)
from chatbot.workout_handler import (
    extract_goal_from_text, extract_level_from_text,
    extract_condition_from_text, get_workout_plan, format_workout_plan
)
from chatbot.motivation_handler import get_random_quote
from chatbot.articles_handler import (
    search_articles,
    get_random_article,
    format_article,
    get_full_article,
    last_article_cache
)
import time
from backend.my_connector import auth_tbl

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import from your existing code (optional for testing)
try:
    from my_connector import AuthTbl
    auth_tbl = AuthTbl()
    USE_DATABASE = True
except ImportError:
    USE_DATABASE = False
    logger.warning("⚠️ Database connector not available - using fallback mode")


# ✅ Runtime session holder for DB-less operation
runtime_sessions = {}


def normalize_goal(goal_text: str) -> str:
    """
    ✅ NEW: Normalize goal text to standard format
    Ensures consistent goal strings across all flows
    """
    if not goal_text:
        return goal_text

    mapping = {
        "lose weight": "lose_weight",
        "weight loss": "lose_weight",
        "losing weight": "lose_weight",
        "cut": "lose_weight",
        "slim down": "lose_weight",

        "gain weight": "gain_weight",
        "bulk": "gain_weight",
        "bulk up": "gain_weight",
        "weight gain": "gain_weight",

        "gain muscles": "gain_muscles",
        "gain muscle": "gain_muscles",
        "build muscle": "gain_muscles",
        "build muscles": "gain_muscles",
        "get ripped": "gain_muscles",
        "muscle gain": "gain_muscles",

        "keep fit": "keep_fit",
        "maintain": "keep_fit",
        "stay fit": "keep_fit",
        "maintenance": "keep_fit",
        "stay healthy": "keep_fit"
    }

    return mapping.get(goal_text.lower().strip(), goal_text.lower().strip())


def get_runtime_session(user_id: int) -> dict:
    """
    ✅ FIXED: Get or create runtime session with ALL required keys
    """
    if user_id not in runtime_sessions:
        runtime_sessions[user_id] = {
            "partial_bmi_data": {},
            "partial_calorie_data": {},
            "partial_workout_data": {},
            "partial_goal_data": {},  # ✅ ADDED: Initialize goal data
            "last_updated": time.time()
        }

    # Update last accessed time
    runtime_sessions[user_id]["last_updated"] = time.time()
    return runtime_sessions[user_id]


def merge_partial_data(user_id: int, flow_key: str, extracted_data: dict) -> dict:
    """
    ✅ FIXED: Merge runtime session partial data with newly extracted data

    Args:
        user_id: User identifier
        flow_key: Unique key for flow (e.g., "partial_bmi_data")
        extracted_data: Newly extracted data from user message

    Returns:
        Merged data dictionary
    """
    runtime_session = get_runtime_session(user_id)

    # ✅ Ensure flow_key exists in runtime session
    if flow_key not in runtime_session:
        runtime_session[flow_key] = {}

    partial_data = runtime_session[flow_key]

    # Merge partial data into extracted_data
    for key, value in partial_data.items():
        if key not in extracted_data or not extracted_data[key]:
            extracted_data[key] = value

    # Update runtime session with new data
    for key, value in extracted_data.items():
        if value:
            partial_data[key] = value

    return extracted_data


def sync_runtime_to_db(user_id):
    """Sync runtime data to database if available"""
    if not USE_DATABASE or user_id not in runtime_sessions:
        return

    try:
        runtime_data = runtime_sessions[user_id]

        # Sync BMI data if available
        bmi_data = runtime_data.get("partial_bmi_data", {})
        if bmi_data.get("height") and bmi_data.get("weight"):
            auth_tbl.update_user_metrics(
                user_id=user_id,
                height=bmi_data["height"],
                weight=bmi_data["weight"]
            )

        logger.info(f"✅ Runtime session synced to DB for user {user_id}")
    except Exception as e:
        logger.error(f"⚠️ Failed to sync runtime session to DB: {str(e)}")


def handle_cancel_request(user_id: int, session) -> str:
    """
    ✅ Handle cancel request from user
    Clears all partial data and resets session
    """
    session.reset()

    # Clear runtime session too
    runtime_session = get_runtime_session(user_id)
    runtime_session["partial_bmi_data"] = {}
    runtime_session["partial_calorie_data"] = {}
    runtime_session["partial_workout_data"] = {}
    runtime_session["partial_goal_data"] = {}

    # Clear from conversation manager
    conversation_manager.clear_partial_flow(user_id)

    return ("[b]No worries at all![/b]\n\n"
            "You can start fresh anytime. What would you like to do?\n\n"
            "• Calculate BMI\n"
            "• Get calorie estimate\n"
            "• Find a workout plan\n"
            "• Read fitness articles\n"
            "• Get motivated")


def handle_wrong_input(user_id: int, session, flow: str, error_message: str) -> str:
    """
    ✅ Handle wrong input with strike counting
    """
    # Increment wrong input counter
    count = session.increment_wrong_input(flow)

    response = f"❌ {error_message}\n\n"

    if count >= 2:
        # Reset flow step but keep user in flow
        session.flow_step = 0

        # Two strikes - prompt to cancel
        response += ("[b]Having trouble?[/b] You can:\n"
                     "• Try again with a different answer\n"
                     "• Type [b]'cancel'[/b] to start over\n"
                     "• Type [b]'help'[/b] for examples")

    return response


def is_empty_or_nonsense(text: str, expect_numeric: bool = False) -> bool:
    """
    ✅ Check if input is empty or nonsense
    """
    text = text.strip()

    # Empty check
    if not text or len(text) < 2:
        return True

    # If expecting numeric input (BMI, weight, height)
    if expect_numeric:
        # Check if there's at least one digit
        return not bool(re.search(r'\d', text))

    # For text input: check if only special characters (no letters OR numbers)
    if re.match(r'^[^a-zA-Z0-9]+$', text):
        return True

    return False


def validate_numeric_input(text: str, min_val: float = None, max_val: float = None) -> Optional[float]:
    """
    ✅ Validate and extract numeric input
    """
    try:
        # Try to extract numbers from text
        numbers = re.findall(r'\d+\.?\d*', text)
        if not numbers:
            return None

        value = float(numbers[0])

        # Check range if specified
        # Handle unrealistic single-digit values
        if value < 10:  # e.g., height <10cm or weight <10kg
            return None

        if min_val is not None and value < min_val:
            return None
        if max_val is not None and value > max_val:
            return None

        return value
    except (ValueError, IndexError):
        return None


def calculate_daily_goal_readonly(user_id: int, activity: str, goal: str) -> int:
    """
    ✅ READ-ONLY wrapper for AI calorie simulation
    """
    if not USE_DATABASE:
        raise Exception("Database not available")

    try:
        # ✅ READ-ONLY: Fetch user data
        user_data = auth_tbl.get_user_by_id(user_id)

        if not user_data:
            raise Exception("User profile not found")

        # ✅ READ-ONLY: Calculate using profile data + AI simulation inputs
        ai_calculated_calories = auth_tbl.calculate_daily_goal(
            weight=user_data.get('weight', 70),
            height=user_data.get('height', 170),
            age=user_data.get('age', 30),
            gender=user_data.get('gender', 'male'),
            activity=activity,
            goal=goal,
            health_condition=user_data.get('specific_condition', 'none')
        )

        return ai_calculated_calories
    except Exception as e:
        logger.error(f"⚠️ Error in calculate_daily_goal_readonly: {str(e)}")
        raise


def cleanup_old_sessions(max_age_seconds=3600):
    """
    Clean up old runtime sessions (older than 1 hour by default)
    """
    current_time = time.time()
    to_remove = []

    for user_id, session_data in runtime_sessions.items():
        if current_time - session_data.get("last_updated", 0) > max_age_seconds:
            to_remove.append(user_id)

    for user_id in to_remove:
        del runtime_sessions[user_id]

    if to_remove:
        logger.info(f"🧹 Cleaned up {len(to_remove)} old runtime sessions")


def process_message(message: str, user_id: int) -> str:
    """
    Main message processing function with proper flow protection

    ✅ FIXED: Prevents flow interruption
    ✅ FIXED: Only calls detect_intent() once
    ✅ FIXED: Prioritizes active flows over new intent detection
    """
    try:
        session = conversation_manager.get_session(user_id)

        # Ensure collected_data exists
        if not hasattr(session, "collected_data") or session.collected_data is None:
            session.collected_data = {}

        # ============================================================
        # 1️⃣ DETECT INTENT (ONLY ONCE!)
        # ============================================================
        intent = detect_intent(message)
        emotion = detect_emotion(message)
        empathy_prefix = get_empathy_phrase(emotion)

        # ============================================================
        # 2️⃣ HANDLE CANCEL (GLOBAL - ALWAYS ALLOWED)
        # ============================================================
        if intent == "CANCEL":
            return handle_cancel_request(user_id, session)

        # ============================================================
        # 3️⃣ PROTECT ACTIVE FLOWS - CONTINUE IF IN FLOW
        # ============================================================
        # ✅ CRITICAL FIX: If user is in a flow, continue that flow
        # Don't let new intent detection interrupt active flows
        if session.current_flow:
            explicit_override_intents = [
                "HELP", "MOTIVATION", "ARTICLES", "READ_MORE_ARTICLE"]

            if intent in explicit_override_intents:
                session.reset()  # user explicitly wants a different action
            else:
                # Route the flow to the correct continuation
                if session.current_flow == "WORKOUT":
                    return continue_workout_flow(message, user_id, session)
                elif session.current_flow == "CALORIES":
                    return continue_calories_flow(message, user_id, session)
                # Add more flows here as needed
                else:
                    # fallback for other flows
                    return continue_flow(message, user_id, session)

        # ============================================================
        # 4️⃣ AUTO-DETECTION (ONLY IF NOT IN FLOW)
        # ============================================================
        if not session.current_flow:
            # Only auto-detect if no active flow
            if intent not in ["BMI", "CALORIES", "WORKOUT", "CANCEL", "MOTIVATION",
                              "HELP", "ARTICLES", "READ_MORE_ARTICLE"]:

                # Check for BMI data
                data = extract_height_weight(message)
                if data["height"] or data["weight"]:
                    intent = "BMI"

                # Check for activity level (calories flow)
                elif extract_activity_level(message):
                    intent = "CALORIES"

                # Enhanced workout detection: ONLY trigger if message explicitly mentions workout
                else:
                    workout_keywords = [
                        "workout", "exercise", "training",
                        "fitness plan", "exercise plan", "routine", "workout plan"
                    ]
                    if any(kw in message.lower() for kw in workout_keywords):
                        intent = "WORKOUT"

        # ============================================================
        # 5️⃣ HANDLE SPECIAL INTENTS (NO FLOW)
        # ============================================================
        if intent == "READ_MORE_ARTICLE":
            return get_full_article(user_id)

        if intent == "MOTIVATION":
            session.reset()
            return get_random_quote()

        if intent == "ARTICLES":
            session.reset()
            return handle_articles_request(message, user_id)

        if intent == "HELP":
            session.reset()
            return get_help_message()

        if intent == "EMOTION_SUPPORT":
            return start_emotion_support_flow(user_id, session, emotion)

        # ============================================================
        # 6️⃣ START NEW FLOWS
        # ============================================================
        if intent == "BMI":
            return empathy_prefix + start_bmi_flow(message, user_id, session)

        if intent == "CALORIES":
            return empathy_prefix + start_calories_flow(message, user_id, session)

        if intent == "WORKOUT":
            return empathy_prefix + start_workout_flow(message, user_id, session)

        # ============================================================
        # 7️⃣ FALLBACK - UNKNOWN INTENT
        # ============================================================
        return handle_unknown_message(message)

    except Exception as e:
        logger.error(f"⚠️ Error in process_message: {str(e)}")
        return "❌ Something went wrong. Please type 'cancel' to start over."


def continue_flow(message: str, user_id: int, session) -> str:
    """
    Continue an ongoing conversation flow

    ✅ FIXED: Simplified - just continues the active flow
    ✅ FIXED: No intent checking here (already done in process_message)
    """
    try:
        # ✅ CRITICAL: Route to the correct flow continuation
        if session.current_flow == "BMI":
            return continue_bmi_flow(message, user_id, session)

        elif session.current_flow == "CALORIES":
            return continue_calories_flow(message, user_id, session)

        elif session.current_flow == "WORKOUT":
            return continue_workout_flow(message, user_id, session)

        # Should not reach here if session.current_flow is set correctly
        logger.warning(f"⚠️ Unknown flow: {session.current_flow}")
        return "Something went wrong. Let's start over!"

    except Exception as e:
        logger.error(f"⚠️ Error in continue_flow: {str(e)}")
        return "❌ Something went wrong. Please type 'cancel' to start over."


# ==================== BMI FLOW ====================


def start_bmi_flow(message: str, user_id: int, session) -> str:
    """
    Start BMI calculation flow with runtime session support
    """
    try:
        # Get runtime session for partial data storage
        runtime_session = get_runtime_session(user_id)
        partial_data = runtime_session["partial_bmi_data"]

        # Robust parsing in any order
        data = extract_height_weight(message)

        # ✅ FIXED: Use merge_partial_data helper
        data = merge_partial_data(user_id, "partial_bmi_data", data)

        # If both provided, calculate immediately
        if data.get("height") and data.get("weight"):
            try:
                bmi, status = calculate_bmi(data["weight"], data["height"])
                session.reset()
                runtime_session["partial_bmi_data"] = {}
                sync_runtime_to_db(user_id)
                return format_bmi_result(bmi, status, data["height"], data["weight"])
            except ValueError as e:
                session.reset()
                runtime_session["partial_bmi_data"] = {}
                return f"[b]Error:[/b] {str(e)}\n\nPlease provide valid height (50-300cm) and weight (20-300kg)."

        # If only one provided, ask for the other
        if data.get("height") and not data.get("weight"):
            session.update(flow="BMI", step=1, data={"height": data["height"]})
            return f"[b]Got your height:[/b] {data['height']} cm\n\nNow, what's your weight in kg?"

        if data.get("weight") and not data.get("height"):
            session.update(flow="BMI", step=1, data={"weight": data["weight"]})
            return f"[b]Got your weight:[/b] {data['weight']} kg\n\nNow, what's your height in cm?"

        # Ask for both
        session.update(flow="BMI", step=0)
        return ("Let's calculate your BMI!\n\n"
                "Please tell me your height and weight.\n\n"
                "[b]Examples:[/b]\n"
                "- '170 cm and 65 kg'\n"
                "- '5 feet 9 inches and 150 pounds'\n"
                "- 'Height: 180cm, Weight: 75kg'")

    except Exception as e:
        logger.error(f"⚠️ Error in start_bmi_flow: {str(e)}")
        return "[b]Error:[/b] Something went wrong. Please try again."


def continue_bmi_flow(message: str, user_id: int, session) -> str:
    """
    ✅ FIXED: Continue BMI flow with proper numeric validation
    """
    try:
        # ✅ FIXED: Check for empty or nonsense input (expecting numeric)
        if is_empty_or_nonsense(message, expect_numeric=True):
            return handle_wrong_input(
                user_id, session, "bmi",
                "I didn't receive a valid response. Please provide your height and weight."
            )

        # Get runtime session
        runtime_session = get_runtime_session(user_id)
        partial_data = runtime_session["partial_bmi_data"]

        # Extract new data from message
        data = extract_height_weight(message)

        # Ensure collected_data exists
        if not hasattr(session, 'collected_data') or session.collected_data is None:
            session.collected_data = {}

        collected = session.collected_data

        # Merge runtime partial data with session data
        if "height" in partial_data:
            collected["height"] = partial_data["height"]
        if "weight" in partial_data:
            collected["weight"] = partial_data["weight"]

        # Check if we got height from current message
        if "height" not in collected and data["height"]:
            collected["height"] = data["height"]
            partial_data["height"] = data["height"]
            session.reset_wrong_input("bmi")  # ✅ Reset counter

        # Check if we got weight from current message
        if "weight" not in collected and data["weight"]:
            collected["weight"] = data["weight"]
            partial_data["weight"] = data["weight"]
            session.reset_wrong_input("bmi")  # ✅ Reset counter

        # If we have both, calculate
        if "height" in collected and "weight" in collected:
            try:
                bmi, status = calculate_bmi(
                    collected["weight"], collected["height"])
                session.reset()
                runtime_session["partial_bmi_data"] = {}
                sync_runtime_to_db(user_id)
                return format_bmi_result(bmi, status, collected["height"], collected["weight"])
            except ValueError as e:
                session.reset()
                runtime_session["partial_bmi_data"] = {}
                return f"[b]Error:[/b] {str(e)}\n\nPlease provide valid height (50-300cm) and weight (20-300kg)."

        # Still missing data
        if "height" in collected and "weight" not in collected:
            if not data["weight"]:
                return handle_wrong_input(
                    user_id, session, "bmi",
                    f"I couldn't find a valid weight in your message.\n\n"
                    f"[b]Height:[/b] {collected['height']} cm\n\n"
                    f"Please provide your weight:\n"
                    "- '65 kg'\n"
                    "- '150 pounds'\n"
                    "- 'I weigh 70 kilograms'"
                )
            return (f"[b]Height:[/b] {collected['height']} cm\n\n"
                    f"Now I need your weight. You can say:\n"
                    "- '65 kg'\n"
                    "- '150 pounds'\n"
                    "- 'I weigh 70 kilograms'")

        if "weight" in collected and "height" not in collected:
            if not data["height"]:
                return handle_wrong_input(
                    user_id, session, "bmi",
                    f"I couldn't find a valid height in your message.\n\n"
                    f"[b]Weight:[/b] {collected['weight']} kg\n\n"
                    f"Please provide your height:\n"
                    "- '170 cm'\n"
                    "- '5 feet 9 inches'\n"
                    "- 'I am 180 centimeters tall'"
                )

            return (f"[b]Weight:[/b] {collected['weight']} kg\n\n"
                    f"Now I need your height. You can say:\n"
                    "- '170 cm'\n"
                    "- '5 feet 9 inches'\n"
                    "- 'I am 180 centimeters tall'")

        # Couldn't extract anything
        return handle_wrong_input(
            user_id, session, "bmi",
            "I couldn't understand that. Please provide your height and weight.\n\n"
            "[b]Examples:[/b]\n"
            "- '170 cm and 65 kg'\n"
            "- '5 feet 9 inches, 150 pounds'\n"
            "- 'Height: 180cm, Weight: 75kg'"
        )

    except Exception as e:
        logger.error(f"⚠️ Error in continue_bmi_flow: {str(e)}")
        return "[b]Error:[/b] Something went wrong. Please type 'cancel' to start over."


def format_bmi_result(bmi: float, status: str, height: float, weight: float) -> str:
    """Format BMI calculation result"""
    response = "[b]Your BMI Results[/b]\n\n"
    response += f"- Height: {height} cm\n"
    response += f"- Weight: {weight} kg\n"
    response += f"- [b]BMI:[/b] {bmi}\n"
    response += f"- Status: [b]{status}[/b]\n\n"

    # Add advice based on status
    if status == "Underweight":
        response += "[b]Advice:[/b] Focus on nutrient-dense foods and strength training to build healthy weight."
    elif status == "Normal weight":
        response += "[b]Great job![/b] Keep maintaining your healthy lifestyle with balanced nutrition and regular exercise."
    elif status == "Overweight":
        response += "[b]Advice:[/b] Consider a balanced diet with a slight calorie deficit and regular cardio exercise."
    else:  # Obese
        response += "[b]Advice:[/b] Consult a healthcare professional for a personalized weight loss plan. Focus on gradual, sustainable changes."

    return response


# ==================== CALORIES FLOW ====================

def start_calories_flow(message: str, user_id: int, session) -> str:
    """
    ✅ FIXED: Better intent detection for retrieval vs calculation
    """
    try:
        message_lower = message.lower().strip()

        # ============================================================
        # IMPROVED INTENT DETECTION
        # ============================================================

        # Retrieval keywords - user wants THEIR saved goal
        retrieval_keywords = [
            "my saved calorie",
            "my saved calories",
            "my calorie goal",
            "my daily calorie goal",
            "show my calorie goal",
            "show my saved calories",
            "view my calorie goal",
            "get my saved calorie"
        ]

        # Calculation keywords - user wants to CALCULATE new estimate
        calculation_keywords = [
            "calculate for", "estimate for", "what if i",
            "how many calories should i", "help me calculate",
            "i want to calculate", "can you calculate"
        ]

        # Check for retrieval intent
        is_retrieval = any(kw in message_lower.replace("?", "")
                           for kw in retrieval_keywords)

        is_calculation = (
            any(kw in message_lower for kw in calculation_keywords)
            or not is_retrieval
        )

        # Special case: standalone words like "calories" or "calorie goal" = retrieval
        standalone_retrieval = message_lower in [
            "calorie goal", "my goal",
            "goal", "daily goal", "my calorie goal"
        ]

        if standalone_retrieval:
            is_retrieval = True
            is_calculation = False

        # ============================================================
        # CASE 1: DB RETRIEVAL (User wants THEIR saved goal)
        # ============================================================
        if is_retrieval:
            logger.info(f"🔍 Retrieval mode triggered for user_id={user_id}")
            if not USE_DATABASE:
                return (
                    "[b]Error:[/b] I can't access your profile right now.\n\n"
                    "Would you like me to calculate a new estimate? "
                    "I'll need some information from you."
                )

            try:
                user_data = auth_tbl.get_user_calorie_profile(user_id)
                # ✅ ADD THIS
                logger.info(f"📊 User data retrieved: {user_data}")

                if not user_data:
                    # ✅ ADD THIS
                    logger.warning(
                        f"⚠️ No profile found for user_id={user_id}")
                    return (
                        "[b]Notice:[/b] I couldn't find your calorie profile in the system.\n\n"
                        "Would you like me to [b]calculate[/b] your daily calorie needs? "
                        "I'll ask you a few questions."
                    )

                db_daily_net_goal = user_data.get("daily_goal")
                # ✅ ADD THIS
                logger.info(f"🎯 Daily goal from DB: {db_daily_net_goal}")

                # ✅ CRITICAL FIX: Check if goal exists AND is valid
                if db_daily_net_goal and db_daily_net_goal > 0:
                    session.reset()
                    return format_calorie_result_from_db(db_daily_net_goal, user_data)
                else:
                    # Profile exists but no goal saved
                    return (
                        "[b]Notice:[/b] You don't have a saved calorie goal yet.\n\n"
                        "Would you like me to [b]calculate[/b] your daily calorie needs based on your profile? "
                        "I'll ask you a few questions to get an accurate estimate."
                    )

            except Exception as e:
                logger.error(f"⚠️ Database error: {str(e)}")
                return (
                    "[b]Error:[/b] I couldn't retrieve your calorie goal right now.\n\n"
                    "Would you like me to calculate a new estimate?"
                )

        # ============================================================
        # CASE 2: CALCULATION (User wants to CALCULATE)
        # ============================================================
        runtime_session = get_runtime_session(user_id)

        # Initialize collected_data structure
        collected_data = {
            "age": None,
            "gender": None,
            "height": None,
            "weight": None,
            "activity_level": None,
            "goal": None
        }

        # Initialize session
        session.update(flow="CALORIES", step=0, data=collected_data.copy())
        runtime_session["partial_calorie_data"] = collected_data.copy()

        return (
            "[b]Let's calculate your daily calorie needs![/b]\n\n"
            "I'll need some information to give you an accurate estimate.\n\n"
            "[b]Required information:[/b]\n"
            "- Age\n"
            "- Sex (male/female)\n"
            "- Height (in cm)\n"
            "- Weight (in kg)\n"
            "- Activity level\n"
            "- Fitness goal\n\n"
            "*Note: This calculation is temporary and won't be saved to your profile.*\n\n"
            "Let's start! [b]How old are you?[/b]"
        )

    except Exception as e:
        logger.error(f"⚠️ Error in start_calories_flow: {str(e)}")
        return "[b]Error:[/b] Something went wrong. Please try again."


def continue_calories_flow(message: str, user_id: int, session) -> str:
    """
    Continue calorie flow with sequential mandatory field collection
    """
    try:
        logger.info(f"Step: {session.flow_step}, Message: {message}")
        logger.info(f"Collected data: {session.collected_data}")
        # Check for empty or nonsense input
        if is_empty_or_nonsense(message, expect_numeric=False):
            return handle_wrong_input(
                user_id, session, "calories",
                "I didn't receive a valid response. Please provide the requested information."
            )

        runtime_session = get_runtime_session(user_id)

        if not hasattr(session, 'collected_data') or session.collected_data is None:
            session.collected_data = {
                "age": None,
                "gender": None,
                "height": None,
                "weight": None,
                "activity_level": None,
                "goal": None
            }

        collected = session.collected_data

        # Step 0: Collect Age
        if collected.get("age") is None:
            age = extract_age(message)
            if age and validate_age(age):
                collected["age"] = age
                runtime_session["partial_calorie_data"]["age"] = age
                session.reset_wrong_input("calories")
                session.update(flow="CALORIES", step=1, data=collected.copy())
                return (
                    f"Got it! You're [b] {age} years old[/b].\n\n"
                    "What's your [b]biological sex[/b]?\n"
                    "- Male\n"
                    "- Female"
                )
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "Please enter a valid age (between 10 and 100 years old)."
                )

        # Step 1: Collect Sex
        if collected.get("gender") is None:
            gender = extract_gender(message)
            if gender:
                collected["gender"] = gender
                runtime_session["partial_calorie_data"]["gender"] = gender
                session.reset_wrong_input("calories")
                session.update(flow="CALORIES", step=2, data=collected.copy())
                return f"Recorded: [b]{gender.title()}[/b]\n\nWhat's your [b]height in centimeters (cm)[/b]?\n(Example: 170)"
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "Please specify your biological sex:\n"
                    "• Male\n"
                    "• Female"
                )

        # Step 2: Collect Height
        if collected.get("height") is None:
            height = extract_height(message)
            if height and validate_height(height):
                collected["height"] = height
                runtime_session["partial_calorie_data"]["height"] = height
                session.reset_wrong_input("calories")
                session.update(flow="CALORIES", step=3, data=collected.copy())
                return f"Height recorded: [b]{height} cm[/b]\n\nWhat's your [b]weight in kilograms (kg)[/b]?\n(Example: 70)"
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "Please enter a valid height in centimeters (between 100 and 250 cm)."
                )

        # Step 3: Collect Weight
        if collected.get("weight") is None:
            weight = extract_weight(message)
            if weight and validate_weight(weight):
                collected["weight"] = weight
                runtime_session["partial_calorie_data"]["weight"] = weight
                session.reset_wrong_input("calories")
                session.update(flow="CALORIES", step=4, data=collected.copy())
                return (
                    f"Weight recorded: [b]{weight} kg[/b]\n\n"
                    "What's your [b]activity level[/b]?\n\n"
                    "- Not very active (sedentary, desk job)\n"
                    "- Lightly active (light exercise 1-3 days/week)\n"
                    "- Active (moderate exercise 3-5 days/week)\n"
                    "- Very active (intense exercise 6-7 days/week)"
                )
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "Please enter a valid weight in kilograms (between 30 and 300 kg)."
                )

        # Step 4: Collect Activity Level
        if collected.get("activity_level") is None:
            activity = extract_activity_level(message)
            if activity:
                collected["activity_level"] = activity
                runtime_session["partial_calorie_data"]["activity_level"] = activity
                session.reset_wrong_input("calories")
                session.update(flow="CALORIES", step=5, data=collected.copy())
                return (
                    f"Activity level: [b]{activity.replace('_', ' ').title()}[/b]\n\n"
                    "Finally, what's your [b]fitness goal[/b]?\n\n"
                    "- Lose weight (calorie deficit)\n"
                    "- Gain muscle (calorie surplus)\n"
                    "- Maintain weight (balanced calories)"
                )
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "I didn't recognize that activity level. Please choose:\n\n"
                    "• Not very active\n"
                    "• Lightly active\n"
                    "• Active\n"
                    "• Very active"
                )

        # Step 5: Collect Goal and Calculate
        if collected.get("goal") is None:
            logger.info(f"Attempting to extract goal from: {message}")
            goal = extract_goal_from_text(message)
            logger.info(f"Extracted goal: {goal}")
            if goal:
                collected["goal"] = goal
                runtime_session["partial_calorie_data"]["goal"] = goal
                session.reset_wrong_input("calories")

                # All data collected - calculate calories
                calories = calculate_calories_from_collected_data(collected)

                session.reset()
                runtime_session["partial_calorie_data"] = {}

                return format_complete_calorie_result(calories, collected)
            else:
                return handle_wrong_input(
                    user_id, session, "calories",
                    "I didn't recognize that goal. Please choose:\n\n"
                    "• Lose weight\n"
                    "• Gain muscle\n"
                    "• Maintain weight"
                )

        return "Something went wrong. Let's start over!"

    except Exception as e:
        logger.error(f"⚠️ Error in continue_calories_flow: {str(e)}")
        return "Something went wrong. Please type 'cancel' to start over."


# ===== VALIDATION FUNCTIONS =====

def extract_age(message: str) -> int:
    """Extract age from message"""
    import re
    numbers = re.findall(r'\d+', message)
    if numbers:
        return int(numbers[0])
    return None


def validate_age(age: int) -> bool:
    """Validate age is within reasonable range"""
    return 10 <= age <= 100


def extract_gender(text: str) -> str | None:
    text = text.lower().strip()

    if "female" in text:
        return "female"
    if "male" in text:
        return "male"
    return None


def extract_height(message: str) -> float:
    """Extract height from message"""
    import re
    numbers = re.findall(r'\d+\.?\d*', message)
    if numbers:
        return float(numbers[0])
    return None


def validate_height(height: float) -> bool:
    """Validate height is within reasonable range (cm)"""
    return 100 <= height <= 250


def extract_weight(message: str) -> float:
    """Extract weight from message"""
    import re
    numbers = re.findall(r'\d+\.?\d*', message)
    if numbers:
        return float(numbers[0])
    return None


def validate_weight(weight: float) -> bool:
    """Validate weight is within reasonable range (kg)"""
    return 30 <= weight <= 300


# ===== CALORIE CALCULATION =====

def calculate_calories_from_collected_data(data: dict) -> int:
    """
    Calculate daily calorie needs using Mifflin-St Jeor Equation
    BMR calculation, then multiply by activity factor and adjust for goal
    """
    age = data["age"]
    gender = data["gender"].lower().strip()
    height = data["height"]
    weight = data["weight"]
    activity_level = (data.get("activity_level") or "").lower().strip()
    goal = (data.get("goal") or "").lower().strip()
    goal = goal.replace("_", " ")

    # Calculate BMR using Mifflin-St Jeor Equation
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:  # female
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # ---------------------------
    # ✅ ACTIVITY NORMALIZATION
    # ---------------------------
    activity_map = {
        "sedentary": "not very active",
        "not active": "not very active",
        "light": "lightly active",
        "lightly active": "lightly active",
        "moderate": "active",
        "active": "active",
        "high": "very active",
        "very active": "very active"
    }

    activity_level = activity_level.replace("_", " ")
    activity_level = activity_map.get(activity_level, "not very active")

    activity_multipliers = {
        "not very active": 1.2,
        "lightly active": 1.375,
        "active": 1.55,
        "very active": 1.725
    }

    tdee = bmr * activity_multipliers[activity_level]

    # Adjust for goal
    if goal == "lose_weight":
        calories = tdee - 500  # 500 calorie deficit
    elif goal in ["gain_weight", "gain_muscles", "gain muscle"]:
        calories = tdee + 500  # 500 calorie surplus
    else:  # keep_fit / maintain
        calories = tdee

    return int(calories)


# ===== FORMATTING FUNCTIONS =====

def format_complete_calorie_result(calories: int, data: dict) -> str:
    """Format the complete calorie calculation result"""
    response = "🎉 [b]Your Personalized Daily Calorie Target[/b]\n\n"
    response += f"🔥 [b]{calories} kcal/day[/b]\n\n"

    response += "[b]Based on your profile:[/b]\n"
    response += f"• Age: {data['age']} years\n"
    response += f"• Sex: {data['gender'].title()}\n"
    response += f"• Height: {data['height']} cm\n"
    response += f"• Weight: {data['weight']} kg\n"
    response += f"• Activity: {data['activity_level'].replace('_', ' ').title()}\n"
    response += f"• Goal: {data['goal'].replace('_', ' ').title()}\n\n"

    response += "[b]Recommended Meal Distribution:[/b]\n"
    response += f"• Breakfast: ~{int(calories * 0.30)} kcal (30%)\n"
    response += f"• Lunch: ~{int(calories * 0.35)} kcal (35%)\n"
    response += f"• Dinner: ~{int(calories * 0.25)} kcal (25%)\n"
    response += f"• Snacks: ~{int(calories * 0.10)} kcal (10%)\n\n"

    # Goal-specific tips
    if data['goal'] == "lose_weight":
        response += "[b]Weight Loss Tips:[/b]\n"
        response += "• This includes a 500 kcal deficit for healthy weight loss\n"
        response += "• Aim to lose 0.5-1 kg per week\n"
        response += "• Focus on protein and fiber-rich foods\n"
        response += "• Stay hydrated and get enough sleep\n\n"
    elif data['goal'] in ["gain_weight", "gain_muscles"]:
        response += "[b]Muscle Gain Tips:[/b]\n"
        response += "• This includes a 500 kcal surplus for muscle growth\n"
        response += "• Combine with strength training 3-5x per week\n"
        response += "• Eat protein-rich foods (1.6-2.2g per kg body weight)\n"
        response += "• Be patient - aim for 0.25-0.5 kg gain per week\n\n"
    else:
        response += "[b]Maintenance Tips:[/b]\n"
        response += "• This maintains your current weight\n"
        response += "• Focus on balanced, nutritious meals\n"
        response += "• Stay active and consistent\n"
        response += "• Monitor your weight weekly\n\n"

    response += "[b]Important Notes:[/b]\n"
    response += "• This is an estimate - adjust based on your progress\n"
    response += "• Track your meals in the Calorie Counter\n"
    response += "• Consult a healthcare provider for personalized advice\n"
    response += "• Reassess every 4-6 weeks as your body changes"

    return response


def format_calorie_result_from_db(db_daily_net_goal: int, user_data: dict) -> str:
    """Format DB-stored calorie goal"""
    response = "[b]Your Daily Calorie Goal[/b]\n\n"
    response += f"• [b]Target: {db_daily_net_goal} kcal/day[/b]\n"

    goal = user_data.get('goal', 'N/A')
    activity = user_data.get('activity_level', 'N/A')

    if goal != 'N/A':
        response += f"• Goal: {goal.replace('_', ' ').title()}\n"
    if activity != 'N/A':
        response += f"• Activity: {activity.replace('_', ' ').title()}\n"

    response += "\n[b]Meal Distribution:[/b]\n"
    response += f"• Breakfast: ~{int(db_daily_net_goal * 0.30)} kcal (30%)\n"
    response += f"• Lunch: ~{int(db_daily_net_goal * 0.35)} kcal (35%)\n"
    response += f"• Dinner: ~{int(db_daily_net_goal * 0.25)} kcal (25%)\n"
    response += f"• Snacks: ~{int(db_daily_net_goal * 0.10)} kcal (10%)\n\n"
    response += "Track your meals in the Calorie Counter to stay on track!"

    return response


# ==================== WORKOUT FLOW ====================

def start_workout_flow(message: str, user_id: int, session) -> str:
    """
    ✅ FIXED: Start workout flow properly - ask for goal if not provided
    """
    try:
        runtime_session = get_runtime_session(user_id)

        if "partial_workout_data" not in runtime_session:
            runtime_session["partial_workout_data"] = {}
        partial_data = runtime_session["partial_workout_data"]

        if not hasattr(session, "collected_data") or session.collected_data is None:
            session.collected_data = {}
        collected = session.collected_data

        message_lower = message.lower().strip()

        # ---------------- EXTRACT DATA ----------------
        goal = extract_goal_from_text(message_lower)
        level = extract_level_from_text(message_lower)
        condition = extract_condition_from_text(message_lower)

        # Normalize goal if found
        if goal:
            goal = normalize_goal(goal)

        # Merge with partial_data & session
        if goal:
            partial_data["goal"] = goal
            collected["goal"] = goal
        elif "goal" in partial_data:
            goal = partial_data["goal"]

        if level:
            partial_data["level"] = level
            collected["level"] = level
        elif "level" in partial_data:
            level = partial_data["level"]

        if condition in ["normal", "health_condition"]:
            partial_data["condition"] = condition
            collected["condition"] = condition
        elif "condition" in partial_data:
            condition = partial_data["condition"]

        # ---------------- AUTO PLAN GENERATION (if all data present) ----------------
        if goal and level and condition:
            has_condition = (condition == "health_condition")

            # Acknowledgment message
            if has_condition:
                ack_msg = (
                    "Thanks for letting me know about your health condition. "
                    "Before we get into your workout plan, here's some important guidance:\n\n"
                    "[b]Safe Exercise Guidelines:[/b]\n"
                    "1. Walking (10–30 min/day)\n"
                    "2. Swimming & Water Aerobics\n"
                    "3. Bodyweight Strength Exercises (2–3x/week)\n"
                    "4. Balance & Flexibility Work\n"
                    "5. Adaptive Yoga / Chair Yoga\n\n"
                    "Always consult your healthcare provider before starting.\n\n"
                )

                # Reset session and partial data
                session.reset()
                runtime_session["partial_workout_data"] = {}
                sync_runtime_to_db(user_id)

                return ack_msg

            exercises = get_workout_plan(user_id, level, condition)

            session.reset()
            runtime_session["partial_workout_data"] = {}
            sync_runtime_to_db(user_id)

            return format_workout_plan(exercises, has_condition=has_condition)

        # ---------------- START FLOW: Ask for missing data ----------------
        # ✅ CRITICAL: Only set current_flow AFTER we know we need to collect data
        session.current_flow = "WORKOUT"

        # If goal was extracted from initial message, skip to level
        if goal:
            collected["goal"] = goal
            partial_data["goal"] = goal
            session.update(flow="WORKOUT", data=collected.copy())
            return (
                f"Got it! Your fitness goal is [b]{goal.replace('_', ' ').title()}[/b].\n\n"
                "What's your current fitness level?\n\n"
                "- [b]Beginner[/b] - New to exercise or returning after a break\n"
                "- [b]Intermediate[/b] - Exercise regularly, comfortable with most movements\n"
                "- [b]Advanced[/b] - Very experienced, can handle intense workouts"
            )

        # If level was extracted (rare), skip to condition
        if level:
            collected["level"] = level
            partial_data["level"] = level
            session.update(flow="WORKOUT", data=collected.copy())
            return (
                f"Got it! You're at the [b]{level.title()}[/b] level.\n\n"
                "[b]Important question:[/b] Do you have any health conditions?\n\n"
                "- [b]Yes[/b] - I have a health condition\n"
                "- [b]No[/b] - I don't have any health conditions\n\n"
                "(Examples: joint issues, heart condition, injury, etc.)"
            )

        # Default: Ask for goal
        session.update(flow="WORKOUT", data=collected.copy())
        return (
            "Let's create your personalized workout plan!\n\n"
            "First, what's your fitness goal?\n\n"
            "- [b]Lose Weight[/b] - Cardio-focused with calorie burn\n"
            "- [b]Gain Weight[/b] - Strength training with nutrition focus\n"
            "- [b]Gain Muscles[/b] - Hypertrophy and resistance training\n"
            "- [b]Keep Fit[/b] - Balanced mix of cardio and strength"
        )

    except Exception as e:
        logger.error(f"⚠️ Error in start_workout_flow: {str(e)}")
        return " Something went wrong. Please try again."


def continue_workout_flow(message: str, user_id: int, session) -> str:
    """
    ✅ FIXED: Proper step-by-step flow with early returns
    """
    try:
        runtime_session = get_runtime_session(user_id)
        if "partial_workout_data" not in runtime_session:
            runtime_session["partial_workout_data"] = {}
        partial_data = runtime_session["partial_workout_data"]

        if not hasattr(session, "collected_data") or session.collected_data is None:
            session.collected_data = {}
        collected = session.collected_data

        message_lower = message.lower().strip()

        # Merge partial data into session
        for key in ["goal", "level", "condition"]:
            if key in partial_data:
                collected[key] = partial_data[key]

        # ---------------- STEP 0 — GOAL ----------------
        if not collected.get("goal"):
            goal = extract_goal_from_text(message_lower)
            if goal:
                goal = normalize_goal(goal)
                collected["goal"] = goal
                partial_data["goal"] = goal
                # ✅ ADDED
                session.update(flow="WORKOUT", step=1, data=collected.copy())
                session.reset_wrong_input("workout")
                return (
                    f"Got it! Your fitness goal is [b]{goal.replace('_', ' ').title()}[/b].\n\n"
                    "What's your current fitness level?\n\n"
                    "- [b]Beginner[/b] - New to exercise or returning after a break\n"
                    "- [b]Intermediate[/b] - Exercise regularly, comfortable with most movements\n"
                    "- [b]Advanced[/b] - Very experienced, can handle intense workouts"
                )
            else:
                return handle_wrong_input(
                    user_id, session, "workout",
                    "I didn't recognize that goal. What's your fitness goal?\n\n"
                    "- [b]Lose Weight[/b]\n"
                    "- [b]Gain Weight[/b]\n"
                    "- [b]Gain Muscles[/b]\n"
                    "- [b]Keep Fit[/b]"
                )

        # ---------------- STEP 1 — LEVEL ----------------
        if not collected.get("level"):
            level = extract_level_from_text(message_lower)
            if level:
                collected["level"] = level
                partial_data["level"] = level
                session.update(flow="WORKOUT", step=2, data=collected.copy())
                session.reset_wrong_input("workout")
                return (
                    f"Got it! You're at the [b]{level.title()}[/b] level.\n\n"
                    "[b]Important question:[/b] Do you have any health conditions?\n\n"
                    "- [b]Yes[/b] - I have a health condition\n"
                    "- [b]No[/b] - I don't have any health conditions\n\n"
                    "(Examples: joint issues, heart condition, injury, etc.)"
                )
            else:
                return handle_wrong_input(
                    user_id, session, "workout",
                    "I didn't recognize that fitness level. What's your current level?\n\n"
                    "- [b]Beginner[/b] - New to exercise or returning after a break\n"
                    "- [b]Intermediate[/b] - Exercise regularly, comfortable with most movements\n"
                    "- [b]Advanced[/b] - Very experienced, can handle intense workouts"
                )

        # ---------------- STEP 2 — CONDITION ----------------
        if not collected.get("condition"):
            condition = extract_condition_from_text(message_lower)

            if condition in ["normal", "health_condition"]:
                collected["condition"] = condition
                partial_data["condition"] = condition
                session.collected_data["condition"] = condition
                session.reset_wrong_input("workout")

                has_condition = (condition == "health_condition")

                # Acknowledgment message
                if has_condition:
                    ack_msg = (
                        "Thank you for sharing this information.\n\n"
                        "Before continuing, please review the following important guidance.\n\n"
                        "[b]Safe Exercise Guidelines for Individuals with Health Conditions:[/b]\n\n"
                        "The following activities are commonly recommended by reputable health organizations "
                        "such as the World Health Organization (WHO), American Heart Association (AHA), "
                        "and physical therapy associations for general movement and conditioning:\n\n"
                        "1. [b]Walking[/b]\n"
                        "Low-impact cardiovascular activity (10–30 minutes per day).\n\n"
                        "2. [b]Swimming & Water-Based Exercises[/b]\n"
                        "Joint-friendly exercises that reduce strain while improving endurance.\n\n"
                        "3. [b]Light Bodyweight or Resistance Exercises[/b]\n"
                        "Performed 2–3 times per week to maintain muscle strength.\n\n"
                        "4. [b]Balance and Flexibility Training[/b]\n"
                        "Helps reduce injury risk and improve mobility.\n\n"
                        "5. [b]Adaptive or Chair-Based Yoga[/b]\n"
                        "Focuses on gentle stretching, breathing, and controlled movement.\n\n"
                        "[b]Important Disclaimer:[/b]\n"
                        "These recommendations are for general guidance only and do not replace medical advice.\n\n"
                        "[b]Consultation with a qualified healthcare professional is REQUIRED[/b] "
                        "before starting or continuing any exercise program, especially if you have a medical condition, "
                        "are recovering from injury, or are experiencing symptoms."
                    )

                    session.reset()
                    runtime_session["partial_workout_data"] = {}
                    sync_runtime_to_db(user_id)

                    return ack_msg

                # Generate workout plan
                exercises = get_workout_plan(
                    user_id,
                    collected["goal"],
                    collected["level"],
                    collected["condition"]
                )

                response = format_workout_plan(
                    exercises, has_condition=has_condition)

                # Reset session and partial data
                session.reset()
                runtime_session["partial_workout_data"] = {}
                sync_runtime_to_db(user_id)

                return response
            else:
                return handle_wrong_input(
                    user_id, session, "workout",
                    "Please answer with 'Yes' or 'No' regarding health conditions.\n\n"
                    "- [b]Yes[/b] - I have a health condition\n"
                    "- [b]No[/b] - I don't have any health conditions"
                )

        # ---------------- FALLBACK ----------------
        return "Something went wrong. Let's start over! Type 'workout' to try again."

    except Exception as e:
        logger.error(f"⚠️ Error in continue_workout_flow: {str(e)}")
        return "Something went wrong. Please type 'cancel' to start over."

    # ==================== OTHER HANDLERS ====================


def handle_goal_question(message: str, user_id: int) -> str:
    """Handle fitness goal questions"""
    articles = search_articles("goal fitness")

    if articles:
        article = articles[0]
        return format_article(article, user_id=user_id, full=False)

    return (
        "[b]Setting Fitness Goals[/b]\n\n"
        "1. [b]Lose Weight:[/b] Create a calorie deficit through diet and cardio\n"
        "2. [b]Gain Muscle:[/b] Increase protein intake and do strength training\n"
        "3. [b]Maintain:[/b] Balance calories in vs out with regular exercise\n"
        "4. [b]Improve Health:[/b] Focus on whole foods and consistent activity\n\n"
        "What specific goal would you like help with?"
    )


def handle_articles_request(message: str, user_id: int) -> str:
    """Handle article requests"""
    articles = search_articles(message)

    if articles:
        article = articles[0]
        last_article_cache[user_id] = article
        return format_article(article, user_id, full=False)

    article = get_random_article()
    if article:
        last_article_cache[user_id] = article
        return format_article(article, user_id, full=False)

    return "No articles available at the moment. Check back later!"


def handle_progress_request(user_id: int) -> str:
    """Handle progress tracking request"""
    return (
        "[b]Your Progress Tracking[/b]\n\n"
        "To view your progress:\n"
        "- Check the Calorie Counter tab for daily intake\n"
        "- Track your workouts in the Workout section\n"
        "- Monitor your weight changes\n\n"
        "Tip: Consistency is key! Keep logging your meals and workouts."
    )


def get_help_message() -> str:
    """Return help message"""
    return (
        "[b]Hi! I'm your AI Fitness Buddy![/b]\n\n"
        "I’m here to support your fitness journey by providing guidance, calculations, "
        "and recommendations based on general health and fitness principles.\n\n"
        "[b]What I can help you with:[/b]\n\n"
        "[b]• BMI Calculator[/b]\n"
        "  Calculate your Body Mass Index using your height and weight.\n\n"
        "[b]• Calorie Goals[/b]\n"
        "  Estimate your daily calorie needs based on age, height, weight, activity level, and goals.\n\n"
        "[b]• Workout Plans[/b]\n"
        "  Get workout recommendations tailored to your fitness level and goals.\n\n"
        "[b]• Motivation[/b]\n"
        "  Receive motivational messages to help you stay consistent.\n\n"
        "[b]• Articles & Tips[/b]\n"
        "  Read general fitness, wellness, and lifestyle advice.\n\n"
        "[b]Important to know:[/b]\n"
        "• To ensure accurate assistance, type carefully and avoid mistakes or typos.\n"
        "• I provide general fitness recommendations, not medical advice.\n"
        "• My suggestions may not account for all medical conditions.\n"
        "• For injuries, chronic conditions, or health concerns, professional consultation is required.\n\n"

        "[b]How to use me:[/b]\n"
        "Just type what you need, for example:\n"
        "• 'Calculate my BMI'\n"
        "• 'Calculate calorie'\n"
        "• 'Show me a workout plan'\n"
        "• 'What’s my daily calorie goal?'\n"
        "• 'Motivate me'\n"
        "• 'Tips for weight loss'\n"
        "• 'Can you give me fitness articles'\n\n"

        "[b]What would you like to do today?[/b]"

    )


def handle_unknown_message(message: str) -> str:
    """Handle unknown messages"""
    return (
        "I'm not sure I understood that.\n\n"
        "Try asking me about:\n"
        "- BMI calculation ('I am 170cm and 65kg')\n"
        "- Daily calories\n"
        "- Workout recommendations\n"
        "- Fitness tips\n"
        "- Motivation\n\n"
        "Or type 'help' to see what I can do!"
    )