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
        'quidditch_team_members',
        'points',
        'grades',
        'students',
        'subjects',
        'dormitories',
        'houses',
        'teachers'
    ]
    
    for table in tables:
        print(f"Clearing table {table}...")
        try:
            cursor.execute(f"DELETE FROM {table}")
            print(f"Table {table} cleared successfully")
        except Exception as e:
            print(f"Error clearing table {table}: {str(e)}")
            raise

def get_first_teacher_id(cursor):
    """Get the ID of the first teacher in the database"""
    cursor.execute("SELECT MIN(id) FROM Teachers")
    return cursor.fetchone()[0]

def import_subjects(cursor):
    """Import subjects data"""
    print("Importing subjects...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'subjects.csv'))
    subject_id_map = {}
    
    for _, row in df.iterrows():
        # Get a random teacher for this subject
        cursor.execute("SELECT id FROM Teachers ORDER BY DBMS_RANDOM.VALUE FETCH FIRST 1 ROW ONLY")
        teacher_id = cursor.fetchone()[0]
        print(f"Using teacher ID: {teacher_id}")
        
        # Insert the subject
        cursor.execute("""
            INSERT INTO Subjects (id, name, classroom, year, teacher_id)
            VALUES (subjects_seq.NEXTVAL, :1, FLOOR(DBMS_RANDOM.VALUE(100,999)), 1, :2)
            RETURNING id INTO :3
        """, (row['name'], teacher_id, cursor.var(int)))
        
        new_id = cursor.var.getvalue()
        subject_id_map[int(row['id'])] = new_id
        
    print(f"Imported {len(df)} subjects")
    return subject_id_map

def import_teachers(cursor):
    """Import teachers data"""
    print("Importing teachers...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'teachers.csv'))
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Teachers (id, name, surname, date_of_birth, date_of_employment)
            VALUES (teachers_seq.NEXTVAL, :1, :2, SYSDATE-365*30, SYSDATE-365*5)
        """, (row['name'], 'Surname'))
    print(f"Imported {len(df)} teachers")

def import_houses(cursor):
    """Import houses data"""
    print("Importing houses...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'houses.csv'))
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
    df = pd.read_csv(os.path.join(DATA_DIR, 'dormitories.csv'))
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
    df = pd.read_csv(os.path.join(DATA_DIR, 'students.csv'))
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
            VALUES (:1, :2, :3, :4, SYSDATE-365*11-DBMS_RANDOM.VALUE(0,365), 
                   FLOOR(DBMS_RANDOM.VALUE(1,8)), FLOOR(DBMS_RANDOM.VALUE(0,2)), :5, :6)
        """, (new_id, row['name'][:64], 'Surname', row['gender'], row['house_id'], dormitory_id))
        
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

def import_grades(cursor, student_id_map, subject_id_map):
    """Import grades data"""
    print("Importing grades...")
    print(f"Student ID mapping (first 5): {dict(list(student_id_map.items())[:5])}")
    print(f"Subject ID mapping: {subject_id_map}")
    
    # Get teacher IDs for each subject
    cursor.execute("SELECT id, teacher_id FROM Subjects")
    subject_teacher_map = {row[0]: row[1] for row in cursor.fetchall()}
    print(f"Subject-Teacher mapping: {subject_teacher_map}")
    
    # Grade value mapping (1-6 to O,E,A,P,D,T)
    grade_map = {
        1: 'T',  # Troll
        2: 'D',  # Dreadful
        3: 'P',  # Poor
        4: 'A',  # Acceptable
        5: 'E',  # Exceeds Expectations
        6: 'O'   # Outstanding
    }
    
    df = pd.read_csv(os.path.join(DATA_DIR, 'grades.csv'))
    for _, row in df.iterrows():
        new_student_id = student_id_map.get(int(row['student_id']))
        new_subject_id = subject_id_map.get(int(row['subject_id']))
        
        if not new_student_id or not new_subject_id:
            print(f"Warning: Missing mapping for student_id={row['student_id']} or subject_id={row['subject_id']}")
            continue
            
        teacher_id = subject_teacher_map.get(new_subject_id)
        if not teacher_id:
            print(f"Warning: No teacher found for subject_id={new_subject_id}")
            continue
            
        grade_value = grade_map.get(int(row['grade']), 'P')  # Default to 'P' if invalid grade
            
        if _ < 5:  # Print first 5 grade entries
            print(f"Inserting grade for student_id={row['student_id']} -> {new_student_id}, subject_id={row['subject_id']} -> {new_subject_id}, teacher_id={teacher_id}, grade={grade_value}")
            
        cursor.execute("""
            INSERT INTO Grades (id, value, award_date, student_id, subject_id, teacher_id)
            VALUES (grades_seq.NEXTVAL, :1, SYSDATE-DBMS_RANDOM.VALUE(0,365), :2, :3, :4)
        """, (grade_value, new_student_id, new_subject_id, teacher_id))
    print(f"Imported {len(df)} grades")

def import_points(cursor):
    """Import points data"""
    print("Importing points...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'points.csv'))
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Points (id, value, description, award_date, student_id, teacher_id)
            VALUES (points_seq.NEXTVAL, :1, :2, SYSDATE-DBMS_RANDOM.VALUE(0,365), :3, 1)
        """, (row['points'], 'For achievements', row['student_id']))
    print(f"Imported {len(df)} points")

def import_quidditch(cursor):
    """Import Quidditch team members data"""
    print("Importing Quidditch team members...")
    df = pd.read_csv(os.path.join(DATA_DIR, 'quidditch_team_members.csv'))
    for _, row in df.iterrows():
        cursor.execute("""
            INSERT INTO Quidditch_Team_Members (id, position, is_captain, student_id)
            VALUES (quidditch_seq.NEXTVAL, :1, FLOOR(DBMS_RANDOM.VALUE(0,2)), :2)
        """, (row['position'], row['student_id']))
    print(f"Imported {len(df)} Quidditch team members")

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

        print("\nImporting base tables...")
        # Import in order of dependencies
        import_teachers(cursor)  # No foreign keys
        connection.commit()
        
        import_houses(cursor)  # References teachers
        connection.commit()
        
        import_dormitories(cursor)  # References houses
        connection.commit()
        
        subject_id_map = import_subjects(cursor)  # References teachers
        connection.commit()
        
        student_id_map = import_students(cursor)  # References houses and dormitories
        connection.commit()
        
        import_grades(cursor, student_id_map, subject_id_map)  # References students, subjects, and teachers
        connection.commit()
        
        import_points(cursor)  # References students and teachers
        connection.commit()
        
        import_quidditch(cursor)  # References students
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