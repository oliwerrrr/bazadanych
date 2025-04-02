import os
import json
import subprocess
from datetime import datetime
import sys

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'hogwarts_config.json')

def debug_print(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data is not None:
        print(f"Data: {data}")

def get_int_input(prompt, default=None):
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value and default is not None:
                return default
            value = int(value)
            if value <= 0:
                print("Value must be greater than 0!")
                continue
            return value
        except ValueError:
            print("Please enter a valid number!")

def get_range_input(prompt, default_min=None, default_max=None):
    while True:
        try:
            min_value = input(f"{prompt} (min) [{default_min}]: ").strip()
            if not min_value and default_min is not None:
                min_value = default_min
            else:
                min_value = int(min_value)
            
            max_value = input(f"{prompt} (max) [{default_max}]: ").strip()
            if not max_value and default_max is not None:
                max_value = default_max
            else:
                max_value = int(max_value)
            
            if min_value > max_value:
                print("Minimum value cannot be greater than maximum value!")
                continue
            return min_value, max_value
        except ValueError:
            print("Please enter valid numbers!")

def create_config():
    debug_print("Starting Hogwarts Data Generator Configuration")
    
    # Database configuration
    print("\nDatabase Configuration:")
    db_host = input("Database host [localhost]: ").strip() or "localhost"
    db_port = input("Database port [1521]: ").strip() or "1521"
    db_service = input("Database service name [XE]: ").strip() or "XE"
    db_user = input("Database username [SYSTEM]: ").strip() or "SYSTEM"
    db_password = input("Database password [admin]: ").strip() or "admin"
    
    # Data generation configuration
    print("\nData Generation Configuration:")
    n_teachers = get_int_input("Number of teachers", 111)
    n_students = get_int_input("Number of students", 10000)
    
    # Gender distribution
    print("\nGender Distribution:")
    female_percentage = get_int_input("Percentage of female students", 50)
    if female_percentage > 100:
        female_percentage = 100
    if female_percentage < 0:
        female_percentage = 0
    
    # Birth year ranges
    print("\nBirth Year Ranges:")
    teacher_birth_years = get_range_input("Teacher birth years", 1950, 1990)
    student_birth_years = get_range_input("Student birth years", 2007, 2013)
    
    # Classroom configuration
    print("\nClassroom Configuration:")
    classroom_range = get_range_input("Classroom numbers", 101, 999)
    
    # Grades configuration
    print("\nGrades Configuration:")
    grades_per_subject = get_range_input("Number of grades per subject", 3, 5)
    grade_values = ["O", "E", "A", "P", "D", "T"]  # Standard Hogwarts grades
    
    # Points configuration
    print("\nPoints Configuration:")
    points_per_student = get_int_input("Average points per student", 3)
    points_range = get_range_input("Points range", -50, 50)
    
    # Quidditch configuration
    print("\nQuidditch Configuration:")
    team_size_range = get_range_input("Quidditch team size", 7, 10)
    min_captain_year = get_int_input("Minimum year for team captain", 5)
    
    # Create configuration dictionary
    config = {
        "database": {
            "host": db_host,
            "port": db_port,
            "service": db_service,
            "user": db_user,
            "password": db_password
        },
        "nTeachers": n_teachers,
        "nStudents": n_students,
        "female_percentage": female_percentage,
        "house_names": ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"],
        "house_symbols": ["Lion", "Snake", "Badger", "Eagle"],
        "grade_values": grade_values,
        "min_teacher_birth_year": teacher_birth_years[0],
        "max_teacher_birth_year": teacher_birth_years[1],
        "min_student_birth_year": student_birth_years[0],
        "max_student_birth_year": student_birth_years[1],
        "min_classroom": classroom_range[0],
        "max_classroom": classroom_range[1],
        "min_grades_per_subject": grades_per_subject[0],
        "max_grades_per_subject": grades_per_subject[1],
        "points_per_student": points_per_student,
        "min_points": points_range[0],
        "max_points": points_range[1],
        "min_team_size": team_size_range[0],
        "max_team_size": team_size_range[1],
        "min_captain_year": min_captain_year
    }
    
    # Save configuration
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)
    
    debug_print("Configuration saved to hogwarts_config.json")
    return config

def run_script(script_name, description):
    debug_print(f"Running {description}...")
    try:
        script_path = os.path.join(BASE_DIR, script_name)
        result = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=BASE_DIR,
            env={**os.environ, 'PYTHONPATH': BASE_DIR}
        )
        if result.returncode == 0:
            debug_print(f"{description} completed successfully")
            print(result.stdout)
        else:
            debug_print(f"Error in {description}:")
            print(result.stderr)
            return False
        return True
    except Exception as e:
        debug_print(f"Error running {description}: {str(e)}")
        return False

def main():
    try:
        # Step 1: Create configuration
        config = create_config()
        
        # Step 2: Generate data
        if not run_script('generate_hogwarts_data.py', 'Data generation'):
            return
        
        # Step 3: Import data to database
        if not run_script('import_data.py', 'Database import'):
            return
        
        # Step 4: Generate visualizations
        if not run_script('visualize_data.py', 'Visualization generation'):
            return
        
        # Step 5: Open report
        if not run_script('open_report.py', 'Opening report'):
            return
        
        debug_print("All steps completed successfully!")
        
    except Exception as e:
        debug_print(f"Error in main process: {str(e)}")
        return

if __name__ == "__main__":
    main() 