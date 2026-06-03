"""
model.py - ML-based grading system using Random Forest.

Uses percentage-normalized features so the model works across
different subject structures and max marks.

Feature vector: 8 subject percentages + avg padding + obedient + punctual = 11 features
"""

import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from config import GRADE_MAP

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "grade_model.pkl")

# Canonical subject order for feature vector (8 subjects for Class 9)
# Note: Biology and Computer are electives — student has one or the other
FEATURE_SUBJECTS = [
    "Urdu", "English", "Maths", "Biology", "Computer",
    "Chemistry", "Physics", "Islamiat", "Pak_Studies"
]


def _build_feature_vector(student):
    """
    Build a normalized feature vector from a student dict.

    Converts all subject marks to percentages (0-100 scale) and
    produces a fixed-length vector of 12 features:
      [9 subject percentages, avg_padding, obedient_scaled, punctual_scaled]

    Biology and Computer are separate slots — student has only one,
    the other defaults to 0.

    Returns:
        list of 12 float features
    """
    percentages = student["subject_percentages"]
    features = []

    for subject in FEATURE_SUBJECTS:
        features.append(percentages.get(subject, 0))

    # Average of actual subjects (exclude zeros from missing elective)
    actual = [f for f in features if f > 0]
    avg_pct = sum(actual) / len(actual) if actual else 0
    features.append(avg_pct)

    # Behavioral traits (scale 0-10 to 0-100)
    features.append(student["obedient"] * 10)
    features.append(student["punctual"] * 10)

    return features


def _generate_synthetic_data(n_samples=2000):
    """
    Generate synthetic training data covering all grade ranges.

    Features: 9 subject pcts + avg_padding + obedient + punctual = 12
    Labels: grade class (0=A+, 1=A, 2=B, 3=C, 4=D)
    """
    rng = np.random.RandomState(42)
    X = []
    y = []

    grade_ranges = [
        (0, 90, 100),   # A+
        (1, 80, 89),    # A
        (2, 65, 79),    # B
        (3, 50, 64),    # C
        (4, 30, 49),    # D
    ]

    samples_per_grade = n_samples // len(grade_ranges)

    for grade_label, low_pct, high_pct in grade_ranges:
        for _ in range(samples_per_grade):
            target_avg = rng.uniform(low_pct, high_pct)
            # 9 subject slots (one of Bio/Computer will be 0)
            subject_pcts = []
            for j in range(9):
                # Randomly zero out either Bio (idx 3) or Computer (idx 4)
                if j == 3 and rng.random() > 0.55:
                    subject_pcts.append(0)
                    continue
                if j == 4 and rng.random() > 0.55:
                    subject_pcts.append(0)
                    continue
                pct = target_avg + rng.normal(0, 8)
                pct = np.clip(pct, 0, 100)
                subject_pcts.append(round(pct, 1))

            # Average padding (of non-zero subjects)
            actual = [p for p in subject_pcts if p > 0]
            avg_pad = sum(actual) / len(actual) if actual else 0

            base_behavior = min(100, max(0, target_avg + rng.normal(0, 15)))
            obedient = round(np.clip(base_behavior + rng.normal(0, 10), 0, 100), 1)
            punctual = round(np.clip(base_behavior + rng.normal(0, 10), 0, 100), 1)

            features = subject_pcts + [avg_pad, obedient, punctual]
            X.append(features)
            y.append(grade_label)

    return np.array(X), np.array(y)


def train_and_save_model():
    """Train the Random Forest model and save it."""
    print("  Generating synthetic training data...")
    X, y = _generate_synthetic_data()

    print(f"  Training Random Forest on {len(X)} samples...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        n_jobs=-1
    )
    model.fit(X_train, y_train)

    accuracy = model.score(X_test, y_test)
    print(f"  Model accuracy: {accuracy:.2%}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"  Model saved to {MODEL_PATH}")

    return model


def load_model():
    """Load the trained model from disk. Train if not found."""
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    else:
        print("  No trained model found. Training new model...")
        return train_and_save_model()


def predict_student(model, student):
    """
    Predict grade and generate ML-driven personalized remarks.

    Uses Random Forest prediction + feature analysis to generate
    subject-specific insights — not generic text.

    Returns:
        dict with: grade, grade_label, remarks
    """
    features = _build_feature_vector(student)
    grade_label = model.predict([features])[0]
    grade_info = GRADE_MAP[grade_label]

    # ─── ML-Driven Remarks ───
    # Analyze subject percentages for personalized insights
    percentages = student["subject_percentages"]
    pct_items = [(s.replace("_", " "), p) for s, p in percentages.items()]
    pct_items.sort(key=lambda x: x[1], reverse=True)

    # Find strongest and weakest subjects
    strongest = pct_items[0] if pct_items else None
    weakest = pct_items[-1] if pct_items else None
    avg_pct = student["percentage"]

    # Build base remark from ML grade
    remark_parts = [grade_info["remarks"]]

    # Add subject-specific ML insight
    if strongest and strongest[1] >= 90:
        remark_parts.append(f"Outstanding in {strongest[0]} ({strongest[1]:.0f}%).")
    elif strongest and strongest[1] >= 75:
        remark_parts.append(f"Strongest in {strongest[0]} ({strongest[1]:.0f}%).")

    if weakest and weakest[1] < 50 and len(pct_items) > 1:
        remark_parts.append(f"Needs focused improvement in {weakest[0]}.")
    elif weakest and weakest[1] < 65 and avg_pct >= 70 and len(pct_items) > 1:
        remark_parts.append(f"Could strengthen {weakest[0]} performance.")

    # Behavioral analysis
    obedient = student["obedient"]
    punctual = student["punctual"]
    if obedient >= 9 and punctual >= 9:
        remark_parts.append("Exemplary discipline and attendance record.")
    elif obedient >= 8:
        remark_parts.append("Shows excellent classroom conduct.")
    elif punctual >= 9:
        remark_parts.append("Commendable attendance and punctuality.")
    elif obedient < 5 or punctual < 5:
        remark_parts.append("Behavioral improvement recommended.")

    full_remarks = " ".join(remark_parts)

    return {
        "grade": grade_info["grade"],
        "grade_label": grade_label,
        "remarks": full_remarks,
    }


def predict_class_batch(model, students):
    """
    Batch-predict grades for all students in a class/exam.

    Args:
        model: trained sklearn model
        students: list of student dicts

    Returns:
        dict of {student_id: ml_result}
    """
    results = {}
    for student in students:
        ml_result = predict_student(model, student)
        results[student["student_id"]] = ml_result
    return results
