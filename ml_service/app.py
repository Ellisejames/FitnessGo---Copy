"""FastAPI app for serving workout recommendations."""
from __future__ import annotations

import os
from typing import Dict, List, Optional

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

MODEL_PATH = os.path.join(os.path.dirname(__file__), "model.pkl")

app = FastAPI(title="FitnessGo ML Service")


class WorkoutRequest(BaseModel):
    user_id: int
    goal: str
    level: str
    condition: str
    top_k: Optional[int] = 10


class WorkoutResponse(BaseModel):
    exercises: List[Dict]


def load_model():
    if not os.path.exists(MODEL_PATH):
        return None
    return joblib.load(MODEL_PATH)


@app.on_event("startup")
def startup_event():
    app.state.model = load_model()


@app.post("/recommend/workout", response_model=WorkoutResponse)
def recommend_workout(payload: WorkoutRequest):
    model = app.state.model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")

    encoder = model["encoder"]
    neighbors = model["neighbors"]
    records = model["records"]

    query = np.array([[payload.goal, payload.level, payload.condition]], dtype=object)
    encoded = encoder.transform(query)

    n_neighbors = min(payload.top_k or 10, len(records))
    distances, indices = neighbors.kneighbors(encoded, n_neighbors=n_neighbors)

    exercises = []
    for idx in indices[0]:
        record = records[idx]
        exercises.append(
            {
                "name": record.get("name"),
                "sets": record.get("sets"),
                "reps": record.get("reps"),
                "rest": record.get("rest"),
            }
        )

    return WorkoutResponse(exercises=exercises)
