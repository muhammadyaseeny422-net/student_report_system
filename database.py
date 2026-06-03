"""
database.py - SQLite database layer for the Student Report System.

Provides:
  - Schema initialization (students, marks, behavior, reports, certificates)
  - Excel bulk import (class-wise, exam-wise)
  - CRUD operations for marks and student data
  - Subject topper queries (one per subject per class/exam)
  - Report and certificate metadata tracking
"""

import sqlite3
import os
import pandas as pd
from config import (
    DATABASE_PATH, CLASSES, EXAM_TYPES,
    get_subject_config, get_sheet_name, TRAIT_CONFIG,
)


# ──────────────────────────────────────────────
#  CONNECTION HELPERS
# ──────────────────────────────────────────────

def _get_connection():
    """Get a SQLite connection with row_factory for dict-like access."""
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


# ──────────────────────────────────────────────
#  SCHEMA INITIALIZATION
# ──────────────────────────────────────────────

def init_db():
    """Create all tables if they don't exist."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS students (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            class_num INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS exam_marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_num INTEGER NOT NULL,
            exam_type TEXT NOT NULL,
            subject TEXT NOT NULL,
            obtained_marks REAL NOT NULL,
            max_marks REAL NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, class_num, exam_type, subject)
        );

        CREATE TABLE IF NOT EXISTS behavior_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_num INTEGER NOT NULL,
            exam_type TEXT NOT NULL,
            obedient INTEGER NOT NULL,
            punctual INTEGER NOT NULL,
            FOREIGN KEY (student_id) REFERENCES students(student_id),
            UNIQUE(student_id, class_num, exam_type)
        );

        CREATE TABLE IF NOT EXISTS generated_reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_num INTEGER NOT NULL,
            exam_type TEXT NOT NULL,
            file_path TEXT NOT NULL,
            grade TEXT,
            percentage REAL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, class_num, exam_type)
        );

        CREATE TABLE IF NOT EXISTS generated_certificates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id TEXT NOT NULL,
            class_num INTEGER NOT NULL,
            cert_type TEXT NOT NULL,
            subject TEXT NOT NULL DEFAULT '',
            file_path TEXT NOT NULL,
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(student_id, class_num, cert_type, subject)
        );

        CREATE INDEX IF NOT EXISTS idx_marks_class_exam
            ON exam_marks(class_num, exam_type);
        CREATE INDEX IF NOT EXISTS idx_behavior_class_exam
            ON behavior_scores(class_num, exam_type);
    """)

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
#  EXCEL BULK IMPORT
# ──────────────────────────────────────────────

def import_from_excel(file_path, classes=None, exam_types=None):
    """
    Bulk import student data from an Excel file into the database.

    Reads sheets named 'class_{N}_{exam_type}' and imports all valid rows.

    Args:
        file_path: path to the Excel file
        classes: list of class numbers to import (defaults to config CLASSES)
        exam_types: list of exam types to import (defaults to config EXAM_TYPES)

    Returns:
        dict with import counts per class/exam
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Excel file not found: {file_path}")

    classes = classes or CLASSES
    exam_types = exam_types or EXAM_TYPES

    conn = _get_connection()
    cursor = conn.cursor()
    results = {}

    for class_num in classes:
        for exam_type in exam_types:
            sheet_name = get_sheet_name(class_num, exam_type)
            try:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
            except ValueError:
                continue  # Sheet doesn't exist, skip

            subject_config = get_subject_config(class_num, exam_type)
            required = ["Student_ID", "Name"] + list(subject_config.keys()) + list(TRAIT_CONFIG.keys())
            missing = [c for c in required if c not in df.columns]
            if missing:
                print(f"  WARNING: Missing columns in {sheet_name}: {missing}")
                continue

            count = 0
            for _, row in df.iterrows():
                student_id = str(row["Student_ID"])
                name = str(row["Name"]).strip()

                # Upsert student
                cursor.execute("""
                    INSERT INTO students (student_id, name, class_num)
                    VALUES (?, ?, ?)
                    ON CONFLICT(student_id) DO UPDATE SET name=excluded.name
                """, (student_id, name, class_num))

                # Insert subject marks
                for subject, max_mark in subject_config.items():
                    val = row.get(subject)
                    if val is None or pd.isna(val):
                        continue
                    obtained = float(val)
                    if 0 <= obtained <= max_mark:
                        cursor.execute("""
                            INSERT INTO exam_marks (student_id, class_num, exam_type, subject, obtained_marks, max_marks)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ON CONFLICT(student_id, class_num, exam_type, subject)
                            DO UPDATE SET obtained_marks=excluded.obtained_marks, max_marks=excluded.max_marks
                        """, (student_id, class_num, exam_type, subject, obtained, max_mark))

                # Insert behavior scores
                obedient = int(row.get("Obedient", 0))
                punctual = int(row.get("Punctual", 0))
                cursor.execute("""
                    INSERT INTO behavior_scores (student_id, class_num, exam_type, obedient, punctual)
                    VALUES (?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, class_num, exam_type)
                    DO UPDATE SET obedient=excluded.obedient, punctual=excluded.punctual
                """, (student_id, class_num, exam_type, obedient, punctual))

                count += 1

            results[f"{sheet_name}"] = count

    conn.commit()
    conn.close()
    return results


# ──────────────────────────────────────────────
#  DATA RETRIEVAL
# ──────────────────────────────────────────────

def get_class_exam_students(class_num, exam_type):
    """
    Fetch all students and their marks for a class/exam from the database.

    Returns a list of student dicts in the same format as the old data_loader:
      - student_id, name, class_num, exam_type
      - marks, max_marks_per_subject, subject_percentages
      - obedient, punctual
      - total_marks, max_marks, percentage
    """
    conn = _get_connection()
    cursor = conn.cursor()

    subject_config = get_subject_config(class_num, exam_type)

    # Get all students who have marks for this class/exam
    cursor.execute("""
        SELECT DISTINCT em.student_id, s.name
        FROM exam_marks em
        JOIN students s ON s.student_id = em.student_id
        WHERE em.class_num = ? AND em.exam_type = ?
        ORDER BY em.student_id
    """, (class_num, exam_type))

    student_rows = cursor.fetchall()
    students = []

    for srow in student_rows:
        sid = srow["student_id"]
        name = srow["name"]

        # Get marks
        cursor.execute("""
            SELECT subject, obtained_marks, max_marks
            FROM exam_marks
            WHERE student_id = ? AND class_num = ? AND exam_type = ?
        """, (sid, class_num, exam_type))

        marks = {}
        max_marks_per_subject = {}
        subject_percentages = {}
        total_obtained = 0
        total_max = 0

        for mrow in cursor.fetchall():
            subject = mrow["subject"]
            obtained = mrow["obtained_marks"]
            max_mark = mrow["max_marks"]
            marks[subject] = obtained
            max_marks_per_subject[subject] = max_mark
            subject_percentages[subject] = (obtained / max_mark) * 100 if max_mark > 0 else 0
            total_obtained += obtained
            total_max += max_mark

        # Get behavior scores
        cursor.execute("""
            SELECT obedient, punctual
            FROM behavior_scores
            WHERE student_id = ? AND class_num = ? AND exam_type = ?
        """, (sid, class_num, exam_type))

        brow = cursor.fetchone()
        obedient = brow["obedient"] if brow else 0
        punctual = brow["punctual"] if brow else 0

        student = {
            "student_id": sid,
            "name": name,
            "class_num": class_num,
            "exam_type": exam_type,
            "marks": marks,
            "max_marks_per_subject": max_marks_per_subject,
            "subject_percentages": subject_percentages,
            "obedient": obedient,
            "punctual": punctual,
            "total_marks": total_obtained,
            "max_marks": total_max,
            "percentage": (total_obtained / total_max) * 100 if total_max > 0 else 0,
        }
        students.append(student)

    conn.close()
    return students


def get_student_by_id(class_num, exam_type, student_id):
    """Fetch a single student's data."""
    students = get_class_exam_students(class_num, exam_type)
    target = str(student_id)
    for s in students:
        if s["student_id"] == target:
            return s
    return None


# ──────────────────────────────────────────────
#  MARKS UPDATE
# ──────────────────────────────────────────────

def upsert_student_marks(student_id, class_num, exam_type, marks_dict, behavior=None):
    """
    Insert or update marks for a student.

    Args:
        student_id: student identifier
        class_num: int
        exam_type: str
        marks_dict: {subject: obtained_marks}
        behavior: optional dict {"obedient": int, "punctual": int}
    """
    conn = _get_connection()
    cursor = conn.cursor()
    subject_config = get_subject_config(class_num, exam_type)

    for subject, obtained in marks_dict.items():
        if subject in subject_config:
            max_mark = subject_config[subject]
            cursor.execute("""
                INSERT INTO exam_marks (student_id, class_num, exam_type, subject, obtained_marks, max_marks)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(student_id, class_num, exam_type, subject)
                DO UPDATE SET obtained_marks=excluded.obtained_marks
            """, (student_id, class_num, exam_type, subject, float(obtained), max_mark))

    if behavior:
        cursor.execute("""
            INSERT INTO behavior_scores (student_id, class_num, exam_type, obedient, punctual)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(student_id, class_num, exam_type)
            DO UPDATE SET obedient=excluded.obedient, punctual=excluded.punctual
        """, (student_id, class_num, exam_type,
              behavior.get("obedient", 0), behavior.get("punctual", 0)))

    conn.commit()
    conn.close()


# ──────────────────────────────────────────────
#  TOPPER QUERIES
# ──────────────────────────────────────────────

def get_subject_toppers(class_num, exam_type):
    """
    Get the single highest scorer for each subject in a class/exam.

    Returns:
        dict of {subject: {"student_id": str, "name": str, "marks": float, "percentage": float}}

    Ties are broken by the student's overall percentage (higher wins).
    """
    conn = _get_connection()
    cursor = conn.cursor()

    subject_config = get_subject_config(class_num, exam_type)
    toppers = {}

    for subject in subject_config:
        cursor.execute("""
            SELECT em.student_id, s.name, em.obtained_marks, em.max_marks,
                   (em.obtained_marks * 100.0 / em.max_marks) as percentage
            FROM exam_marks em
            JOIN students s ON s.student_id = em.student_id
            WHERE em.class_num = ? AND em.exam_type = ? AND em.subject = ?
            ORDER BY em.obtained_marks DESC, em.student_id ASC
            LIMIT 1
        """, (class_num, exam_type, subject))

        row = cursor.fetchone()
        if row:
            toppers[subject] = {
                "student_id": row["student_id"],
                "name": row["name"],
                "marks": row["obtained_marks"],
                "max_marks": row["max_marks"],
                "percentage": row["percentage"],
            }

    conn.close()
    return toppers


def get_behavior_topper(class_num, exam_type):
    """Get the single student with highest combined obedient+punctual score."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bs.student_id, s.name, bs.obedient, bs.punctual,
               (bs.obedient + bs.punctual) as total_score
        FROM behavior_scores bs
        JOIN students s ON s.student_id = bs.student_id
        WHERE bs.class_num = ? AND bs.exam_type = ?
        ORDER BY total_score DESC, bs.student_id ASC
        LIMIT 1
    """, (class_num, exam_type))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "student_id": row["student_id"],
            "name": row["name"],
            "obedient": row["obedient"],
            "punctual": row["punctual"],
        }
    return None


def get_punctuality_topper(class_num, exam_type):
    """Get the single student with highest punctual score."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT bs.student_id, s.name, bs.punctual
        FROM behavior_scores bs
        JOIN students s ON s.student_id = bs.student_id
        WHERE bs.class_num = ? AND bs.exam_type = ?
        ORDER BY bs.punctual DESC, bs.student_id ASC
        LIMIT 1
    """, (class_num, exam_type))

    row = cursor.fetchone()
    conn.close()

    if row:
        return {
            "student_id": row["student_id"],
            "name": row["name"],
            "punctual": row["punctual"],
        }
    return None


# ──────────────────────────────────────────────
#  POSITION HOLDERS
# ──────────────────────────────────────────────

def get_position_holders(class_num, exam_type, top_n=3):
    """
    Get the top N students by overall percentage for a class/exam.

    Returns:
        list of dicts: [{position: 1, student_id, name, percentage}, ...]

    Ties broken by student_id (ascending) for deterministic results.
    """
    students = get_class_exam_students(class_num, exam_type)
    if not students:
        return []

    # Sort by percentage descending, then student_id ascending for tie-breaking
    sorted_students = sorted(students, key=lambda s: (-s["percentage"], s["student_id"]))

    holders = []
    for i, student in enumerate(sorted_students[:top_n]):
        holders.append({
            "position": i + 1,
            "student_id": student["student_id"],
            "name": student["name"],
            "percentage": student["percentage"],
            "total_marks": student["total_marks"],
            "max_marks": student["max_marks"],
        })

    return holders


# ──────────────────────────────────────────────
#  REPORT & CERTIFICATE METADATA
# ──────────────────────────────────────────────

def save_report_metadata(student_id, class_num, exam_type, file_path, grade, percentage):
    """Save or update metadata for a generated report card."""
    conn = _get_connection()
    conn.execute("""
        INSERT INTO generated_reports (student_id, class_num, exam_type, file_path, grade, percentage)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(student_id, class_num, exam_type)
        DO UPDATE SET file_path=excluded.file_path, grade=excluded.grade,
                      percentage=excluded.percentage, generated_at=CURRENT_TIMESTAMP
    """, (student_id, class_num, exam_type, file_path, grade, percentage))
    conn.commit()
    conn.close()


def save_certificate_metadata(student_id, class_num, cert_type, subject, file_path):
    """Save or update metadata for a generated certificate."""
    conn = _get_connection()
    # Use empty string instead of None for subject to match UNIQUE constraint
    subject_val = subject if subject else ''
    conn.execute("""
        INSERT INTO generated_certificates (student_id, class_num, cert_type, subject, file_path)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(student_id, class_num, cert_type, subject)
        DO UPDATE SET file_path=excluded.file_path, generated_at=CURRENT_TIMESTAMP
    """, (student_id, class_num, cert_type, subject_val, file_path))
    conn.commit()
    conn.close()


def get_report_path(student_id, class_num, exam_type):
    """Get the file path of a generated report from metadata."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT file_path FROM generated_reports
        WHERE student_id = ? AND class_num = ? AND exam_type = ?
    """, (student_id, class_num, exam_type))
    row = cursor.fetchone()
    conn.close()
    return row["file_path"] if row else None


def get_certificate_paths(student_id, class_num):
    """Get all certificate file paths for a student."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT cert_type, subject, file_path FROM generated_certificates
        WHERE student_id = ? AND class_num = ?
    """, (student_id, class_num))
    rows = cursor.fetchall()
    conn.close()
    return [{"cert_type": r["cert_type"], "subject": r["subject"], "file_path": r["file_path"]} for r in rows]


def is_db_populated():
    """Check if the database has any student data."""
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) as cnt FROM students")
    row = cursor.fetchone()
    conn.close()
    return row["cnt"] > 0


def get_class_stats(class_num, exam_type):
    """Get summary statistics for a class/exam."""
    conn = _get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT COUNT(DISTINCT student_id) as student_count
        FROM exam_marks
        WHERE class_num = ? AND exam_type = ?
    """, (class_num, exam_type))
    row = cursor.fetchone()
    student_count = row["student_count"] if row else 0

    cursor.execute("""
        SELECT COUNT(*) as report_count
        FROM generated_reports
        WHERE class_num = ? AND exam_type = ?
    """, (class_num, exam_type))
    row = cursor.fetchone()
    report_count = row["report_count"] if row else 0

    cursor.execute("""
        SELECT cert_type, COUNT(*) as cnt
        FROM generated_certificates
        WHERE class_num = ?
        GROUP BY cert_type
    """, (class_num,))
    cert_counts = {r["cert_type"]: r["cnt"] for r in cursor.fetchall()}

    conn.close()
    return {
        "student_count": student_count,
        "report_count": report_count,
        "certificates": cert_counts,
    }


# ──────────────────────────────────────────────
#  YEARLY AGGREGATION (for certificates)
# ──────────────────────────────────────────────

def get_yearly_student_summary(class_num):
    """
    Aggregate student performance across ALL exam types for the year.
    Returns list of student dicts with averaged percentages, behavior, etc.

    Used for certificates — awards based on whole-year performance, not
    just one exam.
    """
    from config import EXAM_TYPES

    conn = _get_connection()
    cursor = conn.cursor()

    # Get all students in the class
    cursor.execute("""
        SELECT DISTINCT s.student_id, s.name
        FROM students s
        JOIN exam_marks em ON s.student_id = em.student_id
        WHERE em.class_num = ?
    """, (class_num,))
    student_rows = cursor.fetchall()

    results = []
    for row in student_rows:
        sid = row["student_id"]
        name = row["name"]

        # Get marks across ALL exam types
        cursor.execute("""
            SELECT exam_type, subject,
                   SUM(obtained_marks) as obtained, SUM(max_marks) as max_m
            FROM exam_marks
            WHERE student_id = ? AND class_num = ?
            GROUP BY exam_type, subject
        """, (sid, class_num))
        marks_rows = cursor.fetchall()

        # Aggregate: compute average percentage per subject across exams
        subject_totals = {}
        subject_max = {}
        for mr in marks_rows:
            subj = mr["subject"]
            subject_totals[subj] = subject_totals.get(subj, 0) + mr["obtained"]
            subject_max[subj] = subject_max.get(subj, 0) + mr["max_m"]

        subject_percentages = {}
        for subj in subject_totals:
            if subject_max[subj] > 0:
                subject_percentages[subj] = (subject_totals[subj] / subject_max[subj]) * 100
            else:
                subject_percentages[subj] = 0

        total = sum(subject_totals.values())
        max_total = sum(subject_max.values())
        percentage = (total / max_total * 100) if max_total > 0 else 0

        # Get average behavior across all exams
        cursor.execute("""
            SELECT AVG(obedient) as avg_ob, AVG(punctual) as avg_pu
            FROM behavior_scores
            WHERE student_id = ? AND class_num = ?
        """, (sid, class_num))
        beh = cursor.fetchone()
        obedient = round(beh["avg_ob"]) if beh and beh["avg_ob"] is not None else 5
        punctual = round(beh["avg_pu"]) if beh and beh["avg_pu"] is not None else 5

        results.append({
            "student_id": sid,
            "name": name,
            "class_num": class_num,
            "exam_type": "annual",
            "marks": subject_totals,
            "max_marks_per_subject": subject_max,
            "subject_percentages": subject_percentages,
            "total_marks": total,
            "max_marks": max_total,
            "percentage": percentage,
            "obedient": obedient,
            "punctual": punctual,
        })

    conn.close()
    return results


def get_yearly_subject_toppers(class_num):
    """Get subject toppers based on yearly (all exams combined) performance."""
    students = get_yearly_student_summary(class_num)
    if not students:
        return {}

    toppers = {}
    subjects = set()
    for s in students:
        subjects.update(s["subject_percentages"].keys())

    for subj in subjects:
        best = None
        best_pct = -1
        for s in students:
            pct = s["subject_percentages"].get(subj, 0)
            if pct > best_pct:
                best_pct = pct
                best = s
        if best:
            toppers[subj] = {
                "student_id": best["student_id"],
                "name": best["name"],
                "percentage": best_pct,
                "marks": best["marks"].get(subj, 0),
                "max_marks": best["max_marks_per_subject"].get(subj, 0),
            }
    return toppers


def get_yearly_position_holders(class_num, top_n=3):
    """Get position holders based on yearly (all exams combined) performance."""
    students = get_yearly_student_summary(class_num)
    if not students:
        return []

    ranked = sorted(students, key=lambda s: s["percentage"], reverse=True)
    holders = []
    for i, s in enumerate(ranked[:top_n]):
        holders.append({
            "student_id": s["student_id"],
            "name": s["name"],
            "position": i + 1,
            "percentage": s["percentage"],
            "total_marks": s["total_marks"],
            "max_marks": s["max_marks"],
        })
    return holders


# ──────────────────────────────────────────────
#  SAMPLE DATA SEEDER (replaces Excel import)
# ──────────────────────────────────────────────

def seed_sample_data():
    """
    Seed the database with realistic sample Class 9 student data.

    Generates 18 students with marks across all 4 exam types.
    Uses numpy random for varied but realistic mark distributions.
    This replaces the need for an Excel file.

    Returns:
        dict with counts per exam type
    """
    import numpy as np

    rng = np.random.RandomState(42)

    # Student roster
    student_names = [
        ("C9-1001", "Ahmed Raza"),
        ("C9-1002", "Junaid Shah"),
        ("C9-1003", "Zara Mahmood"),
        ("C9-1004", "Hamza Ali"),
        ("C9-1005", "Tariq Zafar"),
        ("C9-1006", "Fatima Noor"),
        ("C9-1007", "Usman Ghani"),
        ("C9-1008", "Ayesha Khan"),
        ("C9-1009", "Bilal Hussain"),
        ("C9-1010", "Sara Ahmed"),
        ("C9-1011", "Tariq Chaudhry"),
        ("C9-1012", "Hina Batool"),
        ("C9-1013", "Laiba Khan"),
        ("C9-1014", "Kashif Mehmood"),
        ("C9-1015", "Nadia Parveen"),
        ("C9-1016", "Rizwan Akram"),
        ("C9-1017", "Waqas Mirza"),
        ("C9-1018", "Zainab Baig"),
    ]

    # Per-student ability profiles (base percentage for each student)
    abilities = rng.uniform(55, 95, len(student_names))

    # Assign elective: first 10 students -> Biology, rest -> Computer
    # (students can't have both simultaneously)
    student_elective = {}
    for i, (sid, name) in enumerate(student_names):
        student_elective[sid] = "Biology" if i < 10 else "Computer"

    conn = _get_connection()
    cursor = conn.cursor()
    results = {}

    for exam_type in EXAM_TYPES:
        subject_config = get_subject_config(9, exam_type)
        count = 0

        for i, (sid, name) in enumerate(student_names):
            # Upsert student
            cursor.execute("""
                INSERT INTO students (student_id, name, class_num)
                VALUES (?, ?, ?)
                ON CONFLICT(student_id) DO UPDATE SET name=excluded.name
            """, (sid, name, 9))

            base = abilities[i]
            elective = student_elective[sid]

            # Generate marks per subject with variation
            for subject, max_mark in subject_config.items():
                # Skip the elective they DON'T have
                if subject == "Biology" and elective != "Biology":
                    continue
                if subject == "Computer" and elective != "Computer":
                    continue

                # Add subject-specific variation
                variation = rng.normal(0, 12)
                pct = np.clip(base + variation, 25, 100)
                obtained = round(pct / 100 * max_mark)
                obtained = min(obtained, max_mark)
                obtained = max(obtained, 0)

                cursor.execute("""
                    INSERT INTO exam_marks (student_id, class_num, exam_type,
                                            subject, obtained_marks, max_marks)
                    VALUES (?, ?, ?, ?, ?, ?)
                    ON CONFLICT(student_id, class_num, exam_type, subject)
                    DO UPDATE SET obtained_marks=excluded.obtained_marks,
                                  max_marks=excluded.max_marks
                """, (sid, 9, exam_type, subject, float(obtained), float(max_mark)))

            # Behavior scores — realistic distribution
            # Only 2 students (indices 1,5) get perfect 10/10 punctuality
            # (complete attendance — very rare, ~2 per school)
            # Only 3 students get obedient >= 9
            if i == 1:  # Junaid Shah — perfect discipline + attendance
                obedient = 10
                punctual = 10
            elif i == 5:  # Fatima Noor — perfect attendance
                obedient = 8
                punctual = 10
            elif i == 2:  # Zara Mahmood — high discipline
                obedient = 9
                punctual = min(9, max(6, int(7 + rng.normal(0, 1))))
            else:
                # Most students: 5-8 range, realistic
                obedient = min(8, max(4, int(base / 13 + rng.normal(0, 1))))
                punctual = min(9, max(4, int(base / 13 + rng.normal(0, 0.8))))

            cursor.execute("""
                INSERT INTO behavior_scores (student_id, class_num, exam_type,
                                              obedient, punctual)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(student_id, class_num, exam_type)
                DO UPDATE SET obedient=excluded.obedient, punctual=excluded.punctual
            """, (sid, 9, exam_type, obedient, punctual))

            count += 1

        results[f"class_9_{exam_type}"] = count

    conn.commit()
    conn.close()
    return results
