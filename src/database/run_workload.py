import cx_Oracle
import json
from datetime import datetime
import os
import sys
import time

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
            
            # Simple SELECT
            start_time = time.time()
            cursor.execute("SELECT * FROM students WHERE rownum <= 100")
            cursor.fetchall()
            results['simple_select'] = time.time() - start_time
            print(f"Completed Simple SELECT in {results['simple_select']:.4f} seconds")
            
            # Complex JOIN
            start_time = time.time()
            cursor.execute("""
                SELECT s.name, h.name as house_name 
                FROM students s 
                JOIN houses h ON s.house_id = h.id 
                WHERE rownum <= 100
            """)
            cursor.fetchall()
            results['complex_join'] = time.time() - start_time
            print(f"Completed Complex JOIN in {results['complex_join']:.4f} seconds")
            
            # Aggregation
            start_time = time.time()
            cursor.execute("""
                SELECT h.name, COUNT(*) as student_count 
                FROM students s 
                JOIN houses h ON s.house_id = h.id 
                GROUP BY h.name
            """)
            cursor.fetchall()
            results['aggregation'] = time.time() - start_time
            print(f"Completed Aggregation in {results['aggregation']:.4f} seconds")
            
            # Nested Subquery
            start_time = time.time()
            cursor.execute("""
                SELECT name FROM students 
                WHERE id IN (
                    SELECT student_id FROM grades 
                    WHERE grade = 5 
                    AND rownum <= 100
                )
            """)
            cursor.fetchall()
            results['nested_subquery'] = time.time() - start_time
            print(f"Completed Nested Subquery in {results['nested_subquery']:.4f} seconds")
            
            # Batch Update
            start_time = time.time()
            cursor.execute("""
                UPDATE students 
                SET points = points + 10 
                WHERE house_id = 1 
                AND rownum <= 100
            """)
            conn.commit()
            results['batch_update'] = time.time() - start_time
            print(f"Completed Transaction - Batch Update in {results['batch_update']:.4f} seconds")
            
            # Complex Delete
            start_time = time.time()
            cursor.execute("""
                DELETE FROM grades 
                WHERE student_id IN (
                    SELECT id FROM students 
                    WHERE house_id = 1 
                    AND rownum <= 100
                )
            """)
            conn.commit()
            results['complex_delete'] = time.time() - start_time
            print(f"Completed Transaction - Complex Delete in {results['complex_delete']:.4f} seconds")
            
            # Full Table Scan Analysis
            start_time = time.time()
            cursor.execute("""
                SELECT h.name, COUNT(*) as student_count, AVG(g.grade) as avg_grade
                FROM students s
                JOIN houses h ON s.house_id = h.id
                LEFT JOIN grades g ON s.id = g.student_id
                GROUP BY h.name
            """)
            cursor.fetchall()
            results['full_table_scan'] = time.time() - start_time
            print(f"Completed Full Table Scan Analysis in {results['full_table_scan']:.4f} seconds")
            
    except Exception as e:
        print(f"Error in performance analysis: {str(e)}")
        results['error'] = str(e)
    
    return results

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