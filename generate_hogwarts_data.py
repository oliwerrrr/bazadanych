import random
import time
import os
import csv
from datetime import datetime

# Funkcje debugowania
def debug_print(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data is not None:
        print(f"Data: {data}")

def verify_file_exists(filename):
    if not os.path.exists(f"hogwarts_data/{filename}"):
        debug_print(f"BŁĄD: Plik {filename} nie został utworzony!")
        return False
    return True

def count_rows_in_file(filename):
    if not verify_file_exists(filename):
        return 0
    with open(f"hogwarts_data/{filename}", "r", newline='', encoding='utf-8') as f:
        return sum(1 for row in f) - 1  # -1 dla nagłówka

def verify_foreign_keys(filename, foreign_key_col, reference_file, reference_col):
    if not verify_file_exists(filename) or not verify_file_exists(reference_file):
        return False
    
    # Wczytaj referencje
    references = set()
    with open(f"hogwarts_data/{reference_file}", "r", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            references.add(int(row[reference_col]))
    
    # Sprawdź klucze obce
    invalid_keys = set()
    with open(f"hogwarts_data/{filename}", "r", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            key = int(row[foreign_key_col])
            if key not in references:
                invalid_keys.add(key)
    
    if invalid_keys:
        debug_print(f"BŁĄD: Znaleziono nieprawidłowe klucze obce w {filename}: {invalid_keys}")
        return False
    return True

# Parametry generowania danych - możesz je dostosować
nTeachers = 100    # Stała liczba nauczycieli
nStudents = 10000  # Stała liczba uczniów
house_names = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]
house_symbols = ["Lion", "Snake", "Badger", "Eagle"]
grade_values = ["O", "E", "A", "P", "D", "T"]

debug_print("Rozpoczynam generowanie danych...")
debug_print(f"Parametry: {nTeachers} nauczycieli, {nStudents} uczniów")

# Format daty: YYYY-MM-DD
def random_date(start_date, end_date):
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    year = random.randint(start_year, end_year)
    month = random.randint(1, 12)
    
    if month in [4, 6, 9, 11]:
        day = random.randint(1, 30)
    elif month == 2:
        if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
            day = random.randint(1, 29)
        else:
            day = random.randint(1, 28)
    else:
        day = random.randint(1, 31)
    
    return f"{year:04d}-{month:02d}-{day:02d}"

# Wczytaj pliki z imionami i nazwiskami
try:
    with open("feminineNames.csv", "r", encoding="utf-8") as f:
        feminine_names = f.read().split(";")
        feminine_names = [name.strip() for name in feminine_names if name.strip()]
    
    with open("masculineNames.csv", "r", encoding="utf-8") as f:
        masculine_names = f.read().split(";")
        masculine_names = [name.strip() for name in masculine_names if name.strip()]
    
    with open("surnames.csv", "r", encoding="utf-8") as f:
        surnames = f.read().split(";")
        surnames = [surname.strip() for surname in surnames if surname.strip()]
    
    debug_print("Wczytano pliki z nazwami", {
        "imiona żeńskie": len(feminine_names),
        "imiona męskie": len(masculine_names),
        "nazwiska": len(surnames)
    })
except Exception as e:
    debug_print(f"BŁĄD podczas wczytywania plików z nazwami: {e}")
    feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
    masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
    surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]

# 1. Nauczyciele (Teachers) - generuj najpierw, bo są referencjonowani przez inne tabele
debug_print("Generuję nauczycieli...")
teacher_ids = list(range(nTeachers))
with open("hogwarts_data/teachers.csv", "w", newline='') as teachers_file:
    writer = csv.writer(teachers_file, delimiter=';')
    writer.writerow(["id", "name", "surname", "date_of_birth", "date_of_employment"])
    
    for i in range(nTeachers):
        birth_date = random_date("1950-01-01", "1990-01-01")
        min_employment_year = int(birth_date.split('-')[0]) + 23
        min_employment_date = f"{min_employment_year}-01-01"
        employment_date = random_date(min_employment_date, "2024-09-01")
        
        gender = random.choice(['M', 'F'])
        name = random.choice(feminine_names if gender == 'F' else masculine_names)
        writer.writerow([i, name, random.choice(surnames), birth_date, employment_date])

debug_print(f"Wygenerowano {count_rows_in_file('teachers.csv')} nauczycieli")

# 2. Domy (Houses) - używają teacher_ids
debug_print("Generuję domy...")
house_ids = list(range(4))
with open("hogwarts_data/houses.csv", "w", newline='') as houses_file:
    writer = csv.writer(houses_file, delimiter=';')
    writer.writerow(["id", "name", "symbol", "location", "teacher_id"])
    for i in range(4):
        location = f"{house_names[i]} Common Room"
        teacher_id = random.choice(teacher_ids)
        writer.writerow([i, house_names[i], house_symbols[i], location, teacher_id])

debug_print(f"Wygenerowano {count_rows_in_file('houses.csv')} domów")
verify_foreign_keys('houses.csv', 'teacher_id', 'teachers.csv', 'id')

# 3. Dormitoria (Dormitories) - używają house_ids
debug_print("Generuję dormitoria...")
dormitory_ids = []
with open("hogwarts_data/dormitories.csv", "w", newline='') as dormitories_file:
    writer = csv.writer(dormitories_file, delimiter=';')
    writer.writerow(["id", "gender", "room_number", "house_id"])
    
    dormitory_id = 0
    for house_id in range(4):
        for gender in ['M', 'F']:
            for year in range(1, 8):
                num_rooms = random.randint(1, 3)
                for room in range(num_rooms):
                    room_number = (year * 100) + room
                    writer.writerow([dormitory_id, gender, room_number, house_id])
                    dormitory_ids.append(dormitory_id)
                    dormitory_id += 1

debug_print(f"Wygenerowano {count_rows_in_file('dormitories.csv')} dormitoriów")
verify_foreign_keys('dormitories.csv', 'house_id', 'houses.csv', 'id')

# 4. Przedmioty (Subjects) - używają teacher_ids
debug_print("Generuję przedmioty...")
subject_ids = []
hogwarts_subjects = [
    ["Transfiguration", 1, 7],
    ["Charms", 1, 7],
    ["Potions", 1, 7],
    ["History of Magic", 1, 7],
    ["Defence Against the Dark Arts", 1, 7],
    ["Astronomy", 1, 7],
    ["Herbology", 1, 7],
    ["Flying", 1, 1],
    ["Muggle Studies", 3, 5],
    ["Divination", 3, 5],
    ["Ancient Runes", 3, 5],
    ["Care of Magical Creatures", 3, 5],
    ["Arithmancy", 3, 5],
    ["Alchemy", 6, 2],
    ["Apparition", 6, 1]
]

with open("hogwarts_data/subjects.csv", "w", newline='') as subjects_file:
    writer = csv.writer(subjects_file, delimiter=';')
    writer.writerow(["id", "name", "classroom", "year", "teacher_id"])
    
    subject_id = 0
    for subject_info in hogwarts_subjects:
        name, first_year, duration = subject_info
        
        if duration == 1:
            classroom = random.randint(1, 50)
            teacher_id = random.choice(teacher_ids)
            writer.writerow([subject_id, name, classroom, first_year, teacher_id])
            subject_ids.append(subject_id)
            subject_id += 1
        else:
            for year_offset in range(duration):
                classroom = random.randint(1, 50)
                teacher_id = random.choice(teacher_ids)
                current_year = first_year + year_offset
                subject_name = f"{name} Year {current_year}"
                writer.writerow([subject_id, subject_name, classroom, current_year, teacher_id])
                subject_ids.append(subject_id)
                subject_id += 1

debug_print(f"Wygenerowano {count_rows_in_file('subjects.csv')} przedmiotów")
verify_foreign_keys('subjects.csv', 'teacher_id', 'teachers.csv', 'id')

# 5. Uczniowie (Students) - używają house_ids i dormitory_ids
debug_print("Generuję uczniów...")
student_ids = list(range(nStudents))
with open("hogwarts_data/students.csv", "w", newline='') as students_file:
    writer = csv.writer(students_file, delimiter=';')
    writer.writerow(["id", "name", "surname", "gender", "date_of_birth", "year", "hogsmeade_consent", "house_id", "dormitory_id"])
    
    for i in range(nStudents):
        birth_date = random_date("2007-01-01", "2013-12-31")
        birth_year = int(birth_date.split('-')[0])
        year = 2024 - birth_year - 10
        
        gender = random.choice(['M', 'F'])
        name = random.choice(feminine_names if gender == 'F' else masculine_names)
        
        consent = 0
        if year >= 3:
            consent = 1 if random.random() > 0.05 else 0
        
        house_id = random.choice(house_ids)
        
        # Znajdź odpowiednie dormitorium
        available_dorms = [d for d in dormitory_ids if d % 2 == (0 if gender == 'M' else 1)]
        dormitory_id = random.choice(available_dorms) if available_dorms else None
        
        writer.writerow([i, name, random.choice(surnames), gender, birth_date, year, consent, house_id, dormitory_id])

debug_print(f"Wygenerowano {count_rows_in_file('students.csv')} uczniów")
verify_foreign_keys('students.csv', 'house_id', 'houses.csv', 'id')
verify_foreign_keys('students.csv', 'dormitory_id', 'dormitories.csv', 'id')

# 6. Przedmioty uczniów (Students_Subjects)
debug_print("Generuję przypisania przedmiotów do uczniów...")

# Najpierw wczytajmy wszystkie potrzebne dane do pamięci
debug_print("Wczytuję dane o uczniach i przedmiotach...")
students_data = {}
subjects_data = {}

with open("hogwarts_data/students.csv", "r", newline='') as students_file:
    reader = csv.DictReader(students_file, delimiter=';')
    for row in reader:
        students_data[int(row['id'])] = int(row['year'])

with open("hogwarts_data/subjects.csv", "r", newline='') as subjects_file:
    reader = csv.DictReader(subjects_file, delimiter=';')
    for row in reader:
        subjects_data[int(row['id'])] = {
            'year': int(row['year']),
            'name': row['name']
        }

debug_print(f"Wczytano dane o {len(students_data)} uczniach i {len(subjects_data)} przedmiotach")

student_subject_pairs = set()
with open("hogwarts_data/students_subjects.csv", "w", newline='') as students_subjects_file:
    writer = csv.writer(students_subjects_file, delimiter=';')
    writer.writerow(["student_id", "subject_id"])
    
    total_students = len(student_ids)
    for i, student_id in enumerate(student_ids, 1):
        if i % 1000 == 0:  # Pokazuj postęp co 1000 uczniów
            debug_print(f"Przetworzono {i}/{total_students} uczniów")
        
        year = students_data[student_id]
        
        # Przypisz przedmioty dla danego roku
        for subject_id, subject_info in subjects_data.items():
            if subject_info['year'] == year:
                if year >= 3 and "Year" not in subject_info['name']:
                    if random.random() > 0.7:
                        continue
                student_subject_pairs.add((student_id, subject_id))
                writer.writerow([student_id, subject_id])

debug_print(f"Wygenerowano {count_rows_in_file('students_subjects.csv')} przypisań przedmiotów do uczniów")
verify_foreign_keys('students_subjects.csv', 'student_id', 'students.csv', 'id')
verify_foreign_keys('students_subjects.csv', 'subject_id', 'subjects.csv', 'id')

# 7. Oceny (Grades)
debug_print("Generuję oceny...")

# Najpierw wczytajmy dane o nauczycielach przedmiotów do pamięci
debug_print("Wczytuję dane o nauczycielach przedmiotów...")
subject_teachers = {}
with open("hogwarts_data/subjects.csv", "r", newline='') as subjects_file:
    reader = csv.DictReader(subjects_file, delimiter=';')
    for row in reader:
        subject_teachers[int(row['id'])] = int(row['teacher_id'])

debug_print(f"Wczytano dane o nauczycielach dla {len(subject_teachers)} przedmiotów")

# Generuj oceny
with open("hogwarts_data/grades.csv", "w", newline='') as grades_file:
    writer = csv.writer(grades_file, delimiter=';')
    writer.writerow(["id", "value", "award_date", "student_id", "subject_id", "teacher_id"])
    
    grade_id = 0
    total_pairs = len(student_subject_pairs)
    
    for i, (student_id, subject_id) in enumerate(student_subject_pairs, 1):
        if i % 10000 == 0:  # Pokazuj postęp co 10000 par
            debug_print(f"Przetworzono {i}/{total_pairs} par uczeń-przedmiot")
        
        num_grades = random.randint(2, 5)
        teacher_id = subject_teachers[subject_id]
        
        for _ in range(num_grades):
            value = random.choice(grade_values)
            award_date = random_date("2023-09-01", "2024-06-30")
            writer.writerow([grade_id, value, award_date, student_id, subject_id, teacher_id])
            grade_id += 1

debug_print(f"Wygenerowano {count_rows_in_file('grades.csv')} ocen")
verify_foreign_keys('grades.csv', 'student_id', 'students.csv', 'id')
verify_foreign_keys('grades.csv', 'subject_id', 'subjects.csv', 'id')
verify_foreign_keys('grades.csv', 'teacher_id', 'teachers.csv', 'id')

# 8. Punkty (Points)
debug_print("Generuję punkty...")
with open("hogwarts_data/points.csv", "w", newline='') as points_file:
    writer = csv.writer(points_file, delimiter=';')
    writer.writerow(["id", "value", "description", "award_date", "student_id", "teacher_id"])
    
    points_id = 0
    for _ in range(nStudents * 3):
        student_id = random.choice(student_ids)
        teacher_id = random.choice(teacher_ids)
        value = random.randint(-50, 50)
        
        if value > 0:
            descriptions = [
                "Excellent classwork", 
                "Helping another student", 
                "Answering correctly in class",
                "Outstanding spell performance",
                "Bravery in difficult situation"
            ]
        else:
            descriptions = [
                "Breaking school rules",
                "Being late to class",
                "Disrespecting a teacher",
                "Being out after curfew",
                "Using magic in corridors"
            ]
        
        description = random.choice(descriptions)
        award_date = random_date("2023-09-01", "2024-06-30")
        
        writer.writerow([points_id, value, description, award_date, student_id, teacher_id])
        points_id += 1

debug_print(f"Wygenerowano {count_rows_in_file('points.csv')} punktów")
verify_foreign_keys('points.csv', 'student_id', 'students.csv', 'id')
verify_foreign_keys('points.csv', 'teacher_id', 'teachers.csv', 'id')

# 9. Drużyny Quidditcha (Quidditch_Team_Members)
debug_print("Generuję członków drużyn Quidditcha...")
with open("hogwarts_data/quidditch_team_members.csv", "w", newline='') as quidditch_file:
    writer = csv.writer(quidditch_file, delimiter=';')
    writer.writerow(["id", "position", "is_captain", "student_id"])
    
    quidditch_id = 0
    positions = ["Seeker", "Keeper", "Chaser", "Beater"]
    
    for house_id in range(4):
        # Wybierz kapitana
        potential_captains = [s for s in student_ids if random.randint(0, 3) == house_id and random.randint(1, 7) >= 3]
        if potential_captains:
            captain_student = random.choice(potential_captains)
            writer.writerow([quidditch_id, random.choice(positions), 1, captain_student])
            quidditch_id += 1
        
        # Pozostali członkowie drużyny
        team_size = random.randint(6, 10)
        team_members = set()
        if 'captain_student' in locals():
            team_members.add(captain_student)
            
        while len(team_members) < team_size:
            student_id = random.choice(student_ids)
            if student_id not in team_members:
                team_members.add(student_id)
                writer.writerow([quidditch_id, random.choice(positions), 0, student_id])
                quidditch_id += 1

debug_print(f"Wygenerowano {count_rows_in_file('quidditch_team_members.csv')} członków drużyn Quidditcha")
verify_foreign_keys('quidditch_team_members.csv', 'student_id', 'students.csv', 'id')

# Podsumowanie
debug_print("\nPODSUMOWANIE GENEROWANIA DANYCH:")
debug_print(f"Nauczyciele: {count_rows_in_file('teachers.csv')}")
debug_print(f"Domy: {count_rows_in_file('houses.csv')}")
debug_print(f"Dormitoria: {count_rows_in_file('dormitories.csv')}")
debug_print(f"Przedmioty: {count_rows_in_file('subjects.csv')}")
debug_print(f"Uczniowie: {count_rows_in_file('students.csv')}")
debug_print(f"Przypisania przedmiotów: {count_rows_in_file('students_subjects.csv')}")
debug_print(f"Oceny: {count_rows_in_file('grades.csv')}")
debug_print(f"Punkty: {count_rows_in_file('points.csv')}")
debug_print(f"Członkowie drużyn Quidditcha: {count_rows_in_file('quidditch_team_members.csv')}")

debug_print("\nWszystkie dane zostały wygenerowane i zweryfikowane.")