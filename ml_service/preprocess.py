"""Utilities for preparing workout data for ML training."""
from __future__ import annotations

import json
import os
from typing import Dict, List


def _workouts_json_path() -> str:
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_dir, "Workouts.json")


def load_workout_records() -> List[Dict]:
    """
    Flatten Workouts.json into a list of workout records.
    Each record contains goal, level, condition, and exercise details.
    """
    path = _workouts_json_path()
    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    records: List[Dict] = []
    goals = data.get("goals", {})

    for goal, levels in goals.items():
        for level, condition_sets in levels.items():
            for condition_key, exercises in condition_sets.items():
                for exercise in exercises:
                    records.append(
                        {
                            "goal": goal,
                            "level": level,
                            "condition": condition_key,
                            "name": exercise.get("name"),
                            "sets": exercise.get("sets"),
                            "reps": exercise.get("reps"),
                            "rest": exercise.get("rest"),
                        }
                    )

    return records
