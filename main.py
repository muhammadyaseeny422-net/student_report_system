import os
from marks_processor import process_marks
from pdf_generator import generate_report_card

def main():
    data_file = "data/students_marks.xlsx"
    if not os.path.exists(data_file):
        print(f"Error: {data_file} not found. Please run setup_dummy_data.py first.")
        return
        
    print("Processing marks...")
    students = process_marks(data_file)
    
    os.makedirs("reports", exist_ok=True)
    
    print(f"Generating reports for {len(students)} students...")
    for student in students:
        generate_report_card(student)
        
    print("All reports generated successfully in the 'reports' folder.")

if __name__ == "__main__":
    main()
