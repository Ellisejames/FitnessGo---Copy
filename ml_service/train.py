"""Train a lightweight recommender model from Workout.json data."""
from __future__ import annotations

import joblib
import numpy as np
from sklearn.compose import ColumnTransformer
from sklearn.neighbors import NearestNeighbors
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder

from preprocess import load_workout_records

MODEL_PATH = "model.pkl"


def train() -> None:
    records = load_workout_records()
    if not records:
        raise RuntimeError("No workout records found to train on.")

    goals = [r["goal"] for r in records]
    levels = [r["level"] for r in records]
    conditions = [r["condition"] for r in records]

    features = np.array(list(zip(goals, levels, conditions)), dtype=object)

    encoder = OneHotEncoder(handle_unknown="ignore")
    feature_matrix = encoder.fit_transform(features)

    neighbors = NearestNeighbors(metric="cosine")
    neighbors.fit(feature_matrix)

    artifacts = {
        "encoder": encoder,
        "neighbors": neighbors,
        "records": records,
    }

    joblib.dump(artifacts, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH} ({len(records)} records).")


if __name__ == "__main__":
    train()
