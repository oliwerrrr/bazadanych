import csv
import os

def load_csv(filename):
    data = []
    with open(filename, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=';')
        headers = next(reader)  # skip header
        for row in reader:
            data.append(row)
    print(f"Wczytano {len(data)} rekordów z {filename}")
    return headers, data

def save_csv(filename, headers, data):
    with open(filename, 'w', newline='') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(headers)
        writer.writerows(data)
    print(f"Zapisano {len(data)} rekordów do {filename}")

def verify_and_fix():
    print("\n=== ROZPOCZYNAM WERYFIKACJĘ I NAPRAWĘ DANYCH ===\n")
    
    # Wczytaj wszystkie potrzebne pliki
    print("1. Wczytywanie danych źródłowych:")
    _, students = load_csv('hogwarts_data/students.csv')
    _, subjects = load_csv('hogwarts_data/subjects.csv')
    student_subjects_headers, student_subjects = load_csv('hogwarts_data/students_subjects.csv')
    grades_headers, grades = load_csv('hogwarts_data/grades.csv')
    _, teachers = load_csv('hogwarts_data/teachers.csv')

    print("\n2. Analiza dostępnych ID:")
    # Zbierz wszystkie dostępne ID
    student_ids = set(row[0] for row in students)
    subject_ids = set(row[0] for row in subjects)
    teacher_ids = set(row[0] for row in teachers)

    print(f"- Znaleziono {len(student_ids)} unikalnych ID studentów")
    print(f"- Znaleziono {len(subject_ids)} unikalnych ID przedmiotów")
    print(f"- Znaleziono {len(teacher_ids)} unikalnych ID nauczycieli")

    print("\n3. Weryfikacja powiązań student-przedmiot:")
    # Weryfikuj i napraw student_subjects
    valid_student_subjects = []
    invalid_count = 0
    total_count = len(student_subjects)
    
    for row in student_subjects:
        student_id, subject_id = row
        if student_id in student_ids and subject_id in subject_ids:
            valid_student_subjects.append(row)
        else:
            invalid_count += 1
            if invalid_count <= 5:  # Pokaż pierwsze 5 błędnych rekordów
                print(f"- Znaleziono nieprawidłowe powiązanie: student_id={student_id}, subject_id={subject_id}")

    print(f"- Przeanalizowano łącznie: {total_count} powiązań")
    print(f"- Zaakceptowano: {len(valid_student_subjects)} powiązań")
    print(f"- Usunięto: {invalid_count} nieprawidłowych powiązań")
    print(f"- Procent poprawnych: {(len(valid_student_subjects)/total_count*100):.2f}%")

    print("\n4. Weryfikacja ocen:")
    # Weryfikuj i napraw grades
    valid_grades = []
    invalid_count = 0
    total_grades = len(grades)
    valid_student_subjects_set = {(row[0], row[1]) for row in valid_student_subjects}

    for row in grades:
        grade_id, value, award_date, student_id, subject_id, teacher_id = row
        if (student_id in student_ids and 
            subject_id in subject_ids and 
            teacher_id in teacher_ids and
            (student_id, subject_id) in valid_student_subjects_set):
            valid_grades.append(row)
        else:
            invalid_count += 1
            if invalid_count <= 5:  # Pokaż pierwsze 5 błędnych rekordów
                print(f"- Znaleziono nieprawidłową ocenę: ID={grade_id}, student_id={student_id}, subject_id={subject_id}, teacher_id={teacher_id}")

    print(f"- Przeanalizowano łącznie: {total_grades} ocen")
    print(f"- Zaakceptowano: {len(valid_grades)} ocen")
    print(f"- Usunięto: {invalid_count} nieprawidłowych ocen")
    print(f"- Procent poprawnych: {(len(valid_grades)/total_grades*100):.2f}%")

    print("\n5. Zapisywanie poprawionych danych:")
    # Zapisz poprawione dane
    save_csv('hogwarts_data/students_subjects.csv', student_subjects_headers, valid_student_subjects)
    save_csv('hogwarts_data/grades.csv', grades_headers, valid_grades)

    print("\n=== ZAKOŃCZONO WERYFIKACJĘ I NAPRAWĘ DANYCH ===")

if __name__ == "__main__":
    verify_and_fix() 