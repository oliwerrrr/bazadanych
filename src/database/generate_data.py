import os
import sys
import random
import pandas as pd
from datetime import datetime, timedelta
import oracledb
from tqdm import tqdm

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')
NAMES_DIR = os.path.join(BASE_DIR, 'data', 'names')

def ensure_directories():
    """Ensure all required directories exist"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(NAMES_DIR, exist_ok=True)

def get_database_connection():
    """Get database connection with proper error handling"""
    try:
        connection = oracledb.connect("SYSTEM/admin@localhost:1521/XE")
        print("Database connection successful")
        return connection
    except oracledb.Error as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

def load_names():
    """Load names from CSV files"""
    try:
        masculine_names = pd.read_csv(os.path.join(NAMES_DIR, 'masculineNames.csv'), header=None)[0].tolist()
        feminine_names = pd.read_csv(os.path.join(NAMES_DIR, 'feminineNames.csv'), header=None)[0].tolist()
        print(f"Loaded {len(masculine_names)} masculine names and {len(feminine_names)} feminine names")
        return masculine_names, feminine_names
    except Exception as e:
        print(f"Error loading names: {str(e)}")
        raise

def generate_teachers(cursor, num_teachers=111):
    """Generate teacher data"""
    print("Generating teachers...")
    teachers = []
    for i in range(num_teachers):
        teachers.append({
            'id': i + 1,
            'name': f"Professor {chr(65 + i)}",
            'subject_id': random.randint(1, 78)
        })
    df = pd.DataFrame(teachers)
    df.to_csv(os.path.join(DATA_DIR, 'teachers.csv'), index=False)
    print(f"Generated {len(teachers)} teachers")

def generate_houses(cursor):
    """Generate house data"""
    print("Generating houses...")
    houses = [
        {'id': 1, 'name': 'Gryffindor'},
        {'id': 2, 'name': 'Hufflepuff'},
        {'id': 3, 'name': 'Ravenclaw'},
        {'id': 4, 'name': 'Slytherin'}
    ]
    df = pd.DataFrame(houses)
    df.to_csv(os.path.join(DATA_DIR, 'houses.csv'), index=False)
    print(f"Generated {len(houses)} houses")

def generate_dormitories(cursor):
    """Generate dormitory data"""
    print("Generating dormitories...")
    dormitories = []
    for house_id in range(1, 5):
        for i in range(30):  # 30 dormitories per house
            dormitories.append({
                'id': (house_id - 1) * 30 + i + 1,
                'name': f"Dormitory {i + 1}",
                'house_id': house_id
            })
    df = pd.DataFrame(dormitories)
    df.to_csv(os.path.join(DATA_DIR, 'dormitories.csv'), index=False)
    print(f"Generated {len(dormitories)} dormitories")

def generate_subjects(cursor):
    """Generate subject data"""
    print("Generating subjects...")
    subjects = []
    subject_names = [
        'Transfiguration', 'Charms', 'Potions', 'History of Magic',
        'Defense Against the Dark Arts', 'Astronomy', 'Herbology',
        'Arithmancy', 'Study of Ancient Runes', 'Muggle Studies',
        'Care of Magical Creatures', 'Divination', 'Flying'
    ]
    for i, name in enumerate(subject_names, 1):
        subjects.append({
            'id': i,
            'name': name
        })
    df = pd.DataFrame(subjects)
    df.to_csv(os.path.join(DATA_DIR, 'subjects.csv'), index=False)
    print(f"Generated {len(subjects)} subjects")

def generate_students(cursor, num_students=10000):
    """Generate student data"""
    print("Generating students...")
    masculine_names, feminine_names = load_names()
    students = []
    
    for i in tqdm(range(num_students), desc="Generating students"):
        gender = random.choice(['M', 'F'])
        name_pool = masculine_names if gender == 'M' else feminine_names
        name = random.choice(name_pool)
        
        students.append({
            'id': i + 1,
            'name': name,
            'gender': gender,
            'house_id': random.randint(1, 4),
            'dormitory_id': random.randint(1, 120)
        })
    
    df = pd.DataFrame(students)
    df.to_csv(os.path.join(DATA_DIR, 'students.csv'), index=False)
    print(f"Generated {len(students)} students")

def generate_grades(cursor):
    """Generate grade data"""
    print("Generating grades...")
    grades = []
    num_students = 10000
    num_subjects = 78
    
    for student_id in tqdm(range(1, num_students + 1), desc="Generating grades"):
        # Each student gets 5-10 grades per subject
        for subject_id in range(1, num_subjects + 1):
            num_grades = random.randint(5, 10)
            for _ in range(num_grades):
                grades.append({
                    'id': len(grades) + 1,
                    'student_id': student_id,
                    'subject_id': subject_id,
                    'grade': random.randint(1, 6)
                })
    
    df = pd.DataFrame(grades)
    df.to_csv(os.path.join(DATA_DIR, 'grades.csv'), index=False)
    print(f"Generated {len(grades)} grades")

def generate_points(cursor):
    """Generate points data"""
    print("Generating points...")
    points = []
    num_students = 10000
    
    for student_id in tqdm(range(1, num_students + 1), desc="Generating points"):
        # Each student gets 2-4 points records
        num_points = random.randint(2, 4)
        for _ in range(num_points):
            points.append({
                'id': len(points) + 1,
                'student_id': student_id,
                'points': random.randint(-50, 50)
            })
    
    df = pd.DataFrame(points)
    df.to_csv(os.path.join(DATA_DIR, 'points.csv'), index=False)
    print(f"Generated {len(points)} points records")

def generate_quidditch_team_members(cursor):
    """Generate Quidditch team member data"""
    print("Generating Quidditch team members...")
    team_members = []
    positions = ['Seeker', 'Keeper', 'Beater', 'Chaser']
    num_students = 10000
    
    for house_id in range(1, 5):
        # Each house has 7-9 team members
        num_members = random.randint(7, 9)
        for _ in range(num_members):
            team_members.append({
                'id': len(team_members) + 1,
                'student_id': random.randint(1, num_students),
                'position': random.choice(positions)
            })
    
    df = pd.DataFrame(team_members)
    df.to_csv(os.path.join(DATA_DIR, 'quidditch_team_members.csv'), index=False)
    print(f"Generated {len(team_members)} Quidditch team members")

def main():
    try:
        ensure_directories()
        print("Starting data generation...")
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            generate_teachers(cursor)
            generate_houses(cursor)
            generate_dormitories(cursor)
            generate_subjects(cursor)
            generate_students(cursor)
            generate_grades(cursor)
            generate_points(cursor)
            generate_quidditch_team_members(cursor)
            
            print("All data generated successfully!")
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise e

if __name__ == '__main__':
    main() 