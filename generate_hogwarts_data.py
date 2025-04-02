import random
import time
import os
import csv
import json
import signal
import sys
from datetime import datetime
from tqdm import tqdm

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')
CONFIG_FILE = os.path.join(BASE_DIR, 'hogwarts_config.json')
NAMES_DIR = os.path.join(BASE_DIR, 'names')

# Ensure directories exist
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(NAMES_DIR, exist_ok=True)

# Disable output buffering completely
os.environ['PYTHONUNBUFFERED'] = '1'
sys.stdout = open(sys.stdout.fileno(), mode=sys.stdout.mode, buffering=1)

# Global flag for stopping the process
stop_process = False

def signal_handler(signum, frame):
    global stop_process
    sys.stdout.write("\n[INFO] Stop signal received. Finishing current operation...\n")
    sys.stdout.flush()
    stop_process = True

# Register signal handler
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def load_config():
    try:
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        sys.stdout.write("ERROR: Configuration file hogwarts_config.json not found!\n")
        sys.stdout.write("Please run config_generator.py first to create the configuration.\n")
        sys.stdout.flush()
        exit(1)

# Load configuration
CONFIG = load_config()

# Debug functions
def debug_print(message, data=None):
    global stop_process
    if stop_process:
        return
    timestamp = datetime.now().strftime("%H:%M:%S")
    sys.stdout.write(f"[{timestamp}] {message}\n")
    sys.stdout.flush()
    if data is not None:
        sys.stdout.write(f"Data: {data}\n")
        sys.stdout.flush()

def check_stop():
    global stop_process
    if stop_process:
        debug_print("[INFO] Process stopped by user")
        sys.exit(0)

def verify_file_exists(filename):
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        debug_print(f"ERROR: File {filename} was not created!")
        return False
    return True

def count_rows_in_file(filename):
    if not verify_file_exists(filename):
        return 0
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "r", newline='', encoding='utf-8') as f:
        return sum(1 for row in f) - 1  # -1 for header

def verify_foreign_keys(filename, foreign_key_col, reference_file, reference_col):
    if not verify_file_exists(filename) or not verify_file_exists(reference_file):
        return False
    
    # Load references
    references = set()
    file_path = os.path.join(DATA_DIR, reference_file)
    with open(file_path, "r", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            references.add(int(row[reference_col]))
    
    # Check foreign keys
    invalid_keys = set()
    file_path = os.path.join(DATA_DIR, filename)
    with open(file_path, "r", newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            key = int(row[foreign_key_col])
            if key not in references:
                invalid_keys.add(key)
    
    if invalid_keys:
        debug_print(f"ERROR: Found invalid foreign keys in {filename}: {invalid_keys}")
        return False
    return True

# Date format: YYYY-MM-DD
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

def main():
    global stop_process
    try:
        debug_print("[>>>] Starting data generation...")
        debug_print("[INFO] Press Ctrl+C to stop the process")
        
        # Load name files
        try:
            with open(os.path.join(NAMES_DIR, "feminineNames.csv"), "r", encoding="utf-8") as f:
                feminine_names = f.read().split(";")
                feminine_names = [name.strip() for name in feminine_names if name.strip()]
            
            with open(os.path.join(NAMES_DIR, "masculineNames.csv"), "r", encoding="utf-8") as f:
                masculine_names = f.read().split(";")
                masculine_names = [name.strip() for name in masculine_names if name.strip()]
            
            with open(os.path.join(NAMES_DIR, "surnames.csv"), "r", encoding="utf-8") as f:
                surnames = f.read().split(";")
                surnames = [surname.strip() for surname in surnames if surname.strip()]
            
            debug_print("Name files loaded", {
                "feminine names": len(feminine_names),
                "masculine names": len(masculine_names),
                "surnames": len(surnames)
            })
        except Exception as e:
            debug_print(f"ERROR while loading name files: {e}")
            feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
            masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
            surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]

        # 1. Teachers
        check_stop()
        debug_print("Generating teachers...")
        teacher_ids = list(range(CONFIG['nTeachers']))
        with open(os.path.join(DATA_DIR, "teachers.csv"), "w", newline='') as teachers_file:
            writer = csv.writer(teachers_file, delimiter=';')
            writer.writerow(["id", "name", "surname", "date_of_birth", "date_of_employment"])
            
            for i in tqdm(range(CONFIG['nTeachers']), desc="Generating teachers", file=sys.stdout):
                if stop_process:
                    return
                birth_date = random_date(f"{CONFIG['min_teacher_birth_year']}-01-01", f"{CONFIG['max_teacher_birth_year']}-01-01")
                min_employment_year = int(birth_date.split('-')[0]) + 23
                min_employment_date = f"{min_employment_year}-01-01"
                employment_date = random_date(min_employment_date, "2024-09-01")
                
                gender = random.choice(['M', 'F'])
                name = random.choice(feminine_names if gender == 'F' else masculine_names)
                writer.writerow([i, name, random.choice(surnames), birth_date, employment_date])

        debug_print(f"Generated {count_rows_in_file('teachers.csv')} teachers")

        # 2. Houses - using teacher_ids
        check_stop()
        debug_print("Generating houses...")
        house_ids = list(range(4))
        with open(os.path.join(DATA_DIR, "houses.csv"), "w", newline='') as houses_file:
            writer = csv.writer(houses_file, delimiter=';')
            writer.writerow(["id", "name", "symbol", "location", "teacher_id"])
            for i in range(4):
                location = f"{CONFIG['house_names'][i]} Common Room"
                teacher_id = random.choice(teacher_ids)
                writer.writerow([i, CONFIG['house_names'][i], CONFIG['house_symbols'][i], location, teacher_id])

        debug_print(f"Generated {count_rows_in_file('houses.csv')} houses")
        verify_foreign_keys('houses.csv', 'teacher_id', 'teachers.csv', 'id')

        # 3. Dormitories - using house_ids
        check_stop()
        debug_print("Generating dormitories...")
        dormitory_ids = []
        with open(os.path.join(DATA_DIR, "dormitories.csv"), "w", newline='') as dormitories_file:
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

        debug_print(f"Generated {count_rows_in_file('dormitories.csv')} dormitories")
        verify_foreign_keys('dormitories.csv', 'house_id', 'houses.csv', 'id')

        # 4. Subjects - using teacher_ids
        check_stop()
        debug_print("Generating subjects...")
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

        with open(os.path.join(DATA_DIR, "subjects.csv"), "w", newline='', encoding='utf-8') as subjects_file:
            writer = csv.writer(subjects_file, delimiter=';')
            writer.writerow(["id", "name", "classroom", "year", "teacher_id"])
            
            subject_id = 0
            for subject_info in hogwarts_subjects:
                name, first_year, duration = subject_info
                
                if duration == 1:
                    classroom = random.randint(CONFIG['min_classroom'], CONFIG['max_classroom'])
                    teacher_id = random.choice(teacher_ids)
                    writer.writerow([subject_id, name, classroom, first_year, teacher_id])
                    subject_ids.append(subject_id)
                    subject_id += 1
                else:
                    for year_offset in range(duration):
                        classroom = random.randint(CONFIG['min_classroom'], CONFIG['max_classroom'])
                        teacher_id = random.choice(teacher_ids)
                        current_year = first_year + year_offset
                        subject_name = f"{name} Year {current_year}"
                        writer.writerow([subject_id, subject_name, classroom, current_year, teacher_id])
                        subject_ids.append(subject_id)
                        subject_id += 1

        # Check if file was created and contains data
        if not os.path.exists(os.path.join(DATA_DIR, "subjects.csv")):
            debug_print("ERROR: subjects.csv file was not created!")
            exit(1)

        with open(os.path.join(DATA_DIR, "subjects.csv"), "r", newline='', encoding='utf-8') as f:
            reader = csv.reader(f, delimiter=';')
            next(reader)  # Skip header
            subjects_count = sum(1 for row in reader)

        debug_print(f"Generated {subjects_count} subjects")
        if subjects_count == 0:
            debug_print("ERROR: No subjects were generated!")
            exit(1)

        verify_foreign_keys('subjects.csv', 'teacher_id', 'teachers.csv', 'id')

        # 5. Students - using house_ids and dormitory_ids
        check_stop()
        debug_print("Generating students...")
        student_ids = list(range(CONFIG['nStudents']))
        with open(os.path.join(DATA_DIR, "students.csv"), "w", newline='') as students_file:
            writer = csv.writer(students_file, delimiter=';')
            writer.writerow(["id", "name", "surname", "gender", "date_of_birth", "year", "hogsmeade_consent", "house_id", "dormitory_id"])
            
            for i in range(CONFIG['nStudents']):
                birth_date = random_date(f"{CONFIG['min_student_birth_year']}-01-01", f"{CONFIG['max_student_birth_year']}-12-31")
                birth_year = int(birth_date.split('-')[0])
                year = 2024 - birth_year - 10
                
                # Use configured gender distribution
                female_threshold = CONFIG['female_percentage'] / 100
                gender = 'F' if random.random() < female_threshold else 'M'
                name = random.choice(feminine_names if gender == 'F' else masculine_names)
                
                consent = 0
                if year >= 3:
                    consent = 1 if random.random() > 0.05 else 0
                
                house_id = random.choice(house_ids)
                
                # Find appropriate dormitory
                available_dorms = [d for d in dormitory_ids if d % 2 == (0 if gender == 'M' else 1)]
                dormitory_id = random.choice(available_dorms) if available_dorms else None
                
                writer.writerow([i, name, random.choice(surnames), gender, birth_date, year, consent, house_id, dormitory_id])

        debug_print(f"Generated {count_rows_in_file('students.csv')} students")
        verify_foreign_keys('students.csv', 'house_id', 'houses.csv', 'id')
        verify_foreign_keys('students.csv', 'dormitory_id', 'dormitories.csv', 'id')

        # 6. Student Subjects
        check_stop()
        debug_print("Generating student subject assignments...")

        # First load all needed data into memory
        check_stop()
        debug_print("Loading student and subject data...")
        students_data = {}
        subjects_data = {}

        with open(os.path.join(DATA_DIR, "students.csv"), "r", newline='') as students_file:
            reader = csv.DictReader(students_file, delimiter=';')
            for row in reader:
                students_data[int(row['id'])] = int(row['year'])

        with open(os.path.join(DATA_DIR, "subjects.csv"), "r", newline='') as subjects_file:
            reader = csv.DictReader(subjects_file, delimiter=';')
            for row in reader:
                subjects_data[int(row['id'])] = {
                    'year': int(row['year']),
                    'name': row['name']
                }

        debug_print(f"Loaded data for {len(students_data)} students and {len(subjects_data)} subjects")

        student_subject_pairs = set()
        with open(os.path.join(DATA_DIR, "students_subjects.csv"), "w", newline='') as students_subjects_file:
            writer = csv.writer(students_subjects_file, delimiter=';')
            writer.writerow(["student_id", "subject_id"])
            
            total_students = len(student_ids)
            for i, student_id in enumerate(student_ids, 1):
                if i % 1000 == 0:  # Show progress every 1000 students
                    debug_print(f"Processed {i}/{total_students} students")
                
                year = students_data[student_id]
                
                # Assign subjects for the given year
                for subject_id, subject_info in subjects_data.items():
                    if subject_info['year'] == year:
                        if year >= 3 and "Year" not in subject_info['name']:
                            if random.random() > 0.7:
                                continue
                        student_subject_pairs.add((student_id, subject_id))
                        writer.writerow([student_id, subject_id])

        debug_print(f"Generated {count_rows_in_file('students_subjects.csv')} subject assignments")
        verify_foreign_keys('students_subjects.csv', 'student_id', 'students.csv', 'id')
        verify_foreign_keys('students_subjects.csv', 'subject_id', 'subjects.csv', 'id')

        # 7. Grades
        check_stop()
        debug_print("Generating grades...")

        # First load subject teacher data into memory
        check_stop()
        debug_print("Loading subject teacher data...")
        subject_teachers = {}
        with open(os.path.join(DATA_DIR, "subjects.csv"), "r", newline='') as subjects_file:
            reader = csv.DictReader(subjects_file, delimiter=';')
            for row in reader:
                subject_teachers[int(row['id'])] = int(row['teacher_id'])

        debug_print(f"Loaded teacher data for {len(subject_teachers)} subjects")

        # Generate grades
        with open(os.path.join(DATA_DIR, "grades.csv"), "w", newline='') as grades_file:
            writer = csv.writer(grades_file, delimiter=';')
            writer.writerow(["id", "value", "award_date", "student_id", "subject_id", "teacher_id"])
            
            grade_id = 0
            total_pairs = len(student_subject_pairs)
            
            for i, (student_id, subject_id) in enumerate(student_subject_pairs, 1):
                if i % 10000 == 0:  # Show progress every 10000 pairs
                    debug_print(f"Processed {i}/{total_pairs} student-subject pairs")
                
                num_grades = random.randint(CONFIG['min_grades_per_subject'], CONFIG['max_grades_per_subject'])
                teacher_id = subject_teachers[subject_id]
                
                for _ in range(num_grades):
                    value = random.choice(CONFIG['grade_values'])
                    award_date = random_date("2023-09-01", "2024-06-30")
                    writer.writerow([grade_id, value, award_date, student_id, subject_id, teacher_id])
                    grade_id += 1

        debug_print(f"Generated {count_rows_in_file('grades.csv')} grades")
        verify_foreign_keys('grades.csv', 'student_id', 'students.csv', 'id')
        verify_foreign_keys('grades.csv', 'subject_id', 'subjects.csv', 'id')
        verify_foreign_keys('grades.csv', 'teacher_id', 'teachers.csv', 'id')

        # 8. Points
        check_stop()
        debug_print("Generating points...")
        with open(os.path.join(DATA_DIR, "points.csv"), "w", newline='') as points_file:
            writer = csv.writer(points_file, delimiter=';')
            writer.writerow(["id", "value", "description", "award_date", "student_id", "teacher_id"])
            
            points_id = 0
            for _ in range(CONFIG['nStudents'] * CONFIG['points_per_student']):
                student_id = random.choice(student_ids)
                teacher_id = random.choice(teacher_ids)
                value = random.randint(CONFIG['min_points'], CONFIG['max_points'])
                
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

        debug_print(f"Generated {count_rows_in_file('points.csv')} points")
        verify_foreign_keys('points.csv', 'student_id', 'students.csv', 'id')
        verify_foreign_keys('points.csv', 'teacher_id', 'teachers.csv', 'id')

        # 9. Quidditch Team Members
        check_stop()
        debug_print("Generating Quidditch team members...")
        with open(os.path.join(DATA_DIR, "quidditch_team_members.csv"), "w", newline='') as quidditch_file:
            writer = csv.writer(quidditch_file, delimiter=';')
            writer.writerow(["id", "position", "is_captain", "student_id"])
            
            quidditch_id = 0
            positions = ["Seeker", "Keeper", "Chaser", "Beater"]
            
            for house_id in range(4):
                # Choose captain
                potential_captains = [s for s in student_ids if random.randint(0, 3) == house_id and random.randint(1, 7) >= CONFIG['min_captain_year']]
                if potential_captains:
                    captain_student = random.choice(potential_captains)
                    writer.writerow([quidditch_id, random.choice(positions), 1, captain_student])
                    quidditch_id += 1
                
                # Other team members
                team_size = random.randint(CONFIG['min_team_size'], CONFIG['max_team_size'])
                team_members = set()
                if 'captain_student' in locals():
                    team_members.add(captain_student)
                    
                while len(team_members) < team_size:
                    student_id = random.choice(student_ids)
                    if student_id not in team_members:
                        team_members.add(student_id)
                        writer.writerow([quidditch_id, random.choice(positions), 0, student_id])
                        quidditch_id += 1

        debug_print(f"Generated {count_rows_in_file('quidditch_team_members.csv')} Quidditch team members")
        verify_foreign_keys('quidditch_team_members.csv', 'student_id', 'students.csv', 'id')

        # Summary
        check_stop()
        debug_print("\nDATA GENERATION SUMMARY:")
        debug_print(f"Teachers: {count_rows_in_file('teachers.csv')}")
        debug_print(f"Houses: {count_rows_in_file('houses.csv')}")
        debug_print(f"Dormitories: {count_rows_in_file('dormitories.csv')}")
        debug_print(f"Subjects: {count_rows_in_file('subjects.csv')}")
        debug_print(f"Students: {count_rows_in_file('students.csv')}")
        debug_print(f"Subject assignments: {count_rows_in_file('students_subjects.csv')}")
        debug_print(f"Grades: {count_rows_in_file('grades.csv')}")
        debug_print(f"Points: {count_rows_in_file('points.csv')}")
        debug_print(f"Quidditch team members: {count_rows_in_file('quidditch_team_members.csv')}")

        debug_print("\nAll data has been generated and verified.")

    except KeyboardInterrupt:
        debug_print("\n[INFO] Process interrupted by user")
        sys.exit(0)
    except Exception as e:
        debug_print(f"[ERROR] An error occurred: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()