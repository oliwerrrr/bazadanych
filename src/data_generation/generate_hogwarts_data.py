import random
import time
import os
import csv
import json
import signal
import sys
import numpy as np
from datetime import datetime, timedelta
from tqdm import tqdm
from scipy.stats import truncnorm

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'hogwarts_config.json')
NAMES_DIR = os.path.join(BASE_DIR, 'data', 'names')

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
        if not os.path.exists(CONFIG_FILE):
            sys.stdout.write(f"ERROR: Configuration file not found at {CONFIG_FILE}!\n")
            sys.stdout.write("Please run config_generator.py first to create the configuration.\n")
            sys.stdout.flush()
            exit(1)
            
        with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
            config = json.load(f)
            
        # Validate required fields
        required_fields = [
            'nTeachers', 'nStudents', 'female_percentage',
            'min_teacher_birth_year', 'max_teacher_birth_year',
            'min_student_birth_year', 'max_student_birth_year',
            'min_classroom', 'max_classroom',
            'grade_values', 'min_grades_per_subject', 'max_grades_per_subject',
            'min_points', 'max_points', 'pointsPerStudent',
            'min_team_size', 'max_team_size', 'min_captain_year',
            'house_names', 'house_symbols'
        ]
        
        missing_fields = [field for field in required_fields if field not in config]
        if missing_fields:
            sys.stdout.write(f"ERROR: Missing required fields in config: {', '.join(missing_fields)}\n")
            sys.stdout.write("Please regenerate the configuration using config_generator.py\n")
            sys.stdout.flush()
            exit(1)
            
        return config
            
    except json.JSONDecodeError as e:
        sys.stdout.write(f"ERROR: Invalid JSON in configuration file: {str(e)}\n")
        sys.stdout.write("Please regenerate the configuration using config_generator.py\n")
        sys.stdout.flush()
        exit(1)
    except Exception as e:
        sys.stdout.write(f"ERROR: Failed to load configuration: {str(e)}\n")
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
    try:
        file_path = os.path.join(DATA_DIR, filename)
        with open(file_path, "r", newline='', encoding='utf-8') as f:
            return sum(1 for row in f) - 1  # -1 for header
    except Exception as e:
        debug_print(f"ERROR: Failed to count rows in {filename}: {str(e)}")
        return 0

def verify_foreign_keys(filename, foreign_key_col, reference_file, reference_col):
    if not verify_file_exists(filename) or not verify_file_exists(reference_file):
        return False
    
    try:
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
    except Exception as e:
        debug_print(f"ERROR: Failed to verify foreign keys in {filename}: {str(e)}")
        return False

# Helper functions for number to words conversion
def number_to_words(n):
    """Convert a number to words (simple implementation for 0-10)"""
    words = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    if 0 <= n <= 10:
        return words[n]
    return str(n)

# Helper function for truncated normal distribution
def get_truncated_normal(mean=0, sd=1, low=0, upp=10):
    """Return a truncated normal distribution"""
    return truncnorm((low - mean) / sd, (upp - mean) / sd, loc=mean, scale=sd)

# Helper functions for points generation
def days():
    """Return a varied time description or empty string"""
    if random.random() > 0.3:
        n = random.randint(-3, 7)
        if n <= 0:
            return "Today "
        if n == 1:
            return "Yesterday "
        if n == 7:
            return "A week ago "
        return f"{number_to_words(n).capitalize()} days ago "
    return ""

# Vocabulary lists for generating varied descriptions
verbsShowed = ['demonstrated', 'showed', 'gave a demonstration of', 'expressed', 'answered the question']
verbsExplained = ['explained', 'discussed', 'illustrated', 'presented']
nounsTopic = ['topic', 'subject', 'problem', 'subject matter', 'concept', 'spell']
adjectives = ['','','','great', 'exceptional', 'extraordinary', 'prominent', 'appreciable', 'notable', 'noteworthy', 'outstanding']
nouns = ['knowledge', 'skills', 'passion', 'understanding', 'comprehension', 'mastery', 'capability', 'awareness', 'intuition']

verbsWas = ['was', 'proved to be', 'happened to be', 'remained', 'continued to be', 'started being']
adverbsNegative = ['','','','','', 'highly', 'very', 'slightly', 'surprisingly', "completely", "totally", "utterly", "highly", "entirely",
    "extremely", "remarkably", "particularly", "exceptionally",
    "incredibly", "overly", "excessively", "notoriously",
    "horribly", "ridiculously", "shockingly", "unbelievably",
    "wildly", "absurdly", "insanely"]
adjectivesNegative = [
    "impatient", "harsh", "rude", "dismissive", "condescending",
    "unfair", "inconsiderate", "insensitive", "arrogant",
    "strict", "cold", "indifferent", "apathetic", "unsupportive",
    "intolerant", "disrespectful", "critical", "demeaning",
    "hostile", "aggressive", "patronizing", "inflexible",
    "unapproachable", "manipulative", "negligent", "unhelpful"
]
adverbsPositive = [
    "very", "extremely", "incredibly", "exceptionally", "remarkably",
    "highly", "truly", "deeply", "especially", "hugely",
    "amazingly", "immensely", "profoundly", "outstandingly",
    "extraordinarily", "tremendously", "wonderfully", "notably",
    "genuinely", "wholeheartedly", "sincerely", "thoughtfully"
]
adjectivesPositive = [
    "patient", "kind", "understanding", "supportive", "encouraging",
    "respectful", "compassionate", "considerate", "fair", "attentive",
    "nurturing", "dedicated", "motivating", "thoughtful",
    "approachable", "friendly", "caring", "empathetic",
    "generous", "tolerant", "uplifting", "trustworthy", "inspiring",
    "helpful", "gentle", "wise"
]

# More specific negative actions from original code
negativeActions = [
    "was caught running in the corridors",
    "arrived late to class",
    "failed to complete homework assignment",
    "disrupted class with inappropriate joke",
    "was found wandering after curfew",
    "used magic in the corridors between classes",
    "spoke disrespectfully to a professor",
    "skipped class without permission",
    "caused a cauldron to explode in Potions",
    "released a Dungbomb in the Great Hall",
    "was caught in a restricted section without permission",
    "used a forbidden spell",
    "sent a cursed note to another student",
    "attempted to enter the Forbidden Forest",
    "threw food during mealtime"
]

def positiveDesc():
    """Return a varied positive point description"""
    result = ""
    if random.random() > 0.35:
        if random.random() > 0.5:
            result = f" {random.choice(verbsShowed)} {random.choice(adjectives)} {random.choice(nouns)}"
            if random.random() > 0.5:
                result += f" of the {random.choice(nounsTopic)}"
        else:
            result = f" {random.choice(verbsExplained)} the {random.choice(nounsTopic)}"
            if random.random() > 0.5:
                result += f" with {random.choice(adjectives)} {random.choice(nouns)}"
    else:
        result = f" {random.choice(verbsWas)} {random.choice(adverbsPositive)} {random.choice(adjectivesPositive)}"
    return result + "."

def negativeDesc():
    """Return a varied negative point description"""
    if random.random() > 0.6:
        # Use specific negative actions
        return f" {random.choice(negativeActions)}."
    else:
        # Use general negative descriptions
        return f" {random.choice(verbsWas)} {random.choice(adverbsNegative)} {random.choice(adjectivesNegative)}."

# Modified date generation that's more versatile
def random_date(start_date, end_date):
    """Generate random date between start_date and end_date using direct date calculation."""
    try:
        # Parsuj daty wejściowe
        start_year, start_month, start_day = map(int, start_date.split('-'))
        end_year, end_month, end_day = map(int, end_date.split('-'))
        
        # Prostsze podejście: najpierw wybierz losowy rok
        year = random.randint(start_year, end_year)
        
        # Wybierz losowy miesiąc - jeśli to pierwszy lub ostatni rok, weź pod uwagę ograniczenia
        if year == start_year and year == end_year:
            month = random.randint(start_month, end_month)
        elif year == start_year:
            month = random.randint(start_month, 12)
        elif year == end_year:
            month = random.randint(1, end_month)
        else:
            month = random.randint(1, 12)
            
        # Wybierz losowy dzień - weź pod uwagę liczbę dni w miesiącu
        if month in [4, 6, 9, 11]:
            max_day = 30
        elif month == 2:
            if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
                max_day = 29  # rok przestępny
            else:
                max_day = 28
        else:
            max_day = 31
            
        if year == start_year and month == start_month and year == end_year and month == end_month:
            day = random.randint(start_day, min(end_day, max_day))
        elif year == start_year and month == start_month:
            day = random.randint(start_day, max_day)
        elif year == end_year and month == end_month:
            day = random.randint(1, min(end_day, max_day))
        else:
            day = random.randint(1, max_day)
            
        return f"{year:04d}-{month:02d}-{day:02d}"
    except Exception as e:
        debug_print(f"ERROR: Failed to generate random date: {str(e)}")
        return "2000-01-01"  # Bezpieczna wartość domyślna

def main():
    global stop_process
    try:
        debug_print("[>>>] Starting data generation...")
        debug_print("[INFO] Press Ctrl+C to stop the process")
        debug_print(f"[INFO] Using data directory: {DATA_DIR}")
        debug_print(f"[INFO] Using names directory: {NAMES_DIR}")
        
        # Ensure directories exist
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(NAMES_DIR, exist_ok=True)
        
        # Load name files
        try:
            feminine_names = []
            masculine_names = []
            surnames = []
            
            feminine_path = os.path.join(NAMES_DIR, "feminineNames.csv")
            masculine_path = os.path.join(NAMES_DIR, "masculineNames.csv")
            surnames_path = os.path.join(NAMES_DIR, "surnames.csv")
            
            if os.path.exists(feminine_path):
                with open(feminine_path, "r", encoding="utf-8") as f:
                    feminine_names = f.read().split(";")
                    feminine_names = [name.strip() for name in feminine_names if name.strip()]
            
            if os.path.exists(masculine_path):
                with open(masculine_path, "r", encoding="utf-8") as f:
                    masculine_names = f.read().split(";")
                    masculine_names = [name.strip() for name in masculine_names if name.strip()]
            
            if os.path.exists(surnames_path):
                with open(surnames_path, "r", encoding="utf-8") as f:
                    surnames = f.read().split(";")
                    surnames = [surname.strip() for surname in surnames if surname.strip()]
            
            if not feminine_names:
                feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
                debug_print("[WARN] Using default feminine names")
                
            if not masculine_names:
                masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
                debug_print("[WARN] Using default masculine names")
                
            if not surnames:
                surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]
                debug_print("[WARN] Using default surnames")
            
            debug_print("Name files loaded", {
                "feminine names": len(feminine_names),
                "masculine names": len(masculine_names),
                "surnames": len(surnames)
            })
        except Exception as e:
            debug_print(f"ERROR while loading name files: {e}")
            debug_print("[WARN] Using default names")
            feminine_names = ["Emma", "Olivia", "Ava", "Isabella", "Sophia", "Charlotte", "Mia", "Amelia", "Harper", "Evelyn"]
            masculine_names = ["Liam", "Noah", "William", "James", "Oliver", "Benjamin", "Elijah", "Lucas", "Mason", "Logan"]
            surnames = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor"]

        # 1. Teachers
        check_stop()
        debug_print("Generating teachers...")
        teacher_ids = list(range(CONFIG['nTeachers']))
        with open(os.path.join(DATA_DIR, "teachers.csv"), "w", newline='', encoding='utf-8') as teachers_file:
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
        with open(os.path.join(DATA_DIR, "houses.csv"), "w", newline='', encoding='utf-8') as houses_file:
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
        with open(os.path.join(DATA_DIR, "dormitories.csv"), "w", newline='', encoding='utf-8') as dormitories_file:
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
        with open(os.path.join(DATA_DIR, "students.csv"), "w", newline='', encoding='utf-8') as students_file:
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

        with open(os.path.join(DATA_DIR, "students.csv"), "r", newline='', encoding='utf-8') as students_file:
            reader = csv.DictReader(students_file, delimiter=';')
            for row in reader:
                students_data[int(row['id'])] = {
                    'year': int(row['year']),
                    'house_id': int(row['house_id']),
                    'gender': row['gender']
                }

        with open(os.path.join(DATA_DIR, "subjects.csv"), "r", newline='', encoding='utf-8') as subjects_file:
            reader = csv.DictReader(subjects_file, delimiter=';')
            for row in reader:
                subjects_data[int(row['id'])] = {
                    'year': int(row['year']),
                    'name': row['name'],
                    'teacher_id': int(row['teacher_id'])
                }

        debug_print(f"Loaded data for {len(students_data)} students and {len(subjects_data)} subjects")

        # Określ które przedmioty są obowiązkowe w zależności od roku nauki
        core_subjects_by_year = {
            1: ["Transfiguration", "Charms", "Potions", "History of Magic", "Defence Against the Dark Arts", "Astronomy", "Herbology", "Flying"],
            2: ["Transfiguration", "Charms", "Potions", "History of Magic", "Defence Against the Dark Arts", "Astronomy", "Herbology"],
            3: ["Transfiguration", "Charms", "Potions", "History of Magic", "Defence Against the Dark Arts"],
            4: ["Transfiguration", "Charms", "Potions", "History of Magic", "Defence Against the Dark Arts"],
            5: ["Transfiguration", "Charms", "Potions", "Defence Against the Dark Arts"],
            6: ["Defence Against the Dark Arts"],
            7: ["Defence Against the Dark Arts"]
        }
        
        # Klasyfikacja przedmiotów na obowiązkowe i opcjonalne dla danego roku
        def is_core_subject(subject_name, year):
            for core in core_subjects_by_year.get(year, []):
                if core in subject_name:
                    return True
            return False

        student_subject_pairs = set()
        with open(os.path.join(DATA_DIR, "students_subjects.csv"), "w", newline='', encoding='utf-8') as students_subjects_file:
            writer = csv.writer(students_subjects_file, delimiter=';')
            writer.writerow(["student_id", "subject_id"])
            
            total_students = len(student_ids)
            for i, student_id in enumerate(student_ids, 1):
                if i % 1000 == 0:  # Show progress every 1000 students
                    debug_print(f"Processed {i}/{total_students} students")
                
                student_year = students_data[student_id]['year']
                student_house = students_data[student_id]['house_id']
                student_gender = students_data[student_id]['gender']
                
                # Generuj cechy osobowości i preferencje studenta
                academic_preference = random.random()  # 0-1, gdzie wyższa wartość oznacza większe zainteresowanie nauką
                attendance_rate = random.random() * 0.5 + 0.5  # 0.5-1.0, im wyższa tym lepiej student uczęszcza na zajęcia
                practical_vs_theory = random.random()  # 0-1, gdzie wyższa wartość oznacza preferencję dla zajęć praktycznych
                
                # Wygeneruj listę przedmiotów, które student szczególnie lubi i których nie lubi
                all_subjects = list(subjects_data.keys())
                favorite_subjects = random.sample(all_subjects, min(3, len(all_subjects)))
                disliked_subjects = random.sample([s for s in all_subjects if s not in favorite_subjects], min(3, len(all_subjects)))
                
                # Przedmioty dla danego roku
                for subject_id, subject_info in subjects_data.items():
                    if subject_info['year'] == student_year:
                        is_core = is_core_subject(subject_info['name'], student_year)
                        is_favorite = subject_id in favorite_subjects
                        is_disliked = subject_id in disliked_subjects
                        
                        # Bazowe prawdopodobieństwo wyboru przedmiotu
                        base_probability = 0.0
                        
                        # Modyfikatory prawdopodobieństwa
                        if is_core:
                            if student_year <= 3:
                                # W początkowych latach przedmioty obowiązkowe mają wysokie bazowe prawdopodobieństwo
                                base_probability = 0.80 + (attendance_rate * 0.15)
                            else:
                                # W późniejszych latach mniejsze, ale wciąż znaczące prawdopodobieństwo
                                base_probability = 0.65 + (attendance_rate * 0.15)
                        else:
                            # Przedmioty nieobowiązkowe mają niskie bazowe prawdopodobieństwo
                            base_probability = 0.25 + (academic_preference * 0.25)
                        
                        # Modyfikatory za ulubione i nielubiane przedmioty
                        if is_favorite:
                            base_probability += 0.35  # Duży wzrost za ulubiony przedmiot
                        if is_disliked:
                            base_probability -= 0.30  # Duży spadek za nielubiany przedmiot
                        
                        # Modyfikatory za praktyczne vs teoretyczne przedmioty
                        is_practical = any(practical in subject_info['name'].lower() for practical in ["defence", "charms", "transfiguration", "potions", "flying", "creatures", "herbology"])
                        if is_practical and practical_vs_theory > 0.6:
                            base_probability += 0.15  # Bonus dla uczniów preferujących praktykę
                        elif not is_practical and practical_vs_theory < 0.4:
                            base_probability += 0.15  # Bonus dla uczniów preferujących teorię
                        
                        # Modyfikatory specjalne dla domów
                        if "Divination" in subject_info['name']:
                            if student_house == 2:  # Ravenclaw
                                base_probability -= 0.10  # Krukoni są sceptyczni wobec wróżbiarstwa
                        elif "History of Magic" in subject_info['name']:
                            if student_house == 0:  # Gryffindor
                                base_probability -= 0.15  # Gryfoni mniej interesują się historią
                        elif "Potions" in subject_info['name']:
                            if student_house == 3:  # Slytherin
                                base_probability += 0.15  # Ślizgoni preferują eliksiry
                        elif "Care of Magical Creatures" in subject_info['name']:
                            if student_house == 1:  # Hufflepuff
                                base_probability += 0.20  # Puchoni preferują opiekę nad magicznymi stworzeniami
                        
                        # Wprowadź element kompletnej losowości
                        random_factor = random.random() * 0.30 - 0.15  # -0.15 do +0.15 losowej zmiany
                        final_probability = base_probability + random_factor
                        
                        # Ogranicz prawdopodobieństwo do zakresu 0.0-1.0
                        final_probability = max(0.0, min(1.0, final_probability))
                        
                        # Ostateczna decyzja
                        if random.random() < final_probability:
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
        with open(os.path.join(DATA_DIR, "subjects.csv"), "r", newline='', encoding='utf-8') as subjects_file:
            reader = csv.DictReader(subjects_file, delimiter=';')
            for row in reader:
                subject_teachers[int(row['id'])] = int(row['teacher_id'])

        debug_print(f"Loaded teacher data for {len(subject_teachers)} subjects")

        # Przygotuj mapowanie ocen na wartości numeryczne (dla rozkładu normalnego)
        # O = Outstanding (najlepsza) -> odpowiada 5
        # E = Exceeds Expectations -> odpowiada 4
        # A = Acceptable -> odpowiada 3
        # P = Poor -> odpowiada 2
        # D = Dreadful -> odpowiada 1
        # T = Troll (najgorsza) -> odpowiada 0
        grade_to_numeric = {
            'O': 5,
            'E': 4,
            'A': 3,
            'P': 2,
            'D': 1,
            'T': 0
        }
        numeric_to_grade = {v: k for k, v in grade_to_numeric.items()}
        
        # Generuj oceny
        with open(os.path.join(DATA_DIR, "grades.csv"), "w", newline='', encoding='utf-8') as grades_file:
            writer = csv.writer(grades_file, delimiter=';')
            writer.writerow(["id", "value", "award_date", "student_id", "subject_id", "teacher_id"])
            
            grade_id = 0
            total_pairs = len(student_subject_pairs)
            
            # Utwórz rozkład normalny z średnią 3 (odpowiada ocenie 'A') i odchyleniem 1
            # Obetnij do zakresu 0-5 (odpowiada T-O)
            grade_distribution = get_truncated_normal(mean=3, sd=1, low=0, upp=5)
            
            for i, (student_id, subject_id) in enumerate(student_subject_pairs, 1):
                if i % 10000 == 0:  # Show progress every 10000 pairs
                    debug_print(f"Processed {i}/{total_pairs} student-subject pairs")
                
                num_grades = random.randint(CONFIG['min_grades_per_subject'], CONFIG['max_grades_per_subject'])
                teacher_id = subject_teachers[subject_id]
                
                for _ in range(num_grades):
                    # Generuj wartość numeryczną z rozkładu normalnego i zaokrąglij do najbliższej liczby całkowitej
                    numeric_value = round(grade_distribution.rvs())
                    # Mapuj wartość numeryczną na symbol oceny
                    value = numeric_to_grade[numeric_value]
                    
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
        
        # First, load student names and house information for more descriptive point reasons
        student_data = {}
        with open(os.path.join(DATA_DIR, "students.csv"), "r", newline='', encoding='utf-8') as students_file:
            reader = csv.DictReader(students_file, delimiter=';')
            for row in reader:
                student_data[int(row['id'])] = {
                    'name': f"{row['name']} {row['surname']}",
                    'house_id': int(row['house_id'])
                }
        
        # Przypisz specjalne cechy do domów, które wpłyną na rozkład punktów
        house_point_bias = {
            0: {'positive_chance': 0.65, 'positive_mean': 7, 'positive_sd': 4, 'negative_mean': -5, 'negative_sd': 3},  # Gryffindor - bardziej ekstremalne wartości
            1: {'positive_chance': 0.80, 'positive_mean': 3, 'positive_sd': 2, 'negative_mean': -2, 'negative_sd': 1},  # Hufflepuff - więcej małych pozytywnych punktów
            2: {'positive_chance': 0.85, 'positive_mean': 4, 'positive_sd': 2, 'negative_mean': -2, 'negative_sd': 1},  # Ravenclaw - bardzo mało negatywnych punktów
            3: {'positive_chance': 0.50, 'positive_mean': 6, 'positive_sd': 3, 'negative_mean': -4, 'negative_sd': 2}   # Slytherin - zrównoważone, ale bardziej ekstremalne
        }
        
        with open(os.path.join(DATA_DIR, "points.csv"), "w", newline='', encoding='utf-8') as points_file:
            writer = csv.writer(points_file, delimiter=';')
            writer.writerow(["id", "value", "description", "award_date", "student_id", "teacher_id"])
            
            # Generuj proporcjonalnie więcej lub mniej punktów dla różnych domów
            house_points_count = {
                0: int(CONFIG['nStudents'] * CONFIG['pointsPerStudent'] * 1.1),    # Gryffindor - więcej punktów (zarówno + jak i -)
                1: int(CONFIG['nStudents'] * CONFIG['pointsPerStudent'] * 0.8),    # Hufflepuff - mniej punktów ogólnie
                2: int(CONFIG['nStudents'] * CONFIG['pointsPerStudent'] * 0.9),    # Ravenclaw - standardowa ilość
                3: int(CONFIG['nStudents'] * CONFIG['pointsPerStudent'] * 1.2)     # Slytherin - najwięcej punktów (zarówno + jak i -)
            }
            
            # Stwórz rozkłady normalne dla każdego domu
            dist_by_house = {}
            for house_id, bias in house_point_bias.items():
                dist_by_house[house_id] = {
                    'positive': get_truncated_normal(
                        mean=bias['positive_mean'], 
                        sd=bias['positive_sd'], 
                        low=1, 
                        upp=CONFIG['max_points']
                    ),
                    'negative': get_truncated_normal(
                        mean=bias['negative_mean'], 
                        sd=bias['negative_sd'], 
                        low=CONFIG['min_points'], 
                        upp=-1
                    )
                }
            
            # Generuj punkty dla każdego domu
            points_id = 0
            total_points = sum(house_points_count.values())
            progress_bar = tqdm(total=total_points, desc="Generating points", file=sys.stdout)
            
            for house_id, n_points in house_points_count.items():
                # Znajdź wszystkich studentów z tego domu
                students_in_house = [
                    student_id for student_id, data in student_data.items() 
                    if data['house_id'] == house_id
                ]
                
                if not students_in_house:
                    debug_print(f"WARNING: No students found for house {house_id}")
                    continue
                
                # Generuj punkty dla tego domu
                house_bias = house_point_bias[house_id]
                house_dists = dist_by_house[house_id]
                
                for i in range(n_points):
                    if stop_process:
                        return
                    
                    # Określ czy przyznać punkty pozytywne czy negatywne na podstawie domu
                    is_positive = random.random() < house_bias['positive_chance']
                    
                    if is_positive:
                        v = round(house_dists['positive'].rvs())
                    else:
                        v = round(house_dists['negative'].rvs())
                    
                    student_id = random.choice(students_in_house)
                    teacher_id = random.choice(teacher_ids)
                    award_date = random_date("2023-09-01", "2024-06-30")
                    
                    # Generate descriptive reason
                    student_name = student_data[student_id]['name']
                    description = days() + student_name
                    
                    if v > 0:
                        description += positiveDesc()
                    else:
                        description += negativeDesc()
                    
                    writer.writerow([points_id, v, description, award_date, student_id, teacher_id])
                    points_id += 1
                    progress_bar.update(1)
            
            progress_bar.close()

        debug_print(f"Generated {count_rows_in_file('points.csv')} points")
        verify_foreign_keys('points.csv', 'student_id', 'students.csv', 'id')
        verify_foreign_keys('points.csv', 'teacher_id', 'teachers.csv', 'id')

        # 9. Quidditch Team Members
        check_stop()
        debug_print("Generating Quidditch team members...")
        with open(os.path.join(DATA_DIR, "quidditch_team_members.csv"), "w", newline='', encoding='utf-8') as quidditch_file:
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