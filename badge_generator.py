"""
badge_generator.py - Generates exclusive achievement badges for students.

Badge Philosophy: Badges are RARE and EXCLUSIVE. Only truly exceptional
students earn badges. This makes them meaningful achievements.

Badge Types (all ML-driven):
  - A+ Grade badge     : Only for students with >= 90% overall (ML-predicted A+)
  - Subject Topper     : One badge per subject — only the class #1 scorer
  - Position badges    : 1st, 2nd, 3rd position only
  - Discipline         : Only for students with perfect obedient score (10/10)
  - Complete Attendance: Only for students with perfect punctual score (10/10)
  - Academic Excellence: Only for students with >= 90% in ALL subjects
"""

import os
import shutil
from config import (
    BADGE_ASSETS_DIR, SUBJECT_BADGE_FILES, GRADE_BADGE_FILE,
    POSITION_BADGE_FILES, SPECIAL_BADGE_FILES,
)


def _copy_badge(badge_filename, output_path):
    """Copy a badge asset to the student's badges directory."""
    source = os.path.join(BADGE_ASSETS_DIR, badge_filename)
    if not os.path.exists(source):
        return None
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    shutil.copy2(source, output_path)
    return output_path


def generate_student_badges(student, ml_result, topper_subjects=None,
                             position=None, is_behavior_topper=False,
                             is_punctuality_topper=False):
    """
    Generate EXCLUSIVE achievement badges for a student.

    Badges are rare — most students earn 0-2 badges. Only exceptional
    students collect multiple.

    Args:
        student: student data dict
        ml_result: ML prediction result
        topper_subjects: list of subjects where this student is class topper
        position: int (1, 2, 3) or None
        is_behavior_topper: True if student has perfect obedient score
        is_punctuality_topper: True if student has perfect punctual score

    Returns:
        dict with badge info and file paths
    """
    from config import get_student_dir

    student_id = student["student_id"]
    class_num = student["class_num"]
    exam_type = student["exam_type"]

    student_dir = get_student_dir(class_num, exam_type, student_id)
    badges_dir = os.path.join(student_dir, "badges")
    os.makedirs(badges_dir, exist_ok=True)

    topper_subjects = topper_subjects or []
    badge_results = {
        "grade": None,
        "toppers": [],
        "position": None,
        "specials": [],
        "total": 0,
    }

    # 1. A+ Grade badge — ONLY for >= 90% overall (ML-predicted A+)
    if ml_result["grade"] == "A+" and student["percentage"] >= 90:
        path = _copy_badge(GRADE_BADGE_FILE,
                           os.path.join(badges_dir, "grade_aplus.png"))
        if path:
            badge_results["grade"] = path
            badge_results["total"] += 1

    # 2. Subject Topper badges — ONLY the #1 scorer gets the badge
    for subj in topper_subjects:
        badge_file = SUBJECT_BADGE_FILES.get(subj)
        if badge_file:
            safe_subj = subj.replace("/", "_").replace(" ", "_").lower()
            path = _copy_badge(badge_file,
                               os.path.join(badges_dir, f"{safe_subj}_topper.png"))
            if path:
                badge_results["toppers"].append((subj, path))
                badge_results["total"] += 1

    # 3. Position badge — top 3 only
    if position and position in (1, 2, 3):
        badge_file = POSITION_BADGE_FILES.get(position)
        if badge_file:
            path = _copy_badge(badge_file,
                               os.path.join(badges_dir, f"position_{position}.png"))
            if path:
                badge_results["position"] = path
                badge_results["total"] += 1

    # 4. Academic Excellence — >= 90% in ALL subjects (extremely rare)
    all_above_90 = all(pct >= 90 for pct in student["subject_percentages"].values())
    if all_above_90:
        path = _copy_badge(SPECIAL_BADGE_FILES["academic_excellence"],
                           os.path.join(badges_dir, "academic_excellence.png"))
        if path:
            badge_results["specials"].append(("academic_excellence", path))
            badge_results["total"] += 1

    # 5. Discipline badge — ONLY for perfect 10/10 obedient score
    if is_behavior_topper:
        path = _copy_badge(SPECIAL_BADGE_FILES["discipline"],
                           os.path.join(badges_dir, "discipline.png"))
        if path:
            badge_results["specials"].append(("discipline", path))
            badge_results["total"] += 1

    # 6. Complete Attendance badge — ONLY for perfect 10/10 punctual score
    if is_punctuality_topper:
        path = _copy_badge(SPECIAL_BADGE_FILES["attendance"],
                           os.path.join(badges_dir, "attendance.png"))
        if path:
            badge_results["specials"].append(("attendance", path))
            badge_results["total"] += 1

    return badge_results
