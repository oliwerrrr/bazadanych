from flask import Flask, request, jsonify, send_from_directory, render_template
import oracledb
from visualization.visualize_data import run_performance_analysis, generate_html_report, get_table_stats
import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import time
import uuid

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)), 'docs'))
CORS(app)  # Enable CORS for all routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Enable WebSocket with CORS

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATABASE_DIR = os.path.join(BASE_DIR, 'src', 'database')
DATA_DIR = os.path.join(BASE_DIR, 'data', 'hogwarts_data')
VISUALIZATIONS_DIR = os.path.join(DOCS_DIR, 'visualizations')

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(DATABASE_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(os.path.join(DOCS_DIR, 'visualizations'), exist_ok=True)

def copy_schema_files():
    """Copy schema files to docs directory"""
    schema_files = ['schema.png', 'HogwartRelations.png']
    for file in schema_files:
        src = os.path.join(DOCS_DIR, file)
        dst = os.path.join(DOCS_DIR, file)
        if os.path.exists(src):
            if src != dst:
                shutil.copy2(src, dst)
            print(f"Found {file} in docs directory")
        else:
            print(f"Warning: {file} not found in {DOCS_DIR}")

# Zabawne wiadomości podczas operacji
LOADING_MESSAGES = [
    "🧙‍♂️ Rzucam zaklęcie generowania danych...",
    "🪄 Wingardium Leviosa! Podnoszę dane do bazy...",
    "🎩 Wyciągam dane z magicznego kapelusza...",
    "🦉 Hedwiga dostarcza nowe rekordy...",
    "🧪 Mieszam eliksir w bazie danych...",
    "🏰 Hogwart przetwarza twoje żądanie...",
    "⚡ Błyskawiczne przetwarzanie danych...",
    "🐍 Bazyliszek czyści bazę danych...",
    "🧹 Zamiatam stare dane Nimbusem 2000...",
    "🎭 Evanesco! Usuwam niepotrzebne rekordy..."
]

def get_loading_message():
    import random
    return random.choice(LOADING_MESSAGES)

def get_db_connection():
    """Get database connection with proper error handling"""
    try:
        connection = oracledb.connect("SYSTEM/admin@localhost:1521/XE")
        print("Database connection successful")
        return connection
    except oracledb.Error as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

@app.after_request
def after_request(response):
    """Add CORS headers to all responses"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@app.route('/')
def index():
    """Serve the main page"""
    try:
        return render_template('hogwarts_report.html')
    except Exception as e:
        print(f"Error serving index: {str(e)}")
        return str(e), 500

@app.route('/<path:filename>')
def serve_file(filename):
    """Serve static files from docs directory"""
    file_path = os.path.join(DOCS_DIR, filename)
    if os.path.exists(file_path):
        return send_from_directory(DOCS_DIR, filename)
    return "File not found", 404

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    emit('status', {'data': 'Connected to server'})

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

def emit_progress(message, data=None):
    """Emit progress updates to connected clients"""
    socketio.emit('progress', {
        'message': message,
        'data': data,
        'timestamp': datetime.now().isoformat(),
        'type': 'progress'  # Add type to distinguish progress messages
    })

@app.route('/run_tests')
def run_tests():
    try:
        # Utwórz pusty obiekt dla wyników
        results = {
            'status': 'success',
            'stats': {},
            'performance': {}
        }
        
        # Load database statistics
        with get_db_connection() as conn:
            cursor = conn.cursor()
            for table in ['teachers', 'houses', 'dormitories', 'students', 'subjects', 'grades', 'points', 'quidditch_team_members']:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    count = cursor.fetchone()[0]
                    results['stats'][table] = count
                    print(f"Got stats for table {table}: {count}")
                except Exception as e:
                    print(f"Error getting stats for {table}: {str(e)}")
                    results['stats'][table] = 0

        # Run performance analysis
        print("Running performance analysis...")
        # Uruchom testy wydajnościowe i od razu zapisz wyniki
        results['performance'] = run_performance_analysis()
        
        # Upewnij się, że wszystkie klucze są obecne
        for key in ['simple_select', 'complex_join', 'aggregation', 'nested_subquery', 
                   'batch_insert', 'batch_update', 'complex_delete', 'full_table_scan']:
            if key not in results['performance']:
                results['performance'][key] = 0
                results['performance'][f'{key}_rows'] = 0
        
        return jsonify(results)
    except Exception as e:
        print(f"Error in run_tests: {str(e)}")
        return jsonify({'status': 'error', 'message': str(e)}), 500

def run_performance_analysis():
    results = {}
    try:
        with get_db_connection() as conn:
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
            print(f"Completed Simple SELECT in {results['simple_select']:.4f} seconds, {results['simple_select_rows']} rows")
            
            # Complex JOIN
            start_time = time.time()
            cursor.execute(f"""
                SELECT s.name, h.name as house_name, g.value as grade
                FROM students s 
                JOIN houses h ON s.house_id = h.id 
                JOIN grades g ON s.id = g.student_id
                WHERE rownum <= {int(total_students * 0.3)}
            """)
            rows = cursor.fetchall()
            results['complex_join'] = time.time() - start_time
            results['complex_join_rows'] = len(rows)
            print(f"Completed Complex JOIN in {results['complex_join']:.4f} seconds, {results['complex_join_rows']} rows")
            
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
            print(f"Completed Aggregation in {results['aggregation']:.4f} seconds, {results['aggregation_rows']} rows")
            
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
            print(f"Completed Nested Subquery in {results['nested_subquery']:.4f} seconds, {results['nested_subquery_rows']} rows")
            
            # Transaction - Batch Insert
            start_time = time.time()
            try:
                # Utwórz zwykłą tabelę zamiast tymczasowej
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
                
                # Commit the transaction
                conn.commit()
                # Clean up
                cursor.execute(f"DROP TABLE {temp_grades_name} PURGE")
                conn.commit()
                
                results['batch_insert'] = time.time() - start_time
                results['batch_insert_rows'] = insert_count
                print(f"Completed Transaction - Batch Insert in {results['batch_insert']:.4f} seconds, {insert_count} rows")
            except Exception as e:
                print(f"Error in Transaction - Batch Insert: {str(e)}")
                results['batch_insert'] = f"Error: {str(e)}"
                results['batch_insert_rows'] = 0
                try_cleanup_table(conn, temp_grades_name)
            
            # Transaction - Batch Update
            update_limit = int(total_students * 0.2)
            start_time = time.time()
            try:
                # Utwórz zwykłą tabelę zamiast tymczasowej
                cursor.execute(f"""
                    CREATE TABLE {temp_students_name} (
                        id NUMBER PRIMARY KEY,
                        name VARCHAR2(100),
                        gender CHAR(1),
                        house_id NUMBER,
                        dormitory_id NUMBER
                    )
                """)
                
                # Copy students for testing - use ~20% of students
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
                print(f"Completed Transaction - Batch Update in {results['batch_update']:.4f} seconds, {update_row_count} rows")
            except Exception as e:
                print(f"Error in Transaction - Batch Update: {str(e)}")
                results['batch_update'] = f"Error: {str(e)}"
                results['batch_update_rows'] = 0
                try_cleanup_table(conn, temp_students_name)
            
            # Transaction - Complex Delete
            delete_limit = int(total_grades * 0.15)
            start_time = time.time()
            try:
                # Utwórz zwykłą tabelę zamiast tymczasowej
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
                
                # Copy grades for testing - use ~15% of grades
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
                results['complex_delete_rows'] = deleted_rows if deleted_rows is not None else 0
                print(f"Completed Transaction - Complex Delete in {results['complex_delete']:.4f} seconds, {results['complex_delete_rows']} rows (from {initial_row_count})")
            except Exception as e:
                print(f"Error in Transaction - Complex Delete: {str(e)}")
                results['complex_delete'] = f"Error: {str(e)}"
                results['complex_delete_rows'] = 0
                try_cleanup_table(conn, temp_delete_name)
            
            # Full Table Scan Analysis
            start_time = time.time()
            try:
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
                print(f"Completed Full Table Scan Analysis in {results['full_table_scan']:.4f} seconds, {results['full_table_scan_rows']} rows")
            except Exception as e:
                print(f"Error during Full Table Scan: {str(e)}")
                results['full_table_scan'] = f"Error: {str(e)}"
                results['full_table_scan_rows'] = 0
            
    except Exception as e:
        print(f"Error in performance analysis: {str(e)}")
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

@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        ensure_directories()
        script_path = os.path.join(BASE_DIR, 'src', 'data_generation', 'config_generator.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Generating configuration...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Config generation output: {result.stdout}")
        if result.stderr:
            print(f"Config generation errors: {result.stderr}")
            
        emit_progress("Configuration generated successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Configuration generated successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in generate_config: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in generate_config: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_data')
def generate_data():
    try:
        script_path = os.path.join(DATABASE_DIR, 'generate_data.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Generating data...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Data generation output: {result.stdout}")
        if result.stderr:
            print(f"Data generation errors: {result.stderr}")
            
        emit_progress("Data generated successfully")
            
        return jsonify({
            "status": "success", 
            "message": "Data generated successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in generate_data: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in generate_data: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/import_data')
def import_data():
    try:
        script_path = os.path.join(DATABASE_DIR, 'import_data.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Importing data...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Import output: {result.stdout}")
        if result.stderr:
            print(f"Import errors: {result.stderr}")
            
        emit_progress("Data imported successfully")
            
        return jsonify({
            "status": "success", 
            "message": "Data imported successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in import_data: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in import_data: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear_database', methods=['POST'])
def clear_database():
    try:
        ensure_directories()
        script_path = os.path.join(BASE_DIR, 'src', 'database', 'clear_database.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Clearing database...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Clear database output: {result.stdout}")
        if result.stderr:
            print(f"Clear database errors: {result.stderr}")
            
        emit_progress("Database cleared successfully")
        
        return jsonify({
            "status": "success", 
            "message": "Database cleared successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in clear_database: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in clear_database: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/docs/<path:filename>')
def serve_docs(filename):
    """Serve files from docs directory"""
    if os.path.exists(os.path.join(DOCS_DIR, filename)):
        return send_from_directory(DOCS_DIR, filename)
    return jsonify({"error": f"File {filename} not found"}), 404

@app.route('/visualizations/<path:filename>')
def serve_visualization(filename):
    """Serve visualization files"""
    file_path = os.path.join(DOCS_DIR, 'visualizations', filename)
    if os.path.exists(file_path):
        return send_from_directory(os.path.join(DOCS_DIR, 'visualizations'), filename)
    return "File not found", 404

@app.route('/run_workload')
def run_workload():
    try:
        script_path = os.path.join(DATABASE_DIR, 'run_workload.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Running workload...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Workload output: {result.stdout}")
        if result.stderr:
            print(f"Workload errors: {result.stderr}")
            
        emit_progress("Workload completed successfully")
            
        return jsonify({
            "status": "success", 
            "message": "Workload completed successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in run_workload: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in run_workload: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/visualize_data')
def visualize_data():
    try:
        script_path = os.path.join(DATABASE_DIR, 'visualize_data.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        emit_progress("Generating visualizations...")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Visualization output: {result.stdout}")
        if result.stderr:
            print(f"Visualization errors: {result.stderr}")
            
        emit_progress("Visualizations generated successfully")
            
        return jsonify({
            "status": "success", 
            "message": "Visualizations generated successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in visualize_data: {str(e)}")
        print(f"Process output: {e.output}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in visualize_data: {str(e)}")
        emit_progress(f"Error: {str(e)}", {'error': True})
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    ensure_directories()
    copy_schema_files()
    socketio.run(app, debug=True, port=5000) 