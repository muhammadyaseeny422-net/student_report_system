"""
model.py - ML-based grading system using Random Forest.

Uses percentage-normalized features so the model is class-agnostic.
Works across all classes (6-10) and exam types regardless of
different subject structures and max marks.

Feature vector: 9 subject percentages + obedient + punctual = 11 features
For classes 9/10 (8 subjects), the 9th slot is filled with the average
of the other subject percentages to maintain consistent feature length.
"""

import os
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from config import GRADE_MAP, BADGE_TIERS

MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "grade_model.pkl")

# Canonical subject order for feature vector (9 slots)
# Classes 6-8 use all 9. Classes 9-10 use 8 (Biology/Computer merged).
FEATURE_SUBJECTS_6_8 = [
    "Urdu", "English", "Maths", "Biology", "Computer",
    "Chemistry", "Physics", "Islamiat", "Pak_Studies"
]

FEATURE_SUBJECTS_9_10 = [
    "Urdu", "English", "Maths", "Biology/Computer",
    "Chemistry", "Physics", "Islamiat", "Pak_Studies"
]


def _build_feature_vector(student):
    """
    Build a normalized feature vector from a student dict.

    Converts all subject marks to percentages (0-100 scale) and
    produces a fixed-length vector of 11 features:
      [9 subject percentages, obedient, punctual]

    For classes 9/10 with 8 subjects, the 9th slot is filled with
    the average percentage to keep the vector length consistent.

    Args:
        student: dict with 'subject_percentages', 'obedient', 'punctual', 'class_num'

    Returns:
        list of 11 float features
    """
    class_num = student.get("class_num", 7)  # Default to class 7 format
    percentages = student["subject_percentages"]

    features = []

    if class_num in (9, 10):
        # 8 subjects — fill 9 slots
        for subject in FEATURE_SUBJECTS_9_10:
            features.append(percentages.get(subject, 0))
        # 9th slot: average of all subject percentages
        avg_pct = sum(features) / len(features) if features else 0
        features.append(avg_pct)
    else:
        # Classes 6-8: all 9 subjects
        for subject in FEATURE_SUBJECTS_6_8:
            features.append(percentages.get(subject, 0))

    # Add behavioral traits (already out of 10, scale to 0-100 for consistency)
    features.append(student["obedient"] * 10)
    features.append(student["punctual"] * 10)

    return features


def _generate_synthetic_data(n_samples=2000):
    """
    Generate synthetic training data covering all grade ranges.

    Features: 9 subject percentages (0-100) + obedient (0-100) + punctual (0-100)
    Labels: grade class (0=A+, 1=A, 2=B, 3=C, 4=D)

    All features are on the same 0-100 percentage scale.
    """
    rng = np.random.RandomState(42)
    X = []
    y = []

    grade_ranges = [
        (0, 90, 100),   # A+: percentage 90-100
        (1, 80, 89),    # A:  percentage 80-89
        (2, 65, 79),    # B:  percentage 65-79
        (3, 50, 64),    # C:  percentage 50-64
        (4, 30, 49),    # D:  percentage below 50
    ]

    samples_per_grade = n_samples // len(grade_ranges)

    for grade_label, low_pct, high_pct in grade_ranges:
        for _ in range(samples_per_grade):
            target_avg = rng.uniform(low_pct, high_pct)

            # Generate 9 subject percentages around the target
            subject_pcts = []
            for _ in range(9):
                pct = target_avg + rng.normal(0, 8)
                pct = np.clip(pct, 0, 100)
                subject_pcts.append(round(pct, 1))

            # Behavioral traits (slightly correlated with academics)
            base_behavior = min(100, max(0, target_avg + rng.normal(0, 15)))
            obedient = round(np.clip(base_behavior + rng.normal(0, 10), 0, 100), 1)
            punctual = round(np.clip(base_behavior + rng.normal(0, 10), 0, 100), 1)

            features = subject_pcts + [obedient, punctual]
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
    Predict grade, remarks, and badges for a student using the ML model.

    Uses percentage-normalized features internally, but does NOT
    modify the student's original marks. Results are purely
    classification output.

    Args:
        model: trained sklearn model
        student: dict with marks, subject_percentages, obedient, punctual, class_num

    Returns:
        dict with: grade, remarks, subject_badges, trait_badges
    """
    # Build percentage-normalized feature vector
    features = _build_feature_vector(student)

    # Predict grade
    grade_label = model.predict([features])[0]
    grade_info = GRADE_MAP[grade_label]

    # Add behavioral remarks
    obedient = student["obedient"]
    punctual = student["punctual"]
    behavior_remark = ""
    if obedient >= 9 and punctual >= 9:
        behavior_remark = " A very well-behaved and punctual student."
    elif obedient >= 9:
        behavior_remark = " Well-behaved, but could improve punctuality."
    elif punctual >= 9:
        behavior_remark = " Punctual, but behavior could be improved."

    full_remarks = grade_info["remarks"] + behavior_remark

    # Determine subject badges using ML-predicted grade context
    # Only award badges to students predicted as B or above
    subject_badges = []
    if grade_label <= 2:  # A+, A, or B
        for subject, sub_pct in student["subject_percentages"].items():
            if sub_pct >= BADGE_TIERS["Genius"]:
                subject_badges.append(f"{subject}_Genius.png")
            elif sub_pct >= BADGE_TIERS["Expert"]:
                subject_badges.append(f"{subject}_Expert.png")
            elif sub_pct >= BADGE_TIERS["Star"]:
                subject_badges.append(f"{subject}_Star.png")

    # Trait badges
    trait_badges = []
    if grade_label <= 2:  # Only for B or above
        if obedient >= 8:
            trait_badges.append("obedient.png")
        if punctual >= 8:
            trait_badges.append("punctual.png")

    return {
        "grade": grade_info["grade"],
        "grade_label": grade_label,
        "remarks": full_remarks,
        "subject_badges": subject_badges,
        "trait_badges": trait_badges,
    }
