"""
main.py - Entry point for the AI-Powered Student Report System.

Flow:
  1. Initialize SQLite database
  2. Import from Excel if DB is empty
  3. For each class x exam type:
     - Fetch students from DB
     - Run ML predictions
     - Compute class toppers (one per subject)
     - Compute position holders (1st, 2nd, 3rd)
     - Create per-student directories
     - Generate PDF report cards with topper badges & position
     - Generate achievement badge images (gaming-style PNGs)
  4. Generate certificates based on YEARLY performance
  5. Print summary
"""

import os
import sys
from database import (
    init_db, seed_sample_data, is_db_populated,
    get_class_exam_students, get_subject_toppers,
    get_position_holders,
    save_report_metadata, save_certificate_metadata,
    get_yearly_student_summary, get_yearly_subject_toppers,
    get_yearly_position_holders,
)
from model import load_model, predict_student
from report_generator import generate_student_report
from certificate_generator import (
    generate_academic_certificate,
    generate_subject_topper_certificate,
    generate_behavior_certificate,
    generate_punctuality_certificate,
    generate_position_certificate,
)
from badge_generator import generate_student_badges
from config import (
    CLASSES, EXAM_TYPES, get_exam_label, get_student_dir,
    SUBJECT_TITLES, SPECIAL_TITLES, POSITION_TITLES,
)


def process_class_exam(class_num, exam_type, model):
    """
    Process a single class/exam: generate reports and badges.
    Certificates are generated separately based on yearly data.
    """
    try:
        students = get_class_exam_students(class_num, exam_type)
    except Exception:
        students = []

    if not students:
        return None

    # Compute class averages
    class_averages = {}
    subjects = set()
    for s in students:
        subjects.update(s["subject_percentages"].keys())
    for subject in subjects:
        total = sum(s["subject_percentages"].get(subject, 0) for s in students)
        count = sum(1 for s in students if subject in s["subject_percentages"])
        class_averages[subject] = total / count if count > 0 else 0

    # Get toppers (highest marks per subject)
    toppers = get_subject_toppers(class_num, exam_type)

    # Get position holders (ranked by overall percentage)
    position_holders = get_position_holders(class_num, exam_type, top_n=3)
    position_map = {p["student_id"]: p for p in position_holders}

    report_count = 0
    badge_count = 0

    for student in students:
        sid = student["student_id"]

        # ML prediction
        ml_result = predict_student(model, student)

        # Determine topper subjects for this student
        topper_subjects = [subj for subj, info in toppers.items()
                           if info["student_id"] == sid]

        # Determine position
        position_info = position_map.get(sid)
        position = position_info["position"] if position_info else None

        # Special flags (exclusive: perfect 10/10 only)
        has_perfect_discipline = (student["obedient"] == 10)
        has_perfect_attendance = (student["punctual"] == 10)

        # Create per-student directory
        student_dir = get_student_dir(class_num, exam_type, sid)
        os.makedirs(student_dir, exist_ok=True)

        # Generate achievement badges
        badge_results = generate_student_badges(
            student, ml_result,
            topper_subjects=topper_subjects,
            position=position,
            is_behavior_topper=has_perfect_discipline,
            is_punctuality_topper=has_perfect_attendance,
        )
        badge_count += badge_results.get("total", 0)

        # Generate report card
        report_path = generate_student_report(
            student, ml_result,
            class_averages=class_averages,
            topper_subjects=topper_subjects,
            position=position,
            badge_results=badge_results,
        )
        save_report_metadata(sid, class_num, exam_type,
                             report_path, ml_result["grade"], student["percentage"])
        report_count += 1

    return {
        "student_count": len(students),
        "report_count": report_count,
        "badge_count": badge_count,
    }


def generate_yearly_certificates(class_num, model):
    """
    Generate certificates based on WHOLE-YEAR performance.
    Aggregates all exam types (midterm, final, bimonthly_1, bimonthly_2)
    to determine certificate-worthy students.
    """
    students = get_yearly_student_summary(class_num)
    if not students:
        return {"cert_counts": {}, "info_lines": []}

    toppers = get_yearly_subject_toppers(class_num)
    position_holders = get_yearly_position_holders(class_num, top_n=3)
    position_map = {p["student_id"]: p for p in position_holders}

    cert_counts = {
        "academic": 0, "subject_topper": 0,
        "behavior": 0, "punctuality": 0, "position": 0,
    }
    info_lines = []

    for student in students:
        sid = student["student_id"]

        # Certificate output directory — under annual folder
        cert_dir = os.path.join("media", f"class_{class_num}", "annual",
                                str(sid), "certificates")

        # Determine what this student deserves
        topper_subjects = [subj for subj, info in toppers.items()
                           if info["student_id"] == sid]
        position_info = position_map.get(sid)
        position = position_info["position"] if position_info else None
        has_perfect_discipline = (student["obedient"] >= 9)  # Yearly avg >= 9
        has_perfect_attendance = (student["punctual"] >= 9)   # Yearly avg >= 9

        # Academic Excellence (>= 90% in ALL subjects across the year)
        cert = generate_academic_certificate(student, output_dir=cert_dir)
        if cert:
            save_certificate_metadata(sid, class_num, "academic", None, cert)
            cert_counts["academic"] += 1
            info_lines.append(
                f"    [★] Academic Excellence: {student['name']} ({student['percentage']:.1f}%)")

        # Subject Topper certificates (yearly best per subject)
        for subj in topper_subjects:
            cert = generate_subject_topper_certificate(
                student, subj, toppers[subj], output_dir=cert_dir)
            if cert:
                save_certificate_metadata(sid, class_num, "subject_topper", subj, cert)
                cert_counts["subject_topper"] += 1
                title = SUBJECT_TITLES.get(subj, f"{subj} Topper")
                info_lines.append(
                    f"    [*] {title}: {student['name']} ({toppers[subj]['percentage']:.1f}%)")

        # Discipline Award (yearly average obedient >= 9)
        if has_perfect_discipline:
            cert = generate_behavior_certificate(student, output_dir=cert_dir)
            if cert:
                save_certificate_metadata(sid, class_num, "behavior", None, cert)
                cert_counts["behavior"] += 1
                info_lines.append(
                    f"    [*] {SPECIAL_TITLES['behavior']}: {student['name']} (avg {student['obedient']}/10)")

        # Attendance Champion (yearly average punctual >= 9)
        if has_perfect_attendance:
            cert = generate_punctuality_certificate(student, output_dir=cert_dir)
            if cert:
                save_certificate_metadata(sid, class_num, "punctuality", None, cert)
                cert_counts["punctuality"] += 1
                info_lines.append(
                    f"    [*] {SPECIAL_TITLES['punctuality']}: {student['name']} (avg {student['punctual']}/10)")

        # Position Holder certificates (1st, 2nd, 3rd — yearly rank)
        if position_info and position in (1, 2, 3):
            cert = generate_position_certificate(
                student, position, position_info, output_dir=cert_dir)
            if cert:
                save_certificate_metadata(sid, class_num, "position", str(position), cert)
                cert_counts["position"] += 1
                pos_title = POSITION_TITLES.get(position, f"#{position}")
                info_lines.append(
                    f"    [#] {pos_title}: {student['name']} ({position_info['percentage']:.1f}%)")

    return {
        "cert_counts": cert_counts,
        "info_lines": info_lines,
    }


def main():
    print()
    print("=" * 65)
    print("  AI-POWERED ACADEMIC REPORTING MODULE")
    print("  Database-Driven | Class-wise | ML-Graded | Badges")
    print("=" * 65)
    print()

    # Step 1: Initialize database
    print("  [1/5] Initializing database...")
    init_db()
    print("         > Database ready")

    # Step 2: Seed data if DB is empty
    if not is_db_populated():
        print("  [2/5] Seeding sample student data...")
        results = seed_sample_data()
        for sheet, count in results.items():
            print(f"         > {sheet}: {count} students")
    else:
        print("  [2/5] Database already populated (OK)")

    # Step 3: Load ML model
    print("  [3/5] Loading ML grading model...")
    model = load_model()
    print("         > Model ready")
    print()

    # Step 4: Process each class and exam type (reports + badges)
    print("  [4/5] Generating reports & badges...")
    print("-" * 65)

    total_reports = 0
    total_badges = 0
    total_students = 0

    for class_num in CLASSES:
        print(f"\n  === CLASS {class_num} ===")

        for exam_type in EXAM_TYPES:
            exam_label = get_exam_label(exam_type)
            print(f"  -- {exam_label}:", end=" ")

            result = process_class_exam(class_num, exam_type, model)

            if result is None:
                print("No data")
                continue

            total_reports += result["report_count"]
            total_badges += result["badge_count"]
            total_students += result["student_count"]
            print(f"{result['report_count']} reports, {result['badge_count']} badges")

        print(f"  {'=' * 25}")

    # Step 5: Generate certificates based on YEARLY performance
    print()
    print("  [5/5] Generating yearly certificates...")
    total_certs = {"academic": 0, "subject_topper": 0, "behavior": 0,
                   "punctuality": 0, "position": 0}
    all_info_lines = []

    for class_num in CLASSES:
        cert_result = generate_yearly_certificates(class_num, model)
        for k, v in cert_result["cert_counts"].items():
            total_certs[k] += v
        all_info_lines.extend(cert_result["info_lines"])
        cert_total = sum(cert_result["cert_counts"].values())
        print(f"         > Class {class_num}: {cert_total} certificates (yearly)")

    # Summary
    print()
    print("=" * 65)
    print("  GENERATION COMPLETE")
    print("=" * 65)
    print(f"  Students processed    : {total_students}")
    print(f"  Report cards          : {total_reports}")
    print(f"  Achievement badges    : {total_badges}")
    print(f"  Certificates (yearly) :")
    print(f"    Academic Excellence : {total_certs['academic']}")
    print(f"    Subject Toppers     : {total_certs['subject_topper']}")
    print(f"    Behavior Excellence : {total_certs['behavior']}")
    print(f"    Attendance Champion : {total_certs['punctuality']}")
    print(f"    Position Holders    : {total_certs['position']}")

    if all_info_lines:
        print()
        print("  -- YEARLY AWARDS --")
        for info in all_info_lines:
            print(f"  {info}")

    print()
    print("  Output structure:")
    print("    media/class_N/exam_type/STUDENT_ID/")
    print("      report_card.pdf")
    print("      badges/  (achievement badge PNGs)")
    print("    media/class_N/annual/STUDENT_ID/")
    print("      certificates/  (yearly awards)")
    print("  DB: data/academic.db")
    print("=" * 65)


if __name__ == "__main__":
    main()
