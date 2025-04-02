import cx_Oracle
import json
from datetime import datetime
import os
import sys
import time
import uuid

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATABASE_DIR = os.path.join(BASE_DIR, 'src', 'database')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')

def debug_print(message):
    """Print debug message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

def get_database_connection():
    """Get database connection with proper error handling"""
    try:
        connection = cx_Oracle.connect(
            user="SYSTEM",
            password="admin",
            dsn="localhost:1521/XE"
        )
        print("Database connection successful")
        return connection
    except cx_Oracle.Error as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

def run_workload():
    try:
        ensure_directories()
        
        debug_print("Connecting to database...")
        # Database connection details
        connection = cx_Oracle.connect(
            user="SYSTEM",
            password="admin",
            dsn="localhost:1521/XE"
        )
        
        cursor = connection.cursor()
        debug_print("Connected to database")
        
        # Read the workload.sql file
        workload_path = os.path.join(DATABASE_DIR, 'workload.sql')
        if not os.path.exists(workload_path):
            raise FileNotFoundError(f"Workload file not found: {workload_path}")
            
        debug_print(f"Reading workload from {workload_path}")
        with open(workload_path, 'r', encoding='utf-8') as file:
            sql_commands = file.read()
        
        # Split the commands and execute them
        commands = sql_commands.split(';')
        results = []
        
        debug_print(f"Executing {len(commands)} SQL commands...")
        for i, command in enumerate(commands, 1):
            command = command.strip()
            if command:
                try:
                    cursor.execute(command)
                    if cursor.description:  # If it's a SELECT query
                        columns = [col[0] for col in cursor.description]
                        rows = cursor.fetchall()
                        results.append({
                            'query': command,
                            'columns': columns,
                            'rows': [dict(zip(columns, row)) for row in rows],
                            'status': 'success',
                            'message': f'Query executed successfully, returned {len(rows)} rows'
                        })
                        debug_print(f"Command {i}/{len(commands)}: SELECT query returned {len(rows)} rows")
                    else:
                        results.append({
                            'query': command,
                            'status': 'success',
                            'message': 'Command executed successfully'
                        })
                        debug_print(f"Command {i}/{len(commands)}: Non-SELECT query executed successfully")
                except cx_Oracle.Error as error:
                    error_message = str(error)
                    results.append({
                        'query': command,
                        'status': 'error',
                        'message': error_message
                    })
                    debug_print(f"Error executing command {i}/{len(commands)}: {error_message}")
        
        # Save results to JSON file
        results_path = os.path.join(DOCS_DIR, 'workload_results.json')
        debug_print(f"Saving results to {results_path}")
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'total_commands': len(commands),
                'successful_commands': sum(1 for r in results if r.get('status') == 'success'),
                'failed_commands': sum(1 for r in results if r.get('status') == 'error'),
                'results': results
            }, f, indent=2, ensure_ascii=False)
            
        debug_print("Results saved successfully")
        
    except FileNotFoundError as e:
        debug_print(f"ERROR: {str(e)}")
        sys.exit(1)
    except cx_Oracle.Error as e:
        debug_print(f"Database error: {str(e)}")
        sys.exit(1)
    except Exception as e:
        debug_print(f"Unexpected error: {str(e)}")
        sys.exit(1)
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("Database connection closed")

def run_performance_analysis():
    results = {}
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Pobierz liczby rekordów w kluczowych tabelach
            cursor.execute("SELECT COUNT(*) FROM students")
            total_students = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM grades")
            total_grades = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM subjects")
            total_subjects = cursor.fetchone()[0]
            
            # Oblicz limity 10-30% danych
            students_limit = max(int(total_students * 0.2), 1)
            grades_limit = max(int(total_grades * 0.15), 1)
            subjects_limit = max(int(total_subjects * 0.25), 1)
            
            print(f"Using limits - Students: {students_limit}/{total_students}, Grades: {grades_limit}/{total_grades}, Subjects: {subjects_limit}/{total_subjects}")
            
            # Generuj unikalny identyfikator dla tabel
            session_id = str(uuid.uuid4()).replace('-', '')[:8]
            temp_grades_name = f"test_grades_{session_id}"
            temp_students_name = f"test_students_{session_id}"
            temp_delete_name = f"test_delete_{session_id}"
            
            # Upewnij się, że nie ma pozostałości po poprzednich tabelach
            cleanup_temp_tables(conn, [temp_grades_name, temp_students_name, temp_delete_name])
            
            # Simple SELECT
            start_time = time.time()
            cursor.execute(f"SELECT * FROM students WHERE rownum <= {students_limit}")
            rows = cursor.fetchall()
            results['simple_select'] = time.time() - start_time
            results['simple_select_rows'] = len(rows)
            print(f"Completed Simple SELECT in {results['simple_select']:.4f} seconds")
            
            # Complex JOIN
            start_time = time.time()
            cursor.execute(f"""
                SELECT s.name, h.name as house_name 
                FROM students s 
                JOIN houses h ON s.house_id = h.id 
                JOIN grades g ON s.id = g.student_id
                WHERE rownum <= {int(total_students * 0.3)}
            """)
            rows = cursor.fetchall()
            results['complex_join'] = time.time() - start_time
            results['complex_join_rows'] = len(rows)
            print(f"Completed Complex JOIN in {results['complex_join']:.4f} seconds")
            
            # Aggregation
            start_time = time.time()
            cursor.execute("""
                SELECT h.name, COUNT(*) as student_count 
                FROM students s 
                JOIN houses h ON s.house_id = h.id 
                GROUP BY h.name
            """)
            rows = cursor.fetchall()
            results['aggregation'] = time.time() - start_time
            results['aggregation_rows'] = len(rows)
            print(f"Completed Aggregation in {results['aggregation']:.4f} seconds")
            
            # Nested Subquery
            nested_limit = int(total_students * 0.1)
            nested_grades_limit = int(total_grades * 0.1)
            start_time = time.time()
            cursor.execute(f"""
                SELECT name FROM students 
                WHERE id IN (
                    SELECT student_id FROM grades 
                    WHERE value = 'A' 
                    AND rownum <= {nested_grades_limit}
                )
                AND rownum <= {nested_limit}
            """)
            rows = cursor.fetchall()
            results['nested_subquery'] = time.time() - start_time
            results['nested_subquery_rows'] = len(rows)
            print(f"Completed Nested Subquery in {results['nested_subquery']:.4f} seconds")
            
            # Transaction - Batch Insert
            start_time = time.time()
            try:
                cursor.execute(f"""
                    CREATE TABLE {temp_grades_name} (
                        id NUMBER PRIMARY KEY, 
                        value VARCHAR2(2),
                        award_date DATE,
                        student_id NUMBER,
                        subject_id NUMBER,
                        teacher_id NUMBER
                    )
                """)
                
                # Pobierz istniejące ID studentów i przedmiotów - 20% studentów, wszystkie przedmioty
                cursor.execute(f"SELECT id FROM students WHERE rownum <= {students_limit}")
                student_ids = [row[0] for row in cursor.fetchall()]
                
                cursor.execute(f"SELECT id FROM subjects WHERE rownum <= {subjects_limit}")
                subject_ids = [row[0] for row in cursor.fetchall()]
                
                # Insert data - 10-15% kombinacji student-przedmiot
                max_inserts = int(0.15 * students_limit * subjects_limit)
                insert_count = min(max_inserts, 2000)
                
                if student_ids and subject_ids:
                    for i in range(insert_count):
                        student_id = student_ids[i % len(student_ids)]
                        subject_id = subject_ids[i % len(subject_ids)]
                        
                        cursor.execute(f"""
                            INSERT INTO {temp_grades_name} (id, value, award_date, student_id, subject_id, teacher_id)
                            VALUES (:1, :2, SYSDATE, :3, :4, 1)
                        """, (i+1, 'A', student_id, subject_id))
                
                conn.commit()
                
                # Clean up
                cursor.execute(f"DROP TABLE {temp_grades_name} PURGE")
                conn.commit()
                
                results['batch_insert'] = time.time() - start_time
                results['batch_insert_rows'] = insert_count
                print(f"Completed Transaction - Batch Insert in {results['batch_insert']:.4f} seconds")
            except Exception as e:
                print(f"Error in Transaction - Batch Insert: {str(e)}")
                if hasattr(e, 'help'):
                    print(f"Help: {e.help}")
                results['batch_insert'] = f"Error: {str(e)}"
                try_cleanup_table(conn, temp_grades_name)
            
            # Transaction - Batch Update
            update_limit = int(total_students * 0.2)
            start_time = time.time()
            try:
                cursor.execute(f"""
                    CREATE TABLE {temp_students_name} (
                        id NUMBER PRIMARY KEY,
                        name VARCHAR2(100),
                        gender CHAR(1),
                        house_id NUMBER,
                        dormitory_id NUMBER
                    )
                """)
                
                # Copy data from students - use ~20% of students
                cursor.execute(f"""
                    INSERT INTO {temp_students_name} (id, name, gender, house_id, dormitory_id)
                    SELECT id, name, gender, house_id, dormitory_id 
                    FROM students
                    WHERE rownum <= {update_limit}
                """)
                
                # Get count of inserted rows
                cursor.execute(f"SELECT COUNT(*) FROM {temp_students_name}")
                update_row_count = cursor.fetchone()[0]
                
                # Update batch of records
                cursor.execute(f"""
                    UPDATE {temp_students_name} 
                    SET gender = gender
                """)
                
                conn.commit()
                # Clean up
                cursor.execute(f"DROP TABLE {temp_students_name} PURGE")
                conn.commit()
                
                results['batch_update'] = time.time() - start_time
                results['batch_update_rows'] = update_row_count
                print(f"Completed Transaction - Batch Update in {results['batch_update']:.4f} seconds")
            except Exception as e:
                print(f"Error in Transaction - Batch Update: {str(e)}")
                if hasattr(e, 'help'):
                    print(f"Help: {e.help}")
                results['batch_update'] = f"Error: {str(e)}"
                try_cleanup_table(conn, temp_students_name)
            
            # Transaction - Complex Delete
            delete_limit = int(total_grades * 0.15)
            start_time = time.time()
            try:
                cursor.execute(f"""
                    CREATE TABLE {temp_delete_name} (
                        id NUMBER PRIMARY KEY,
                        value VARCHAR2(2),
                        award_date DATE,
                        student_id NUMBER,
                        subject_id NUMBER,
                        teacher_id NUMBER
                    )
                """)
                
                # Copy data from grades - use ~15% of grades
                cursor.execute(f"""
                    INSERT INTO {temp_delete_name} (id, value, award_date, student_id, subject_id, teacher_id)
                    SELECT id, value, award_date, student_id, subject_id, teacher_id 
                    FROM grades
                    WHERE rownum <= {delete_limit}
                """)
                
                # Get count of inserted rows
                cursor.execute(f"SELECT COUNT(*) FROM {temp_delete_name}")
                initial_row_count = cursor.fetchone()[0]
                
                # Complex delete operation
                cursor.execute(f"""
                    DELETE FROM {temp_delete_name}
                    WHERE student_id IN (
                        SELECT student_id FROM {temp_delete_name}
                        WHERE value = 'P'
                    )
                """)
                
                deleted_rows = cursor.rowcount
                conn.commit()
                
                # Clean up
                cursor.execute(f"DROP TABLE {temp_delete_name} PURGE")
                conn.commit()
                
                results['complex_delete'] = time.time() - start_time
                results['complex_delete_rows'] = deleted_rows if deleted_rows else 0
                print(f"Completed Transaction - Complex Delete in {results['complex_delete']:.4f} seconds")
            except Exception as e:
                print(f"Error in Transaction - Complex Delete: {str(e)}")
                if hasattr(e, 'help'):
                    print(f"Help: {e.help}")
                results['complex_delete'] = f"Error: {str(e)}"
                try_cleanup_table(conn, temp_delete_name)
            
            # Full Table Scan Analysis
            start_time = time.time()
            cursor.execute("""
                SELECT h.name, COUNT(*) as student_count, AVG(CASE 
                    WHEN g.value = 'O' THEN 6
                    WHEN g.value = 'E' THEN 5
                    WHEN g.value = 'A' THEN 4
                    WHEN g.value = 'P' THEN 3
                    WHEN g.value = 'D' THEN 2
                    WHEN g.value = 'T' THEN 1
                    ELSE 0
                END) as avg_grade
                FROM houses h
                LEFT JOIN students s ON h.id = s.house_id
                LEFT JOIN grades g ON s.id = g.student_id
                GROUP BY h.name
            """)
            rows = cursor.fetchall()
            results['full_table_scan'] = time.time() - start_time
            results['full_table_scan_rows'] = len(rows)
            print(f"Completed Full Table Scan Analysis in {results['full_table_scan']:.4f} seconds")
            
    except Exception as e:
        print(f"Error in performance analysis: {str(e)}")
        if hasattr(e, 'help'):
            print(f"Help: {e.help}")
        results['error'] = str(e)
    
    return results

def cleanup_temp_tables(conn, table_names):
    """Bezpieczne czyszczenie tabel tymczasowych"""
    cursor = conn.cursor()
    for table_name in table_names:
        try:
            cursor.execute(f"DROP TABLE {table_name} PURGE")
            conn.commit()
        except:
            pass

def try_cleanup_table(conn, table_name):
    """Próba usunięcia tabeli tymczasowej"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"DROP TABLE {table_name} PURGE")
        conn.commit()
    except:
        pass

def ensure_sequences():
    """Ensure all required sequences exist in the database."""
    try:
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            # Create sequences if they don't exist
            sequences = [
                ('teachers_seq', 1, 1000),
                ('houses_seq', 1, 10),
                ('dormitories_seq', 1, 200),
                ('students_seq', 1, 20000),
                ('subjects_seq', 1, 100),
                ('grades_seq', 1, 1000000),
                ('points_seq', 1, 50000),
                ('quidditch_seq', 1, 100)
            ]
            
            for seq_name, start_val, max_val in sequences:
                try:
                    cursor.execute(f"""
                        CREATE SEQUENCE {seq_name}
                        START WITH {start_val}
                        MAXVALUE {max_val}
                        NOCACHE
                        NOCYCLE
                    """)
                    print(f"Created sequence {seq_name}")
                except Exception as e:
                    if "ORA-00955" in str(e):  # Sequence already exists
                        print(f"Sequence {seq_name} already exists")
                    else:
                        raise e
            
            conn.commit()
            print("All sequences created successfully")
            
    except Exception as e:
        print(f"Error creating sequences: {str(e)}")
        raise e

if __name__ == "__main__":
    run_workload()
    ensure_sequences()
    results = run_performance_analysis()
    print("\nPerformance Analysis Results:")
    for test, time_taken in results.items():
        if test != 'error':
            print(f"{test}: {time_taken:.4f} seconds") 