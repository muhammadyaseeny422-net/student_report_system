"""
certificate_generator.py - Generates premium diploma-style PDF certificates.

Design: Formal diploma layout inspired by high school diploma certificates.
  - Dark navy triangular corner decorations
  - Clean white center with navy inner border frame
  - School logo centered at top
  - School name in navy below logo
  - Certificate title in gold/amber
  - Student name large and elegant
  - Body text centered
  - Achievement badge beautifully integrated in bottom-right
  - Signature lines at bottom

Certificate Types (all rare/exclusive):
  1. Academic Excellence  - >= 90% in ALL subjects
  2. Subject Topper       - Single highest scorer per subject
  3. Discipline Award     - Only for 10/10 obedient score
  4. Complete Attendance   - Only for 10/10 punctual score
  5. Position Holder       - 1st, 2nd, 3rd position in class
"""

import os
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from config import (get_certificate_dir, SUBJECT_TITLES, SPECIAL_TITLES,
                    POSITION_TITLES, SESSION_YEAR, SCHOOL_NAME,
                    BADGE_ASSETS_DIR, SUBJECT_BADGE_FILES,
                    POSITION_BADGE_FILES, SPECIAL_BADGE_FILES, GRADE_BADGE_FILE)


# ──────────────────────────────────────────────
#  COLOR CONSTANTS
# ──────────────────────────────────────────────

NAVY = "#1B1F5E"
GOLD = "#C8962E"
DARK_GOLD = "#A07A24"
LIGHT_GRAY = "#6B7280"
BLACK = "#1F2937"


# ──────────────────────────────────────────────
#  DIPLOMA DRAWING PRIMITIVES
# ──────────────────────────────────────────────

def _draw_diploma_frame(c, width, height):
    """
    Draw the diploma-style frame:
    - Navy triangular corners (top-left, top-right, bottom-left, bottom-right)
    - White center area
    - Navy inner border rectangle
    """
    # White background
    c.setFillColor(colors.white)
    c.rect(0, 0, width, height, fill=1, stroke=0)

    navy = colors.HexColor(NAVY)
    c.setFillColor(navy)

    # Top-left triangle
    p = c.beginPath()
    p.moveTo(0, height)
    p.lineTo(140, height)
    p.lineTo(0, height - 140)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Top-right triangle
    p = c.beginPath()
    p.moveTo(width, height)
    p.lineTo(width - 140, height)
    p.lineTo(width, height - 140)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Bottom-left triangle
    p = c.beginPath()
    p.moveTo(0, 0)
    p.lineTo(140, 0)
    p.lineTo(0, 140)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Bottom-right triangle
    p = c.beginPath()
    p.moveTo(width, 0)
    p.lineTo(width - 140, 0)
    p.lineTo(width, 140)
    p.close()
    c.drawPath(p, fill=1, stroke=0)

    # Inner border rectangle (navy, thin)
    c.setStrokeColor(navy)
    c.setLineWidth(2)
    c.rect(50, 40, width - 100, height - 80, fill=0, stroke=1)

    # Second inner border (thinner, slightly inset)
    c.setLineWidth(0.5)
    c.rect(55, 45, width - 110, height - 90, fill=0, stroke=1)


def _draw_diploma_header(c, width, height):
    """Draw school logo and name centered at top."""
    # School logo — centered, prominent
    logo_path = os.path.join("assets", "images", "school_logo.png")
    if os.path.exists(logo_path):
        logo_size = 65
        c.drawImage(logo_path,
                     width / 2 - logo_size / 2, height - 135,
                     width=logo_size, height=logo_size,
                     preserveAspectRatio=True, mask='auto')

    # School name — navy, centered below logo
    c.setFillColor(colors.HexColor(NAVY))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 160, SCHOOL_NAME.upper())


def _draw_diploma_title(c, width, height, title):
    """Draw certificate title in gold."""
    c.setFillColor(colors.HexColor(GOLD))
    c.setFont("Helvetica-Bold", 30)
    c.drawCentredString(width / 2, height - 195, title.upper())


def _draw_diploma_subtitle(c, width, height, text):
    """Draw the 'This is to acknowledge that' text."""
    c.setFillColor(colors.HexColor(NAVY))
    c.setFont("Helvetica", 12)
    c.drawCentredString(width / 2, height - 225, text)


def _draw_diploma_student_name(c, width, height, name):
    """Draw the student name — elegant italic serif font."""
    c.setFillColor(colors.HexColor(BLACK))
    c.setFont("Times-BoldItalic", 34)
    c.drawCentredString(width / 2, height - 272, name.title())

    # Elegant underline
    name_w = c.stringWidth(name.title(), "Times-BoldItalic", 34)
    c.setStrokeColor(colors.HexColor(NAVY))
    c.setLineWidth(1.5)
    c.line((width - name_w) / 2 - 20, height - 282,
           (width + name_w) / 2 + 20, height - 282)


def _draw_diploma_body(c, width, height, lines):
    """Draw body text centered."""
    c.setFillColor(colors.HexColor(LIGHT_GRAY))
    c.setFont("Helvetica", 11)
    y = height - 320
    for line in lines:
        c.drawCentredString(width / 2, y, line)
        y -= 18


def _draw_diploma_award_label(c, width, height, label):
    """Draw the award type label in gold."""
    c.setFillColor(colors.HexColor(GOLD))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(width / 2, height - 375, label.upper())


def _draw_diploma_date(c, width, height):
    """Draw the session date in italic."""
    c.setFillColor(colors.HexColor(NAVY))
    c.setFont("Helvetica-Oblique", 11)
    c.drawCentredString(width / 2, height - 400, f"Academic Session {SESSION_YEAR}")


def _draw_diploma_badge(c, width, height, badge_path):
    """
    Draw the achievement badge beautifully integrated in the bottom-right.
    Uses PIL to create a circular mask with soft edge so the badge blends
    cleanly into the white certificate. Adds a subtle gold ring border.
    """
    if not badge_path or not os.path.exists(badge_path):
        return

    try:
        from PIL import Image, ImageDraw, ImageFilter
        import math

        # Open badge and resize to high quality
        img = Image.open(badge_path).convert("RGBA")
        badge_px = 500  # high quality render
        img = img.resize((badge_px, badge_px), Image.LANCZOS)

        # Create circular mask (smooth anti-aliased edge)
        mask = Image.new("L", (badge_px, badge_px), 0)
        draw = ImageDraw.Draw(mask)
        margin = 8
        draw.ellipse([margin, margin, badge_px - margin, badge_px - margin], fill=255)
        # Smooth the edge slightly
        mask = mask.filter(ImageFilter.GaussianBlur(2))

        # Apply mask — make areas outside circle transparent
        output = Image.new("RGBA", (badge_px, badge_px), (255, 255, 255, 0))
        output.paste(img, (0, 0), mask)

        # Add subtle gold ring border
        ring_draw = ImageDraw.Draw(output)
        ring_draw.ellipse(
            [margin + 2, margin + 2, badge_px - margin - 2, badge_px - margin - 2],
            outline=(200, 150, 46, 180), width=4
        )

        # Save to temp file
        temp_dir = os.path.join("media", "_temp")
        os.makedirs(temp_dir, exist_ok=True)
        temp_path = os.path.join(temp_dir, "badge_cert_" + os.path.basename(badge_path))
        output.save(temp_path, "PNG")

        # Draw on certificate — bottom-right, raised and enlarged
        badge_size = 140
        badge_x = width - 78 - badge_size
        badge_y = 65

        c.drawImage(temp_path, badge_x, badge_y,
                     width=badge_size, height=badge_size,
                     preserveAspectRatio=True, mask='auto')
    except Exception:
        pass


def _draw_diploma_footer(c, width, height):
    """Draw signature lines and labels."""
    sig_y = 95

    # Left signature
    c.setStrokeColor(colors.HexColor(NAVY))
    c.setLineWidth(0.8)
    c.line(120, sig_y, 300, sig_y)
    c.setFillColor(colors.HexColor(BLACK))
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(210, sig_y - 15, "Class Teacher")

    # Right signature (shifted left to accommodate badge)
    c.line(width / 2 - 20, sig_y, width / 2 + 160, sig_y)
    c.drawCentredString(width / 2 + 70, sig_y - 15, "Principal")

    # Footer text
    c.setFillColor(colors.HexColor(LIGHT_GRAY))
    c.setFont("Helvetica", 7)
    c.drawCentredString(width / 2 - 50, 50,
                         "This certificate was generated by the AI-Powered Academic Reporting System")


# ──────────────────────────────────────────────
#  BADGE PATH RESOLVER
# ──────────────────────────────────────────────

def _get_badge_for_cert(cert_type, subject=None, position=None):
    """Get the full-quality badge asset path for a certificate type."""
    if cert_type == "subject_topper" and subject:
        badge_file = SUBJECT_BADGE_FILES.get(subject)
        if badge_file:
            return os.path.join(BADGE_ASSETS_DIR, badge_file)
    elif cert_type == "academic":
        return os.path.join(BADGE_ASSETS_DIR, SPECIAL_BADGE_FILES["academic_excellence"])
    elif cert_type == "behavior":
        return os.path.join(BADGE_ASSETS_DIR, SPECIAL_BADGE_FILES["discipline"])
    elif cert_type == "punctuality":
        return os.path.join(BADGE_ASSETS_DIR, SPECIAL_BADGE_FILES["attendance"])
    elif cert_type == "position" and position:
        badge_file = POSITION_BADGE_FILES.get(position)
        if badge_file:
            return os.path.join(BADGE_ASSETS_DIR, badge_file)
    return None


# ──────────────────────────────────────────────
#  CERTIFICATE GENERATORS
# ──────────────────────────────────────────────

def _build_diploma(student, title, subtitle, body_lines, award_label,
                   badge_path, output_prefix, output_dir=None):
    """
    Build a diploma-style certificate with consistent design.
    """
    class_num = student["class_num"]
    exam_type = student.get("exam_type", "final")
    if output_dir is None:
        output_dir = get_certificate_dir(class_num, exam_type)
    os.makedirs(output_dir, exist_ok=True)

    student_id = student["student_id"]
    file_path = os.path.join(output_dir, f"{output_prefix}_{student_id}.pdf")

    width, height = landscape(letter)
    c = canvas.Canvas(file_path, pagesize=landscape(letter))

    _draw_diploma_frame(c, width, height)
    _draw_diploma_header(c, width, height)
    _draw_diploma_title(c, width, height, title)
    _draw_diploma_subtitle(c, width, height, subtitle)
    _draw_diploma_student_name(c, width, height, student["name"])

    _draw_diploma_body(c, width, height, body_lines)
    _draw_diploma_award_label(c, width, height, award_label)
    _draw_diploma_date(c, width, height)

    _draw_diploma_badge(c, width, height, badge_path)
    _draw_diploma_footer(c, width, height)

    c.save()
    return file_path


def generate_academic_certificate(student, output_dir=None):
    """Academic Excellence — >= 90% in ALL subjects."""
    for pct in student["subject_percentages"].values():
        if pct < 90:
            return None

    badge_path = _get_badge_for_cert("academic")

    return _build_diploma(
        student,
        title="Certificate of Excellence",
        subtitle="This is to acknowledge that",
        body_lines=[
            "has achieved a score of 90% or above in every subject,",
            f"demonstrating exceptional academic dedication in Class {student['class_num']}.",
        ],
        award_label=f"Academic Excellence  |  Overall: {student['percentage']:.1f}%",
        badge_path=badge_path,
        output_prefix="academic",
        output_dir=output_dir,
    )


def generate_subject_topper_certificate(student, subject, topper_info, output_dir=None):
    """Subject Topper — single highest scorer per subject."""
    title_text = SUBJECT_TITLES.get(subject, f"{subject} Topper")
    display_subject = subject.replace("_", " ")
    obtained = int(topper_info["marks"])
    max_mark = int(topper_info["max_marks"])
    pct = topper_info["percentage"]

    badge_path = _get_badge_for_cert("subject_topper", subject=subject)

    return _build_diploma(
        student,
        title="Certificate of Achievement",
        subtitle="This is to acknowledge that",
        body_lines=[
            f"has achieved the highest score in {display_subject} in the class,",
            "demonstrating exceptional understanding and mastery of the subject.",
        ],
        award_label=f"{title_text}  |  Score: {obtained}/{max_mark} ({pct:.1f}%)",
        badge_path=badge_path,
        output_prefix=f"topper_{subject.replace('/', '_')}",
        output_dir=output_dir,
    )


def generate_behavior_certificate(student, output_dir=None):
    """Discipline Award — only for perfect 10/10 obedient score."""
    badge_path = _get_badge_for_cert("behavior")

    return _build_diploma(
        student,
        title="Certificate of Distinction",
        subtitle="This is to acknowledge that",
        body_lines=[
            "has demonstrated consistently exemplary behavior and outstanding discipline,",
            "serving as a role model and upholding the core values of our institution.",
        ],
        award_label=f"{SPECIAL_TITLES['behavior']}  |  Score: {student['obedient']}/10",
        badge_path=badge_path,
        output_prefix="behavior",
        output_dir=output_dir,
    )


def generate_punctuality_certificate(student, output_dir=None):
    """Complete Attendance — only for perfect 10/10 punctual score."""
    badge_path = _get_badge_for_cert("punctuality")

    return _build_diploma(
        student,
        title="Certificate of Commitment",
        subtitle="This is to acknowledge that",
        body_lines=[
            "has maintained perfect attendance throughout the academic session,",
            "demonstrating exceptional reliability and unwavering dedication to learning.",
        ],
        award_label=f"{SPECIAL_TITLES['punctuality']}  |  Perfect Attendance",
        badge_path=badge_path,
        output_prefix="punctuality",
        output_dir=output_dir,
    )


def generate_position_certificate(student, position, position_info, output_dir=None):
    """Position Holder — 1st, 2nd, 3rd in class."""
    if position not in (1, 2, 3):
        return None

    title_map = {
        1: "Certificate of Honor",
        2: "Certificate of Merit",
        3: "Certificate of Recognition",
    }

    pos_title = POSITION_TITLES.get(position, f"Position {position}")
    pct = position_info["percentage"]
    total = int(position_info["total_marks"])
    max_total = int(position_info["max_marks"])

    badge_path = _get_badge_for_cert("position", position=position)

    return _build_diploma(
        student,
        title=title_map.get(position, "Certificate of Achievement"),
        subtitle="This is to acknowledge that",
        body_lines=[
            f"has demonstrated outstanding academic performance and secured",
            f"{pos_title} in Class {student['class_num']} with exceptional dedication.",
        ],
        award_label=f"{pos_title}  |  Score: {total}/{max_total} ({pct:.1f}%)",
        badge_path=badge_path,
        output_prefix=f"position_{position}",
        output_dir=output_dir,
    )
