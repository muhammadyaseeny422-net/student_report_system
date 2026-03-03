import pandas as pd

def get_grade_and_remark(percentage, obedient, punctual):
    if percentage >= 90:
        grade = "A+"
        base_remark = "Outstanding performance!"
    elif percentage >= 80:
        grade = "A"
        base_remark = "Excellent work!"
    elif percentage >= 70:
        grade = "B"
        base_remark = "Good effort, but room for improvement."
    else:
        grade = "C"
        base_remark = "Needs more attention to studies."
    
    # Add trait-based remarks
    if obedient == "Yes" and punctual == "Yes":
        trait_remark = " A very well-behaved and timely student."
    elif obedient == "Yes":
        trait_remark = " Well-behaved, but needs to improve punctuality."
    elif punctual == "Yes":
        trait_remark = " Punctual, but behavior could be improved."
    else:
        trait_remark = " Needs significant improvement in discipline and punctuality."
        
    return grade, base_remark + trait_remark

def process_marks(file_path):
    df = pd.read_excel(file_path)
    students_data = []

    subject_cols = [col for col in df.columns if '(' in col]
    total_max_marks = sum([float(col.split('(')[1].replace(')', '')) for col in subject_cols])
    
    for _, row in df.iterrows():
        student = {}
        student["name"] = row["Student Name"]
        
        # Extract marks
        marks = {}
        student_total_marks = 0
        subject_badges = []
        
        for col in subject_cols:
            sub_name = col.split('(')[0].strip()
            max_mark = float(col.split('(')[1].replace(')', ''))
            obtained = float(row[col])
            marks[col] = obtained
            student_total_marks += obtained
            
            # Subject percentage for badges
            sub_percent = (obtained / max_mark) * 100
            if sub_percent >= 90:
                subject_badges.append(f"{sub_name}_Genius.png")
            elif sub_percent > 85:
                subject_badges.append(f"{sub_name}_Expert.png")
            elif sub_percent >= 80:
                subject_badges.append(f"{sub_name}_Star.png")

        percentage = (student_total_marks / total_max_marks) * 100
        
        obedient = str(row.get("Obedient", "Yes"))
        punctual = str(row.get("Punctual", "Yes"))
        
        trait_badges = []
        if obedient.lower() == "yes":
            trait_badges.append("obedient.png")
        if punctual.lower() == "yes":
            trait_badges.append("punctual.png")
            
        # Restrict badges if overall percentage < 80% as requested
        if percentage < 80:
            subject_badges = []
            trait_badges = []
            
        grade, remarks = get_grade_and_remark(percentage, obedient, punctual)
        
        student["marks"] = marks
        student["total_marks"] = student_total_marks
        student["max_marks"] = total_max_marks
        student["percentage"] = percentage
        student["grade"] = grade
        student["remarks"] = remarks
        student["subject_badges"] = subject_badges
        student["trait_badges"] = trait_badges
        
        students_data.append(student)
        
    return students_data
