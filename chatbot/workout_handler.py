# chatbot/workout_handler.py

import json
from typing import Dict, Any
import os
from ml_client import get_ml_workout_plan


def get_workout_plan(user_id: int, goal: str, level: str, condition: str) -> list:
    """
    Get workout plan from JSON
    ✅ Matches your Workouts.json structure
    """
    # ✅ Try ML first
    ml_plan = get_ml_workout_plan(user_id, goal, level, condition)
    if ml_plan:
        return ml_plan

    workouts = load_workouts()

    try:
        plan = workouts["goals"][goal][level][condition]
        return plan
    except KeyError as e:
        print(
            f"⚠️ Workout not found for: goal={goal}, level={level}, condition={condition}")
        return []
    except Exception as e:
        print(f"⚠️ Error getting workout plan: {e}")
        return []

def load_workouts():
    """Load workouts from JSON file"""
    try:
        BASE_DIR = os.path.dirname(__file__)
        PROJECT_ROOT = os.path.dirname(BASE_DIR)  # ⬅️ go up one level

        with open(os.path.join(PROJECT_ROOT, "Workouts.json"), "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading workouts: {e}")
        return {}


def extract_goal_from_text(text: str) -> str:
    """
    Extract workout goal from user message
    ✅ ENHANCED: More comprehensive keyword matching for auto-detection
    """
    text = text.lower()

    # Lose weight keywords
    if any(word in text for word in [
        "lose", "loss", "cut", "slim", "shed",
        "lose weight", "weight loss", "losing weight",
        "drop weight", "reduce weight", "slim down",
        "get lean", "fat loss", "burn fat"
    ]):
        return "lose_weight"

    # Gain weight keywords
    elif any(word in text for word in [
        "gain weight", "bulk", "mass", "put on weight",
        "weight gain", "bulk up", "get bigger", "add weight",
        "increase weight"
    ]):
        return "gain_weight"

    # Gain muscles keywords - ✅ ENHANCED with "build muscle"
    elif any(word in text for word in [
        "muscle", "strength", "strong", "toned", "build",
        "gain muscle", "gain muscles", "build muscle", "build muscles",
        "muscle gain", "get muscular", "get ripped", "get toned",
        "strength training", "bodybuilding", "muscle building",
        "add muscle", "grow muscle", "pack on muscle"
    ]):
        return "gain_muscles"

    # Keep fit keywords
    elif any(word in text for word in [
        "fit", "maintain", "stay", "keep",
        "keep fit", "stay fit", "maintenance",
        "stay healthy", "general fitness", "overall fitness",
        "stay in shape", "maintain weight"
    ]):
        return "keep_fit"

    return None


def extract_level_from_text(text: str) -> str:
    """
    Extract fitness level from user message
    ✅ IMPROVED VERSION with comprehensive matching
    """
    text = text.lower()

    # Beginner level
    if any(word in text for word in [
        "beginner", "beginer", "new", "start", "novice",
        "just starting", "first time", "never worked out",
        "basic", "newbie", "starter"
    ]):
        return "beginner"

    # Intermediate level (also matches "medium" from your JSON structure)
    elif any(word in text for word in [
        "intermediate", "medium", "moderate", "middle",
        "average", "some experience", "been working out",
        "regularly exercise", "occasional", "mid-level"
    ]):
        return "intermediate"

    # Advanced level
    elif any(word in text for word in [
        "advanced", "expert", "pro", "experienced",
        "high level", "veteran", "years of experience",
        "very experienced", "athlete", "competitive"
    ]):
        return "advanced"

    return None


def extract_condition_from_text(text: str) -> str | None:
    """
    Extract health condition status from text
    Returns: 'normal' or 'health_condition' or None
    """
    text = text.lower().strip()

    # Check for "Yes, I have conditions"
    yes_keywords = ["yes", "i have", "i do", "health condition", "health issue",
                    "medical condition", "injury", "condition"]

    # Check for "No, I don't have conditions"
    no_keywords = ["no", "none", "don't have", "do not have", "no health",
                   "no condition", "no issue", "healthy", "fine", "good health",
                   "no medical", "not have", "dont have"]

    # Check no keywords first (more specific)
    if any(kw in text for kw in no_keywords):
        return "normal"

    # Then check yes keywords
    if any(kw in text for kw in yes_keywords):
        return "health_condition"

    return None


def get_workout_plan(goal: str, level: str, condition: str) -> list:
    """
    Get workout plan from JSON
    ✅ Matches your Workouts.json structure
    """
    workouts = load_workouts()

    try:
        # Access: workouts["goals"][goal][level][condition]
        plan = workouts["goals"][goal][level][condition]
        return plan
    except KeyError as e:
        print(
            f"⚠️ Workout not found for: goal={goal}, level={level}, condition={condition}")
        return []
    except Exception as e:
        print(f"⚠️ Error getting workout plan: {e}")
        return []


def format_workout_plan(exercises: list, has_condition: bool = False) -> str:
    """
    Format workout plan as readable text
    ✅ Matches your exercise structure with name, sets, reps, rest
    """
    if not exercises:
        return "No workout plan found for these criteria. Please try again with different options."

    response = "[b]Great! Here's your Personalized Workout Plan:[/b]\n\n"

    for i, exercise in enumerate(exercises, 1):
        name = exercise.get("name", "Unknown Exercise")
        sets = exercise.get("sets", "N/A")
        reps = exercise.get("reps", "N/A")
        rest = exercise.get("rest", "N/A")

        response += f"[b]{i}. {name}[/b]\n"
        response += f"   - Sets: {sets}\n"
        response += f"   - Reps: {reps}\n"
        response += f"   - Rest: {rest}\n\n"

    if has_condition:
        response += "Note: Some exercises may need modification due to your health condition. Always consult your doctor.\n\n"

    response += "[b]Tips:[/b]\n"
    response += "• Warm up for 5-10 minutes before starting\n"
    response += "• Focus on proper form over speed\n"
    response += "• Stay hydrated throughout your workout\n"
    response += "• Cool down and stretch after finishing\n"

    return response


# ✅ Helper function for debugging
def test_workout_extraction():
    """Test the extraction functions with common phrases"""
    test_cases = [
        ("I want to build muscle", "gain_muscles"),
        ("I want to lose weight", "lose_weight"),
        ("I'm a beginner", "beginner"),
        ("I'm intermediate level", "intermediate"),
        ("I have no health issues", "normal"),
        ("Yes I have a condition", "health_condition"),
    ]

    print("Testing Workout Extraction Functions:")
    print("=" * 50)

    for text, expected in test_cases:
        if "muscle" in text or "weight" in text:
            result = extract_goal_from_text(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} Goal: '{text}' → {result} (expected: {expected})")

        elif "beginner" in text or "intermediate" in text:
            result = extract_level_from_text(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} Level: '{text}' → {result} (expected: {expected})")

        elif "health" in text or "condition" in text or "no" in text:
            result = extract_condition_from_text(text)
            status = "✅" if result == expected else "❌"
            print(f"{status} Condition: '{text}' → {result} (expected: {expected})")


if __name__ == "__main__":
    test_workout_extraction()