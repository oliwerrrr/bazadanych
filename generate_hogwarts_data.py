import random
import time
import os
import csv

# Parametry generowania danych - możesz je dostosować
nTeachers = random.randrange(90, 110)    # Około 100 nauczycieli
nStudents = random.randrange(9000, 11000)  # Około 1000 uczniów
house_names = ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"]
house_symbols = ["Lion", "Snake", "Badger", "Eagle"]
grade_values = ["O", "E", "A", "P", "D", "T"]  # Oceny w Hogwarts: Outstanding, Exceeds Expectations, Acceptable, Poor, Dreadful, Troll

# Format daty: YYYY-MM-DD
def random_date(start_date, end_date):
    start_year = int(start_date.split('-')[0])
    end_year = int(end_date.split('-')[0])
    
    # Generuj losowy rok
    year = random.randint(start_year, end_year)
    # Generuj losowy miesiąc
    month = random.randint(1, 12)
    # Generuj losowy dzień
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
    
    # W przypadku braku danych, użyj przykładowych
    if not feminine_names:
        feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
    if not masculine_names:
        masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
    if not surnames:
        surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
        
    names = feminine_names + masculine_names
except Exception as e:
    print(f"Błąd podczas wczytywania plików z nazwami: {e}")
    # Domyślne imiona i nazwiska w przypadku błędu
    feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
    masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
    surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
    names = feminine_names + masculine_names

# Generowanie tabel

# 1. Domy (Houses)
with open("hogwarts_data/houses.csv", "w", newline='') as houses_file:
    writer = csv.writer(houses_file, delimiter=';')
    writer.writerow(["id", "name", "symbol", "location", "teacher_id"])
    for i in range(4):
        location = f"{house_names[i]} Common Room"
        teacher_id = random.randint(0, nTeachers-1)
        writer.writerow([i, house_names[i], house_symbols[i], location, teacher_id])

# 2. Dormitoria (Dormitories)
with open("hogwarts_data/dormitories.csv", "w", newline='') as dormitories_file:
    writer = csv.writer(dormitories_file, delimiter=';')
    writer.writerow(["id", "gender", "room_number", "house_id"])
    
    dormitory_id = 0
    for house_id in range(4):
        for gender in ['M', 'F']:
            for year in range(1, 8):  # 7 lat nauki
                num_rooms = random.randint(1, 3)  # 1-3 pokoje na rok na płeć na dom
                for room in range(num_rooms):
                    room_number = (year * 100) + room
                    writer.writerow([dormitory_id, gender, room_number, house_id])
                    dormitory_id += 1

# 3. Nauczyciele (Teachers)
with open("hogwarts_data/teachers.csv", "w", newline='') as teachers_file:
    writer = csv.writer(teachers_file, delimiter=';')
    writer.writerow(["id", "name", "surname", "date_of_birth", "date_of_employment"])
    
    for i in range(nTeachers):
        birth_date = random_date("1950-01-01", "1990-01-01")
        # Data zatrudnienia najwcześniej 23 lata po urodzeniu
        min_employment_year = int(birth_date.split('-')[0]) + 23
        min_employment_date = f"{min_employment_year}-01-01"
        employment_date = random_date(min_employment_date, "2024-09-01")
        
        gender = random.choice(['M', 'F'])
        if gender == 'F':
            name = random.choice(feminine_names)
        else:
            name = random.choice(masculine_names)
            
        writer.writerow([i, name, random.choice(surnames), birth_date, employment_date])

# 4. Przedmioty (Subjects)
# Lista typowych przedmiotów w Hogwarts
hogwarts_subjects = [
    # przedmiot, rok rozpoczęcia, czas trwania (lat)
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
            teacher_id = random.randint(0, nTeachers-1)
            writer.writerow([subject_id, name, classroom, first_year, teacher_id])
            subject_id += 1
        else:
            for year_offset in range(duration):
                classroom = random.randint(1, 50)
                teacher_id = random.randint(0, nTeachers-1)
                current_year = first_year + year_offset
                subject_name = f"{name} Year {current_year}"
                writer.writerow([subject_id, subject_name, classroom, current_year, teacher_id])
                subject_id += 1

    nSubjects = subject_id

# 5. Uczniowie (Students)
dormitories_by_house_and_gender = {}

# Załaduj identyfikatory dormitoriów dla każdego domu i płci
with open("hogwarts_data/dormitories.csv", "r", newline='') as dormitories_file:
    reader = csv.reader(dormitories_file, delimiter=';')
    next(reader)  # Pomiń nagłówek
    for row in reader:
        dorm_id, gender, room_number, house_id = row
        year = int(room_number) // 100
        key = (int(house_id), gender, year)
        if key not in dormitories_by_house_and_gender:
            dormitories_by_house_and_gender[key] = []
        dormitories_by_house_and_gender[key].append(int(dorm_id))

with open("hogwarts_data/students.csv", "w", newline='') as students_file:
    writer = csv.writer(students_file, delimiter=';')
    writer.writerow(["id", "name", "surname", "gender", "date_of_birth", "year", "hogsmeade_consent", "house_id", "dormitory_id"])
    
    for i in range(nStudents):
        # Rok urodzenia determinuje rok nauki
        birth_date = random_date("2007-01-01", "2013-12-31")
        birth_year = int(birth_date.split('-')[0])
        year = 2024 - birth_year - 10  # Uczniowie zaczynają w wieku 11 lat
        
        gender = random.choice(['M', 'F'])
        if gender == 'F':
            name = random.choice(feminine_names)
        else:
            name = random.choice(masculine_names)
        
        # Zgoda na wyjścia do Hogsmeade (od 3 roku)
        consent = 0
        if year >= 3:
            consent = 1 if random.random() > 0.05 else 0
        
        house_id = random.randint(0, 3)
        
        # Przypisanie do dormitorium
        dormitory_id = None
        key = (house_id, gender, year)
        if key in dormitories_by_house_and_gender and dormitories_by_house_and_gender[key]:
            dormitory_id = random.choice(dormitories_by_house_and_gender[key])
        else:
            # Jeśli nie znaleziono odpowiedniego dormitorium, przypisz NULL
            dormitory_id = "NULL"
        
        writer.writerow([i, name, random.choice(surnames), gender, birth_date, year, consent, house_id, dormitory_id])

# 6. Przedmioty uczniów (Students_Subjects)
with open("hogwarts_data/students_subjects.csv", "w", newline='') as students_subjects_file:
    writer = csv.writer(students_subjects_file, delimiter=';')
    writer.writerow(["student_id", "subject_id"])
    
    # Wczytaj przedmioty i ich lata
    subjects_by_year = {}
    subject_ids = set()  # Dodane: zbiór istniejących ID przedmiotów
    with open("hogwarts_data/subjects.csv", "r", newline='') as subjects_file:
        reader = csv.reader(subjects_file, delimiter=';')
        next(reader)  # Pomiń nagłówek
        for row in reader:
            subject_id, name, classroom, year, teacher_id = row
            subject_ids.add(int(subject_id))  # Dodane: zapisz ID przedmiotu
            year = int(year)
            if year not in subjects_by_year:
                subjects_by_year[year] = []
            subjects_by_year[year].append(int(subject_id))
    
    # Wczytaj uczniów i ich lata
    students_by_year = {}
    student_ids = set()  # Dodane: zbiór istniejących ID studentów
    with open("hogwarts_data/students.csv", "r", newline='') as students_file:
        reader = csv.reader(students_file, delimiter=';')
        next(reader)  # Pomiń nagłówek
        for row in reader:
            student_id, name, surname, gender, birth_date, year, consent, house_id, dormitory_id = row
            student_ids.add(int(student_id))  # Dodane: zapisz ID studenta
            year = int(year)
            if year not in students_by_year:
                students_by_year[year] = []
            students_by_year[year].append(int(student_id))

    # Zapisz wszystkie pary student-przedmiot do weryfikacji
    student_subject_pairs = set()
    
    # Przypisz uczniów do przedmiotów
    for year in range(1, 8):
        if year not in subjects_by_year or year not in students_by_year:
            continue
            
        for student_id in students_by_year[year]:
            # Obowiązkowe przedmioty (wszyscy uczniowie)
            for subject_id in subjects_by_year[year]:
                # Dla przedmiotów opcjonalnych (od 3 roku), tylko część uczniów je wybiera
                if year >= 3 and "Year" not in next((s for s in hogwarts_subjects if s[0] in subjects_by_year[year]), [""])[0]:
                    if random.random() > 0.7:  # 70% szans na wybór przedmiotu opcjonalnego
                        continue
                if student_id in student_ids and subject_id in subject_ids:  # Dodane: weryfikacja
                    student_subject_pairs.add((student_id, subject_id))
                    writer.writerow([student_id, subject_id])

# 7. Drużyny Quidditcha (Quidditch_Team_Members)
positions = ["Seeker", "Keeper", "Chaser", "Beater"]
with open("hogwarts_data/quidditch_team_members.csv", "w", newline='') as quidditch_file:
    writer = csv.writer(quidditch_file, delimiter=';')
    writer.writerow(["id", "position", "is_captain", "student_id"])
    
    quidditch_id = 0
    for house_id in range(4):
        # Wybierz kapitana
        captain_student = None
        potential_captains = [s for s in range(nStudents) if random.randint(0, 3) == house_id and random.randint(1, 7) >= 3]
        if potential_captains:
            captain_student = random.choice(potential_captains)
            writer.writerow([quidditch_id, random.choice(positions), 1, captain_student])
            quidditch_id += 1
        
        # Pozostali członkowie drużyny
        team_size = random.randint(6, 10)  # Różne rozmiary drużyn
        team_members = set()
        if captain_student:
            team_members.add(captain_student)
            
        while len(team_members) < team_size:
            student_id = random.randint(0, nStudents-1)
            if student_id not in team_members:
                team_members.add(student_id)
                is_captain = 0  # Już wybraliśmy kapitana
                writer.writerow([quidditch_id, random.choice(positions), is_captain, student_id])
                quidditch_id += 1

# 8. Punkty (Points)
with open("hogwarts_data/points.csv", "w", newline='') as points_file:
    writer = csv.writer(points_file, delimiter=';')
    writer.writerow(["id", "value", "description", "award_date", "student_id", "teacher_id"])
    
    points_id = 0
    # Generuj losowe przyznane punkty
    for _ in range(nStudents * 3):  # Średnio 3 przyznania punktów na ucznia
        student_id = random.randint(0, nStudents-1)
        teacher_id = random.randint(0, nTeachers-1)
        value = random.randint(-50, 50)  # Można też odejmować punkty
        
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

# 9. Oceny (Grades)
with open("hogwarts_data/grades.csv", "w", newline='') as grades_file:
    writer = csv.writer(grades_file, delimiter=';')
    writer.writerow(["id", "value", "award_date", "student_id", "subject_id", "teacher_id"])
    
    grade_id = 0
    # Używamy wcześniej utworzonego zbioru par student-przedmiot
    for student_id, subject_id in student_subject_pairs:
        # Każdy uczeń otrzymuje 2-5 ocen z każdego przedmiotu
        num_grades = random.randint(2, 5)
        
        for _ in range(num_grades):
            value = random.choice(grade_values)
            award_date = random_date("2023-09-01", "2024-06-30")
            
            # Znajdź nauczyciela przypisanego do przedmiotu
            teacher_id = None
            with open("hogwarts_data/subjects.csv", "r", newline='') as subjects_file:
                reader = csv.reader(subjects_file, delimiter=';')
                next(reader)  # Pomiń nagłówek
                for row in reader:
                    if int(row[0]) == subject_id:
                        teacher_id = int(row[4])
                        break
            
            if teacher_id is None:
                continue  # Pomiń ocenę jeśli nie znaleziono nauczyciela
                
            writer.writerow([grade_id, value, award_date, student_id, subject_id, teacher_id])
            grade_id += 1

print(f"Wygenerowano dane dla {nStudents} uczniów, {nTeachers} nauczycieli i {nSubjects} przedmiotów.")
print("Pliki CSV zostały utworzone.")