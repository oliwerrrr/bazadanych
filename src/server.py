from flask import Flask, request, jsonify, send_from_directory, render_template_string
import oracledb
from visualization.visualize_data import run_performance_analysis, generate_html_report, get_table_stats
import json
import os
import sys
import subprocess
import shutil
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')
DATA_DIR = os.path.join(BASE_DIR, 'data')
VISUALIZATIONS_DIR = os.path.join(DOCS_DIR, 'visualizations')

def ensure_directories():
    """Create necessary directories if they don't exist"""
    os.makedirs(DOCS_DIR, exist_ok=True)
    os.makedirs(VISUALIZATIONS_DIR, exist_ok=True)
    os.makedirs(DATA_DIR, exist_ok=True)

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
    ensure_directories()
    if os.path.exists(os.path.join(DOCS_DIR, 'hogwarts_report.html')):
        return send_from_directory(DOCS_DIR, 'hogwarts_report.html')
    return jsonify({"error": "Report file not found"}), 404

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files from docs directory"""
    if os.path.exists(os.path.join(DOCS_DIR, filename)):
        return send_from_directory(DOCS_DIR, filename)
    return jsonify({"error": f"File {filename} not found"}), 404

@app.route('/run_tests', methods=['POST'])
def run_tests():
    try:
        config = request.json
        connection = get_db_connection()
        cursor = connection.cursor()
        
        stats = {
            'teachers': get_table_stats(cursor, 'teachers'),
            'houses': get_table_stats(cursor, 'houses'),
            'dormitories': get_table_stats(cursor, 'dormitories'),
            'students': get_table_stats(cursor, 'students'),
            'subjects': get_table_stats(cursor, 'subjects'),
            'grades': get_table_stats(cursor, 'grades'),
            'points': get_table_stats(cursor, 'points'),
            'quidditch': get_table_stats(cursor, 'quidditch_team_members')
        }
        
        performance_results = run_performance_analysis(cursor, config)
        generate_html_report(stats, performance_results)
        
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success", 
            "message": "Tests completed successfully",
            "loading_message": get_loading_message()
        })
    except Exception as e:
        print(f"Error in run_tests: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_config', methods=['POST'])
def generate_config():
    try:
        config_data = request.json or {}  # Use empty dict if no JSON provided
        
        # Add default values if not provided
        default_config = {
            "nTeachers": 111,
            "nStudents": 10000,
            "pointsPerStudent": 3,
            "female_percentage": 50,
            "min_teacher_birth_year": 1950,
            "max_teacher_birth_year": 1990,
            "min_student_birth_year": 2006,
            "max_student_birth_year": 2013,
            "min_captain_year": 5,
            "min_team_size": 7,
            "max_team_size": 12,
            "min_classroom": 100,
            "max_classroom": 999,
            "min_grades_per_subject": 2,
            "max_grades_per_subject": 10,
            "min_points": -50,
            "max_points": 50,
            "grade_values": ["O", "E", "A", "P", "D", "T"],
            "house_names": ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"],
            "house_symbols": ["Lion", "Badger", "Eagle", "Snake"]
        }
        
        # Update with provided values
        config_data = {**default_config, **(config_data or {})}
        
        config_path = os.path.join(BASE_DIR, 'hogwarts_config.json')
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4)
        
        return jsonify({
            "status": "success", 
            "message": "Configuration saved",
            "loading_message": get_loading_message()
        })
    except Exception as e:
        print(f"Error in generate_config: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/generate_data', methods=['POST'])
def generate_data():
    try:
        ensure_directories()
        script_path = os.path.join(BASE_DIR, 'generate_hogwarts_data.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR
        )
        
        print(f"Generate data output: {result.stdout}")
        if result.stderr:
            print(f"Generate data errors: {result.stderr}")
            
        return jsonify({
            "status": "success", 
            "message": "Data generated successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in generate_data: {str(e)}")
        print(f"Process output: {e.output}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in generate_data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/import_data', methods=['POST'])
def import_data():
    try:
        ensure_directories()
        script_path = os.path.join(BASE_DIR, 'import_data.py')
        if not os.path.exists(script_path):
            raise Exception(f"Script not found: {script_path}")
            
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            check=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        
        print(f"Import data output: {result.stdout}")
        if result.stderr:
            print(f"Import data errors: {result.stderr}")
            
        return jsonify({
            "status": "success", 
            "message": "Data imported successfully",
            "loading_message": get_loading_message()
        })
    except subprocess.CalledProcessError as e:
        print(f"Error in import_data: {str(e)}")
        print(f"Process output: {e.output}")
        return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        print(f"Error in import_data: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/clear_database', methods=['POST'])
def clear_database():
    try:
        connection = oracledb.connect("SYSTEM/admin@localhost:1521/XE")
        cursor = connection.cursor()
        
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
            cursor.execute(f"DELETE FROM {table}")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return jsonify({
            "status": "success", 
            "message": "Database cleared successfully",
            "loading_message": get_loading_message()
        })
    except Exception as e:
        print(f"Error in clear_database: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.route('/docs/<path:filename>')
def serve_docs(filename):
    """Serve files from docs directory"""
    if os.path.exists(os.path.join(DOCS_DIR, filename)):
        return send_from_directory(DOCS_DIR, filename)
    return jsonify({"error": f"File {filename} not found"}), 404

@app.route('/visualizations/<path:filename>')
def serve_visualizations(filename):
    """Serve files from visualizations directory"""
    if os.path.exists(os.path.join(VISUALIZATIONS_DIR, filename)):
        return send_from_directory(VISUALIZATIONS_DIR, filename)
    return jsonify({"error": f"File {filename} not found"}), 404

if __name__ == '__main__':
    # Create necessary directories and copy files
    ensure_directories()
    copy_schema_files()
    
    print(f"Serving files from: {DOCS_DIR}")
    print(f"Visualizations from: {VISUALIZATIONS_DIR}")
    app.run(port=5000, debug=True) 