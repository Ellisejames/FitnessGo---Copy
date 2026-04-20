# chatbot/data_extractors.py

import re
from typing import Optional, Tuple, Dict


def extract_numbers(text: str) -> list:
    """Extract all numbers from text including decimals"""
    pattern = r'\b\d+\.?\d*\b'
    numbers = re.findall(pattern, text)
    # Filter out unrealistic values and dates
    filtered = []
    for n in numbers:
        num = float(n)
        # Keep numbers that could be height (50-300) or weight (20-300)
        # Exclude very small numbers (<10) and very large numbers (>1000)
        if 10 <= num <= 1000:
            filtered.append(num)
    return filtered


def convert_feet_inches_to_cm(feet: float, inches: float = 0) -> float:
    """Convert feet and inches to centimeters"""
    total_inches = (feet * 12) + inches
    return total_inches * 2.54


def extract_height_weight(text: str) -> Dict[str, Optional[float]]:
    """
    Extract height and weight from user message with context-aware parsing.
    Supports:
    - Metric: "170cm", "height 170", "65 kg"
    - Imperial: "5'9", "5 feet 9 inches", "150 pounds"
    - Mixed: "I am 5'9 and weigh 150 pounds"
    """
    text_lower = text.lower()
    result = {"height": None, "weight": None}

    # ===== HEIGHT EXTRACTION =====
    # Imperial patterns: 5'9", 5 feet 9 inches, 5ft 9in
    feet_inch_patterns = [
        r"(\d+)\s*'\s*(\d+)",  # 5'9
        r"(\d+)\s*feet\s*(\d+)\s*inch",  # 5 feet 9 inches
        r"(\d+)\s*ft\s*(\d+)\s*in",  # 5ft 9in
    ]
    for pattern in feet_inch_patterns:
        match = re.search(pattern, text_lower)
        if match:
            feet = float(match.group(1))
            inches = float(match.group(2))
            if 3 <= feet <= 8:
                result["height"] = round(
                    convert_feet_inches_to_cm(feet, inches), 1)
                break

    # Metric patterns
    if result["height"] is None:
        height_patterns = [
            r'height[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*cm',
            r'(\d+\.?\d*)\s*centimeter',
            r'tall[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*tall'
        ]
        for pattern in height_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                if 50 <= value <= 300:
                    result["height"] = value
                    break

    # ===== WEIGHT EXTRACTION =====
    # Pounds
    pound_patterns = [
        r'(\d+\.?\d*)\s*pounds?',
        r'(\d+\.?\d*)\s*lbs?',
        r'weigh[:\s]+(\d+\.?\d*)\s*pounds?'
    ]
    for pattern in pound_patterns:
        match = re.search(pattern, text_lower)
        if match:
            pounds = float(match.group(1))
            if 40 <= pounds <= 660:
                result["weight"] = round(pounds * 0.453592, 1)
                break

    # Kilograms
    if result["weight"] is None:
        weight_patterns = [
            r'weight[:\s]+(\d+\.?\d*)',
            r'(\d+\.?\d*)\s*kg',
            r'(\d+\.?\d*)\s*kilogram',
            r'weigh[:\s]+(\d+\.?\d*)'
        ]
        for pattern in weight_patterns:
            match = re.search(pattern, text_lower)
            if match:
                value = float(match.group(1))
                if 20 <= value <= 300:
                    result["weight"] = value
                    break

    # ===== CONTEXT-AWARE NUMERIC FALLBACK =====
    if result["height"] is None or result["weight"] is None:
        numbers = extract_numbers(text_lower)

        used_values = set(v for v in result.values() if v is not None)
        remaining_nums = [n for n in numbers if n not in used_values]

        if len(remaining_nums) >= 1:
            # Define context keywords
            height_keywords = ["height", "tall",
                               "cm", "centimeter", "feet", "ft", "'"]
            weight_keywords = ["weight", "weigh", "kg",
                               "kilogram", "pounds", "lbs", "lb"]

            # ✅ FIX: Check if text has weight-specific units (more restrictive)
            has_weight_unit = any(unit in text_lower for unit in [
                                  "kg", "kilogram", "pound", "lbs", "lb"])
            has_height_unit = any(unit in text_lower for unit in [
                                  "cm", "centimeter", "feet", "ft", "'"])

            # Try keyword proximity heuristic
            for num in remaining_nums:
                # Find position of this number in text
                num_str = str(num) if '.' in str(num) else str(int(num))
                idx = text_lower.find(num_str)

                if idx != -1:
                    # Check 15 characters before and after for context (expanded window)
                    context_window = text_lower[max(
                        0, idx-15):min(len(text_lower), idx+len(num_str)+15)]

                    # ✅ FIX: Prioritize weight if weight unit is present in context
                    has_weight_in_context = any(
                        kw in context_window for kw in weight_keywords)
                    has_height_in_context = any(
                        kw in context_window for kw in height_keywords)

                    # If weight unit is in context and weight is missing, assign to weight
                    if result["weight"] is None and has_weight_in_context:
                        result["weight"] = float(num)
                        continue
                    # If height unit is in context and height is missing, assign to height
                    elif result["height"] is None and has_height_in_context:
                        result["height"] = float(num)
                        continue

            # Update remaining numbers after keyword proximity assignment
            used_values = set(v for v in result.values() if v is not None)
            remaining_nums = [
                n for n in remaining_nums if n not in used_values]

            # ✅ Early return if both are found
            if result["height"] is not None and result["weight"] is not None:
                return result

            # ✅ FIX: Unit-sensitive fallback - if only weight units present, don't assign to height
            if len(remaining_nums) >= 1:
                # If only weight units in text and weight is missing, assign to weight
                if has_weight_unit and not has_height_unit and result["weight"] is None:
                    for num in remaining_nums:
                        if 20 <= num <= 300:  # Valid weight range
                            result["weight"] = float(num)
                            remaining_nums.remove(num)
                            break
                # If only height units in text and height is missing, assign to height
                elif has_height_unit and not has_weight_unit and result["height"] is None:
                    for num in remaining_nums:
                        if 50 <= num <= 300:  # Valid height range
                            result["height"] = float(num)
                            remaining_nums.remove(num)
                            break
                # Both missing or both units present - use range-based heuristic
                else:
                    remaining_nums_sorted = sorted(
                        remaining_nums, reverse=True)

                    if result["height"] is None and len(remaining_nums_sorted) >= 1:
                        # Height typically larger (in cm) or in range 50-300
                        for num in list(remaining_nums_sorted):
                            if 50 <= num <= 300:
                                result["height"] = float(num)
                                remaining_nums_sorted.remove(num)
                                break

                    if result["weight"] is None and len(remaining_nums_sorted) >= 1:
                        # Weight typically in range 20-300 kg
                        for num in remaining_nums_sorted:
                            if 20 <= num <= 300:
                                result["weight"] = float(num)
                                break

    return result


def extract_activity_level(text: str) -> Optional[str]:
    """Extract activity level from user message"""
    text = text.lower()

    activity_map = {
        "not very active": [
            "not very active", "sedentary", "inactive", "not active",
            "barely active", "rarely active", "minimal activity",
            "sit all day", "desk job", "no exercise", "couch potato"
        ],
        "lightly active": [
            "lightly active", "light", "slightly active", "somewhat active",
            "walk sometimes", "light exercise", "1-3 days", "casual activity"
        ],
        "active": [
            "active", "moderate", "moderately active", "medium",
            "regular exercise", "3-5 days", "fairly active", "medium level"
        ],
        "very active": [
            "very active", "highly active", "extremely active", "athlete",
            "intense", "heavy exercise", "6-7 days", "very fit", "train daily"
        ]
    }

    for level, keywords in activity_map.items():
        for keyword in keywords:
            if keyword in text:
                return level

    return None


def calculate_bmi(weight: float, height: float) -> Tuple[float, str]:
    """
    Calculate BMI and return status
    BMI = weight (kg) / (height (m))^2
    """
    # Validate inputs
    if height <= 0 or weight <= 0:
        raise ValueError("Height and weight must be positive numbers")

    if height < 50 or height > 300:
        raise ValueError(
            f"Invalid height: {height}cm. Must be between 50-300cm")

    if weight < 20 or weight > 300:
        raise ValueError(
            f"Invalid weight: {weight}kg. Must be between 20-300kg")

    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)

    # Determine BMI status
    if bmi < 18.5:
        status = "Underweight"
    elif 18.5 <= bmi < 25:
        status = "Normal weight"
    elif 25 <= bmi < 30:
        status = "Overweight"
    else:
        status = "Obese"

    return round(bmi, 1), status