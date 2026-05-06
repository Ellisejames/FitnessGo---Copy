from __future__ import annotations

import os
from typing import Dict, List, Optional

import requests

ML_RECOMMENDER_URL = os.getenv("ML_RECOMMENDER_URL", "").strip()


def get_ml_workout_plan(
    user_id: int,
    goal: str,
    level: str,
    condition: str,
    top_k: int = 10,
) -> Optional[List[Dict]]:
    if not ML_RECOMMENDER_URL:
        return None

    payload = {
        "user_id": user_id,
        "goal": goal,
        "level": level,
        "condition": condition,
        "top_k": top_k,
    }

    try:
        response = requests.post(
            f"{ML_RECOMMENDER_URL}/recommend/workout",
            json=payload,
            timeout=5,
        )
        response.raise_for_status()
        data = response.json()
        return data.get("exercises") or None
    except Exception:
        return None