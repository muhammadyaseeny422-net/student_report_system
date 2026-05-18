"""
main.py - Entry point for the Multi-Class, Multi-Exam Student Report System.

Processes all classes (6-10) and exam types (midterm, final, bimonthly_1, bimonthly_2):
  1. Loads class/exam-specific student data from Excel
  2. Runs ML model for grade prediction, remarks, and badges
  3. Generates PDF report cards (all exams)
  4. Generates PDF certificates (final term only)
"""

import os
import sys
from data_loader import load_data
from model import load_model, predict_student
from report_generator import generate_student_report
from certificate_generator import generate_all_certificates
from config import CLASSES, EXAM_TYPES, get_exam_label, DEFAULT_EXCEL_FILE


def process_class_exam(class_num, exam_type, model):
    """
    Process a single class/exam combination.

    Returns:
        dict with report_count, cert_counts, student_count
    """
    exam_label = get_exam_label(exam_type)

    try:
        students = load_data(class_num, exam_type)
    except (ValueError, FileNotFoundError) as e:
        print(f"    SKIPPED: {e}")
        return None

    print(f"    Loaded {len(students)} students")

    report_count = 0
    cert_counts = {"academic": 0, "subject": 0, "behavior": 0, "punctuality": 0}

    for student in students:
        # ML prediction (uses normalized percentages internally)
        ml_result = predict_student(model, student)

        # Store ML results in student dict for certificate generation
        student["_ml_result"] = ml_result

        # Generate report card
        generate_student_report(student, ml_result)
        report_count += 1

    # Generate certificates ONLY for final term
    if exam_type == "final":
        for student in students:
            certs = generate_all_certificates(student)
            if certs["academic"]:
                cert_counts["academic"] += 1
            cert_counts["subject"] += len(certs["subject"])
            if certs["behavior"]:
                cert_counts["behavior"] += 1
            if certs["punctuality"]:
                cert_counts["punctuality"] += 1

    return {
        "student_count": len(students),
        "report_count": report_count,
        "cert_counts": cert_counts,
    }


def main():
    # Check data file exists
    if not os.path.exists(DEFAULT_EXCEL_FILE):
        print(f"Error: {DEFAULT_EXCEL_FILE} not found.")
        print("Please place the student marks Excel file in the data/ folder.")
        return

    print("=" * 65)
    print("  MULTI-CLASS STUDENT REPORT & CERTIFICATE GENERATION SYSTEM")
    print("=" * 65)
    print()

    # Step 1: Load ML model
    print("Step 1: Loading ML grading model...")
    model = load_model()
    print()

    # Step 2: Process each class and exam type
    print("Step 2: Processing all classes and exam types...")
    print("-" * 65)

    total_reports = 0
    total_certs = {"academic": 0, "subject": 0, "behavior": 0, "punctuality": 0}
    total_students_processed = 0

    for class_num in CLASSES:
        print(f"\n  === CLASS {class_num} ===")

        for exam_type in EXAM_TYPES:
            exam_label = get_exam_label(exam_type)
            print(f"  -- {exam_label}:", end=" ")

            result = process_class_exam(class_num, exam_type, model)

            if result is None:
                continue

            total_reports += result["report_count"]
            total_students_processed += result["student_count"]
            print(f"{result['report_count']} reports generated", end="")

            if exam_type == "final":
                certs = result["cert_counts"]
                cert_total = sum(certs.values())
                if cert_total > 0:
                    print(f" + {cert_total} certificates", end="")
                for k, v in certs.items():
                    total_certs[k] += v

            print()  # newline

        print(f"  {'=' * 25}")

    # Summary
    print()
    print("=" * 65)
    print("  GENERATION COMPLETE")
    print("=" * 65)
    print(f"  Total students processed : {total_students_processed}")
    print(f"  Total report cards       : {total_reports}")
    print(f"  Certificates (final term):")
    print(f"    Academic Excellence     : {total_certs['academic']}")
    print(f"    Subject Excellence      : {total_certs['subject']}")
    print(f"    Behavior Excellence     : {total_certs['behavior']}")
    print(f"    Punctuality             : {total_certs['punctuality']}")
    print()
    print("  Output structure: media/class_N/exam_type/reports/")
    print("  Certificates   : media/class_N/final/certificates/")
    print()
    print("  CMS Integration: Use cms_integration.py functions:")
    print("    - get_student_access(student_id, class_num)")
    print("    - get_teacher_access(student_ids, class_num)")
    print("    - get_admin_access(class_num, exam_type)")
    print("    - update_student_marks(student_id, marks, class_num, exam_type)")
    print("=" * 65)


if __name__ == "__main__":
    main()
