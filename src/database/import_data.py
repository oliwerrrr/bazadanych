import oracledb
import csv
import os
import time
import sys
import signal
from datetime import datetime
from tqdm import tqdm
import pandas as pd
import traceback
import random

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')

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

def check_stop():
    global stop_process
    if stop_process:
        sys.stdout.write("[INFO] Process stopped by user\n")
        sys.stdout.flush()
        sys.exit(0)

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

def count_rows_in_file(filename):
    if not os.path.exists(filename):
        debug_print(f"[ERROR] File {filename} does not exist!")
        return 0
    with open(filename, "r", newline='', encoding='utf-8') as f:
        return sum(1 for row in f) - 1  # -1 for header

def read_csv_file(filepath):
    """Read a CSV file with either comma or semicolon delimiter"""
    try:
        # Try comma first
        df = pd.read_csv(filepath)
        return df
    except:
        try:
            # Try semicolon
            df = pd.read_csv(filepath, sep=';')
            return df
        except Exception as e:
            print(f"Error reading {filepath}: {str(e)}")
            raise

def import_csv(cursor, filename, table_name, columns):
    global stop_process
    if stop_process:
        return False
        
    if not os.path.exists(filename):
        debug_print(f"[ERROR] File {filename} does not exist!")
        return False
    
    debug_print(f"[>>>] Starting import to table {table_name}...")
    row_count = 0
    
    try:
        with open(filename, "r", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            total_rows = count_rows_in_file(filename)
            
            # Use tqdm for progress bar
            pbar = tqdm(total=total_rows, desc=f"Importing {table_name}", unit="rows", file=sys.stdout)
            
            for row in reader:
                if stop_process:
                    pbar.close()
                    return False
                    
                values = [row[col] for col in columns]
                placeholders = ','.join([':' + str(i+1) for i in range(len(columns))])
                sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                cursor.execute(sql, values)
                row_count += 1
                pbar.update(1)
                
                if row_count % 1000 == 0:
                    debug_print(f"[>>>] Progress: {row_count}/{total_rows} rows imported to {table_name} ({(row_count/total_rows*100):.1f}%)")
            
            pbar.close()
            debug_print(f"[OK] Successfully imported {row_count} rows to {table_name}")
            return True
    except Exception as e:
        debug_print(f"[ERROR] Import failed for {table_name}: {str(e)}")
        return False

def clear_tables(cursor):
    """Clear all tables in the correct order"""
    tables = [
        'quidditch_team_members',  # No dependencies
        'points',                  # Depends on students
        'grades',                  # Depends on students and subjects
        'students_subjects',       # Depends on students and subjects
        'students',               # Depends on houses and dormitories
        'subjects',               # Depends on teachers
        'dormitories',            # Depends on houses
        'houses',                 # No dependencies
        'teachers'                # No dependencies
    ]
    
    for table in tables:
        try:
            print(f"Clearing table {table}...")
            cursor.execute(f"DELETE FROM {table}")
            print(f"Table {table} cleared successfully")
        except Exception as e:
            print(f"Error clearing table {table}:", str(e))
            if hasattr(e, 'help'):
                print("Help:", e.help)
            raise e

def get_first_teacher_id(cursor):
    """Get the ID of the first teacher in the database"""
    cursor.execute("SELECT MIN(id) FROM Teachers")
    return cursor.fetchone()[0]

def import_teachers(cursor):
    """Import teachers data"""
    print("Importing teachers...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'teachers.csv'), sep=';')
    teacher_id_map = {}
    
    for _, row in df.iterrows():
        # Get next value from sequence
        cursor.execute("SELECT teachers_seq.NEXTVAL FROM dual")
        new_id = cursor.fetchone()[0]
        teacher_id_map[row['id']] = new_id
        
        # Insert teacher with all required fields
        cursor.execute("""
            INSERT INTO Teachers (id, name, surname, date_of_birth, date_of_employment)
            VALUES (:1, :2, :3, TO_DATE(:4, 'YYYY-MM-DD'), TO_DATE(:5, 'YYYY-MM-DD'))
        """, (new_id, row['name'], row['surname'], row['date_of_birth'], row['date_of_employment']))
    
    print(f"Imported {len(teacher_id_map)} teachers")
    return teacher_id_map

def import_subjects(cursor, teacher_id_map):
    print("Importing subjects...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'subjects.csv'), sep=';')
    subject_id_map = {}
    
    for _, row in df.iterrows():
        subject_name = row['name']
        classroom = row['classroom']
        year = row['year']
        old_teacher_id = row['teacher_id']
        
        # Map the teacher ID
        if old_teacher_id not in teacher_id_map:
            print(f"Warning: Teacher ID {old_teacher_id} not found in mapping")
            continue
        
        teacher_id = teacher_id_map[old_teacher_id]
        
        # Get next value from sequence
        cursor.execute("SELECT subjects_seq.NEXTVAL FROM dual")
        new_id = cursor.fetchone()[0]
        subject_id_map[row['id']] = new_id
        
        # Insert subject
        cursor.execute("""
            INSERT INTO Subjects (id, name, classroom, year, teacher_id)
            VALUES (:1, :2, :3, :4, :5)
        """, (new_id, subject_name, classroom, year, teacher_id))
        
        if len(subject_id_map) <= 5:
            print(f"Imported subject {subject_name} with ID {new_id}")
    
    print(f"Imported {len(subject_id_map)} subjects")
    return subject_id_map

def import_houses(cursor):
    """Import houses data"""
    print("Importing houses...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'houses.csv'), sep=';')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Houses (id, name, symbol, location, teacher_id)
            VALUES (:1, :2, :3, :4, NULL)
        """, (row['id'], row['name'], row['name'].upper()[:16], f"{row['name']} Tower"[:128]))
        print(f"Imported house {row['name']} with ID {row['id']}")
    print(f"Imported {len(df)} houses")

def import_dormitories(cursor):
    """Import dormitories data"""
    print("Importing dormitories...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'dormitories.csv'), sep=';')
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Dormitories (id, gender, room_number, house_id)
            VALUES (dormitories_seq.NEXTVAL, :1, :2, :3)
        """, ('M' if int(row['id']) % 2 == 0 else 'F', int(row['id']), row['house_id']))
    print(f"Imported {len(df)} dormitories")

def get_dormitory_id_for_house(cursor, house_id, gender):
    """Get a valid dormitory ID for the given house and gender"""
    cursor.execute("""
        SELECT MIN(id) FROM Dormitories 
        WHERE house_id = :1 AND gender = :2
    """, (house_id, gender))
    return cursor.fetchone()[0]

def import_students(cursor):
    """Import students data"""
    print("Importing students...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'students.csv'), sep=';')
    student_id_map = {}
    
    for _, row in df.iterrows():
        # Get a valid dormitory ID for this student's house and gender
        dormitory_id = get_dormitory_id_for_house(cursor, row['house_id'], row['gender'])
        if not dormitory_id:
            print(f"Warning: No dormitory found for house {row['house_id']} and gender {row['gender']}")
            continue
            
        cursor.execute("SELECT students_seq.NEXTVAL FROM DUAL")
        new_id = cursor.fetchone()[0]
        student_id_map[int(row['id'])] = new_id
            
        cursor.execute("""
            INSERT INTO Students (id, name, surname, gender, date_of_birth, year, hogsmeade_consent, house_id, dormitory_id)
            VALUES (:1, :2, :3, :4, TO_DATE(:5, 'YYYY-MM-DD'), :6, :7, :8, :9)
        """, (new_id, row['name'][:64], row['surname'], row['gender'], row['date_of_birth'], 
              row['year'], row['hogsmeade_consent'], row['house_id'], dormitory_id))
        
        if _ < 5:  # Print first 5 student IDs
            print(f"Created student with ID {new_id} for original ID {row['id']}")
            
    print(f"Imported {len(df)} students")
    return student_id_map

def get_student_id_mapping(cursor):
    """Get a mapping of old student IDs to new ones"""
    cursor.execute("SELECT id FROM Students ORDER BY id")
    student_ids = [row[0] for row in cursor.fetchall()]
    mapping = {i+1: student_id for i, student_id in enumerate(student_ids)}
    print(f"Student ID mapping (first 5 entries): {dict(list(mapping.items())[:5])}")
    return mapping

def get_subject_id_mapping(cursor):
    """Get a mapping of old subject IDs to new ones"""
    cursor.execute("SELECT id FROM Subjects ORDER BY id")
    subject_ids = [row[0] for row in cursor.fetchall()]
    mapping = {i+1: subject_id for i, subject_id in enumerate(subject_ids)}
    print(f"Subject ID mapping: {mapping}")
    return mapping

def import_grades(cursor, student_id_map, subject_id_map, teacher_id_map):
    """Import grades data"""
    print("Importing grades...")
    print("Student ID mapping (first 5):", dict(list(student_id_map.items())[:5]))
    
    df = pd.read_csv(os.path.join(DATA_DIR, 'grades.csv'), sep=';')
    
    # Map numeric grades to letters
    grade_map = {
        2: 'T',  # Troll
        3: 'D',  # Dreadful
        4: 'P',  # Poor
        5: 'A',  # Acceptable
        6: 'E',  # Exceeds Expectations
        7: 'O'   # Outstanding
    }
    
    for _, row in df.iterrows():
        student_id = student_id_map.get(row['student_id'])
        subject_id = subject_id_map.get(row['subject_id'])
        teacher_id = teacher_id_map.get(row['teacher_id'])
        
        if student_id is None:
            print(f"Warning: Student ID {row['student_id']} not found in mapping")
            continue
            
        if subject_id is None:
            print(f"Warning: Subject ID {row['subject_id']} not found in mapping")
            continue
            
        if teacher_id is None:
            print(f"Warning: Teacher ID {row['teacher_id']} not found in mapping")
            continue
        
        try:
            # Try to convert value to int and map it
            value = int(row['value'])
            grade_value = grade_map.get(value, 'P')  # Default to 'P' if invalid grade
        except (ValueError, TypeError):
            # If value is already a letter grade or invalid, use it as is
            grade_value = str(row['value']).upper()
            if grade_value not in ['O', 'E', 'A', 'P', 'D', 'T']:
                grade_value = 'P'  # Default to 'P' for invalid grades
        
        # Insert grade
        cursor.execute("""
            INSERT INTO Grades (id, value, award_date, student_id, subject_id, teacher_id)
            VALUES (grades_seq.NEXTVAL, :1, TO_DATE(:2, 'YYYY-MM-DD'), :3, :4, :5)
        """, (grade_value, row['award_date'], student_id, subject_id, teacher_id))
    
    print("Imported grades successfully")

def import_points(cursor, student_id_map, teacher_id_map):
    """Import points data"""
    print("Importing points...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'points.csv'), sep=';')
    
    for _, row in df.iterrows():
        student_id = student_id_map.get(row['student_id'])
        teacher_id = teacher_id_map.get(row['teacher_id'])
        
        if student_id is None:
            print(f"Warning: Student ID {row['student_id']} not found in mapping")
            continue
            
        if teacher_id is None:
            print(f"Warning: Teacher ID {row['teacher_id']} not found in mapping")
            continue
        
        cursor.execute("""
            INSERT INTO Points (id, value, description, award_date, student_id, teacher_id)
            VALUES (points_seq.NEXTVAL, :1, :2, TO_DATE(:3, 'YYYY-MM-DD'), :4, :5)
        """, (row['value'], row['description'], row['award_date'], student_id, teacher_id))
    
    print("Imported points successfully")

def import_quidditch(cursor, student_id_map):
    """Import Quidditch team members data"""
    print("Importing Quidditch team members...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'quidditch_team_members.csv'), sep=';')
    
    for _, row in df.iterrows():
        student_id = student_id_map.get(row['student_id'])
        
        if student_id is None:
            print(f"Warning: Student ID {row['student_id']} not found in mapping")
            continue
        
        cursor.execute("""
            INSERT INTO Quidditch_Team_Members (id, position, is_captain, student_id)
            VALUES (quidditch_seq.NEXTVAL, :1, :2, :3)
        """, (row['position'], row['is_captain'], student_id))
    
    print("Imported Quidditch team members successfully")

def import_students_subjects(cursor, student_id_map, subject_id_map):
    """Import students_subjects data"""
    print("Importing students_subjects...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'students_subjects.csv'), sep=';')
    imported_count = 0
    
    for _, row in df.iterrows():
        new_student_id = student_id_map.get(int(row['student_id']))
        new_subject_id = subject_id_map.get(int(row['subject_id']))
        
        if not new_student_id or not new_subject_id:
            print(f"Warning: Missing mapping for student_id={row['student_id']} or subject_id={row['subject_id']}")
            continue
            
        if imported_count < 5:  # Print first 5 entries
            print(f"Inserting student-subject pair: student_id={row['student_id']} -> {new_student_id}, subject_id={row['subject_id']} -> {new_subject_id}")
            
        cursor.execute("""
            INSERT INTO Students_Subjects (student_id, subject_id)
            VALUES (:1, :2)
        """, (new_student_id, new_subject_id))
        imported_count += 1
        
    print(f"Imported {imported_count} student-subject pairs")

def get_database_connection():
    """Get database connection with proper error handling"""
    try:
        connection = oracledb.connect("SYSTEM/admin@localhost:1521/XE")
        print("Database connection successful")
        return connection
    except oracledb.Error as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

def main():
    """Main function to import data"""
    print("Starting data import...")
    print(f"Using data directory: {DATA_DIR}")

    try:
        connection = get_database_connection()
        cursor = connection.cursor()
        print("Database connection successful")

        # Clear existing data
        clear_tables(cursor)

        print("\nImporting data in specified order...")
        
        # 1. Import teachers first (no dependencies)
        print("\n1. Importing teachers...")
        teacher_id_map = import_teachers(cursor)
        connection.commit()
        
        # 2. Import houses (depends on teachers)
        print("\n2. Importing houses...")
        import_houses(cursor)
        connection.commit()
        
        # 3. Import dormitories (depends on houses)
        print("\n3. Importing dormitories...")
        import_dormitories(cursor)
        connection.commit()
        
        # 4. Import subjects (depends on teachers)
        print("\n4. Importing subjects...")
        subject_id_map = import_subjects(cursor, teacher_id_map)
        connection.commit()
        
        # 5. Import students (depends on houses and dormitories)
        print("\n5. Importing students...")
        student_id_map = import_students(cursor)
        connection.commit()
        
        # 6. Import students_subjects (depends on students and subjects)
        print("\n6. Importing students_subjects...")
        import_students_subjects(cursor, student_id_map, subject_id_map)
        connection.commit()
        
        # 7. Import grades (depends on students, subjects, and teachers)
        print("\n7. Importing grades...")
        import_grades(cursor, student_id_map, subject_id_map, teacher_id_map)
        connection.commit()
        
        # 8. Import points (depends on students and teachers)
        print("\n8. Importing points...")
        import_points(cursor, student_id_map, teacher_id_map)
        connection.commit()
        
        # 9. Import quidditch team members (depends on students)
        print("\n9. Importing quidditch team members...")
        import_quidditch(cursor, student_id_map)
        connection.commit()

        print("\nData import completed successfully!")

    except Exception as e:
        print("Error importing data:", str(e))
        if hasattr(e, 'help'):
            print("Help:", e.help)
        traceback.print_exc()
        raise e
    finally:
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    main() 