import oracledb
import csv
import os
import time
import sys
import signal
from datetime import datetime
from tqdm import tqdm

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

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
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        debug_print(f"[ERROR] File {filename} does not exist!")
        return 0
    with open(file_path, "r", newline='', encoding='utf-8') as f:
        return sum(1 for row in f) - 1  # -1 for header

def import_csv(cursor, filename, table_name, columns):
    global stop_process
    if stop_process:
        return False
    
    file_path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(file_path):
        debug_print(f"[ERROR] File {filename} does not exist!")
        return False
    
    debug_print(f"[>>>] Starting import to table {table_name}...")
    row_count = 0
    
    try:
        with open(file_path, "r", newline='', encoding='utf-8') as f:
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
    debug_print("[>>>] Starting database cleanup...")
    tables = [
        "quidditch_team_members",
        "points",
        "grades",
        "students_subjects",
        "students",
        "subjects",
        "dormitories",
        "houses",
        "teachers"
    ]
    
    for table in tables:
        try:
            debug_print(f"[>>>] Clearing table {table}...")
            cursor.execute(f"DELETE FROM {table}")
            debug_print(f"[OK] Table {table} cleared successfully")
        except Exception as e:
            debug_print(f"[ERROR] Failed to clear table {table}: {str(e)}")
            raise e

def main():
    global stop_process
    connection_string = "SYSTEM/admin@localhost:1521/XE"
    
    try:
        debug_print("[>>>] Starting data import...")
        debug_print("[INFO] Press Ctrl+C to stop the process")
        
        check_stop()
        debug_print("[>>>] Connecting to database...")
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        debug_print("[OK] Connected to database successfully")
        
        # Clear tables first
        check_stop()
        clear_tables(cursor)
        connection.commit()
        debug_print("[OK] All tables cleared successfully")
        
        # Table and column definitions
        tables = [
            ("teachers.csv", "teachers", ["id", "name", "surname", "date_of_birth", "date_of_employment"]),
            ("houses.csv", "houses", ["id", "name", "symbol", "location", "teacher_id"]),
            ("dormitories.csv", "dormitories", ["id", "gender", "room_number", "house_id"]),
            ("students.csv", "students", ["id", "name", "surname", "gender", "date_of_birth", "year", "hogsmeade_consent", "house_id", "dormitory_id"]),
            ("subjects.csv", "subjects", ["id", "name", "classroom", "year", "teacher_id"]),
            ("students_subjects.csv", "students_subjects", ["student_id", "subject_id"]),
            ("grades.csv", "grades", ["id", "value", "award_date", "student_id", "subject_id", "teacher_id"]),
            ("points.csv", "points", ["id", "value", "description", "award_date", "student_id", "teacher_id"]),
            ("quidditch_team_members.csv", "quidditch_team_members", ["id", "position", "is_captain", "student_id"])
        ]
        
        for filename, table_name, columns in tables:
            check_stop()
            debug_print(f"[>>>] Processing {filename}")
            
            file_path = os.path.join(DATA_DIR, filename)
            if not os.path.exists(file_path):
                debug_print(f"[ERROR] File {filename} does not exist in directory {DATA_DIR}")
                continue
                
            row_count = count_rows_in_file(filename)
            debug_print(f"[INFO] Found {row_count:,} rows in file {filename}")
            
            if row_count == 0:
                debug_print(f"[WARN] File {filename} is empty!")
                continue
                
            if import_csv(cursor, filename, table_name, columns):
                connection.commit()
            else:
                connection.rollback()
                debug_print(f"[ERROR] Failed to import data to {table_name}")
        
        if not stop_process:
            # Check record count in each table
            debug_print("\n[SUMMARY] Import results:")
            for _, table_name, _ in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                count = cursor.fetchone()[0]
                debug_print(f"  > {table_name}: {count:,} records")
            
            debug_print("\n[OK] Import completed successfully!")
        
    except KeyboardInterrupt:
        debug_print("\n[INFO] Process interrupted by user")
        if 'connection' in locals():
            connection.rollback()
    except Exception as e:
        debug_print(f"[ERROR] {str(e)}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("[INFO] Database connection closed")

if __name__ == "__main__":
    main() 