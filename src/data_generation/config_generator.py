import json
import os
from datetime import datetime
import sys

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'config', 'hogwarts_config.json')

def debug_print(message):
    """Print debug message with timestamp"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")

def get_int_input(prompt, default, min_value=1, max_value=None):
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            value = int(value)
            if value < min_value:
                print(f"Please enter a number greater than or equal to {min_value}.")
                continue
            if max_value is not None and value > max_value:
                print(f"Please enter a number less than or equal to {max_value}.")
                continue
            return value
        except ValueError:
            print("Please enter a valid number.")

def get_range_input(prompt, min_default, max_default, absolute_min=None, absolute_max=None):
    while True:
        try:
            min_value = input(f"{prompt} (min) [{min_default}]: ").strip()
            if not min_value:
                min_value = min_default
            else:
                min_value = int(min_value)
                if absolute_min is not None and min_value < absolute_min:
                    print(f"Minimum value must be at least {absolute_min}.")
                    continue
            
            max_value = input(f"{prompt} (max) [{max_default}]: ").strip()
            if not max_value:
                max_value = max_default
            else:
                max_value = int(max_value)
                if absolute_max is not None and max_value > absolute_max:
                    print(f"Maximum value must be at most {absolute_max}.")
                    continue
            
            if min_value <= max_value:
                return min_value, max_value
            print("Minimum value must be less than or equal to maximum value.")
        except ValueError:
            print("Please enter valid numbers.")

def get_yes_no_input(prompt, default=True):
    while True:
        value = input(f"{prompt} [{'Y/n' if default else 'y/N'}]: ").strip().lower()
        if not value:
            return default
        if value in ['y', 'yes']:
            return True
        if value in ['n', 'no']:
            return False
        print("Please enter 'y' or 'n'.")

def main():
    try:
        debug_print("Starting configuration generator...")
        
        print("\nHogwarts Data Generator Configuration")
        print("=====================================")
        
        # Basic configuration
        config = {
            "nTeachers": get_int_input("Number of teachers", 111, min_value=1),
            "nStudents": get_int_input("Number of students", 10000, min_value=1),
            "female_percentage": get_int_input("Percentage of female students", 50, min_value=0, max_value=100),
            
            # Birth years
            "min_teacher_birth_year": get_int_input("Minimum teacher birth year", 1950, min_value=1900),
            "max_teacher_birth_year": get_int_input("Maximum teacher birth year", 1990),
            "min_student_birth_year": get_int_input("Minimum student birth year", 2006),
            "max_student_birth_year": get_int_input("Maximum student birth year", 2013),
            
            # Classroom numbers
            "min_classroom": get_int_input("Minimum classroom number", 100, min_value=1),
            "max_classroom": get_int_input("Maximum classroom number", 999),
            
            # Grades configuration
            "grade_values": ["O", "E", "A", "P", "D", "T"],  # Standard Hogwarts grades
            "min_grades_per_subject": get_int_input("Minimum grades per subject", 2, min_value=0),
            "max_grades_per_subject": get_int_input("Maximum grades per subject", 10),
            
            # Points configuration
            "min_points": get_int_input("Minimum points per action", -50),
            "max_points": get_int_input("Maximum points per action", 50),
            "pointsPerStudent": get_int_input("Average points actions per student", 3, min_value=0),
            
            # Quidditch configuration
            "min_team_size": get_int_input("Minimum Quidditch team size", 7, min_value=7),
            "max_team_size": get_int_input("Maximum Quidditch team size", 12, min_value=7),
            "min_captain_year": get_int_input("Minimum year for Quidditch captain", 5, min_value=3, max_value=7),
            
            # House configuration
            "house_names": ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"],
            "house_symbols": ["Lion", "Badger", "Eagle", "Snake"],
            
            # Advanced options
            "allow_empty_dormitories": get_yes_no_input("Allow empty dormitories", False),
            "enforce_min_subjects": get_yes_no_input("Enforce minimum subjects per student", True),
            "allow_multiple_captains": get_yes_no_input("Allow multiple Quidditch captains per house", False),
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Validate configuration
        if config['min_teacher_birth_year'] >= config['max_teacher_birth_year']:
            raise ValueError("Teacher birth year range is invalid")
        if config['min_student_birth_year'] >= config['max_student_birth_year']:
            raise ValueError("Student birth year range is invalid")
        if config['min_classroom'] >= config['max_classroom']:
            raise ValueError("Classroom number range is invalid")
        if config['min_grades_per_subject'] > config['max_grades_per_subject']:
            raise ValueError("Grades per subject range is invalid")
        if config['min_points'] > config['max_points']:
            raise ValueError("Points range is invalid")
        if config['min_team_size'] > config['max_team_size']:
            raise ValueError("Quidditch team size range is invalid")
        
        # Save configuration
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
        
        debug_print(f"Configuration saved to {CONFIG_FILE}")
        
        print("\nConfiguration Summary:")
        print("=====================")
        print(f"Teachers: {config['nTeachers']}")
        print(f"Students: {config['nStudents']}")
        print(f"Female students: {config['female_percentage']}%")
        print(f"Teacher birth years: {config['min_teacher_birth_year']}-{config['max_teacher_birth_year']}")
        print(f"Student birth years: {config['min_student_birth_year']}-{config['max_student_birth_year']}")
        print(f"Classrooms: {config['min_classroom']}-{config['max_classroom']}")
        print(f"Grades: {', '.join(config['grade_values'])}")
        print(f"Grades per subject: {config['min_grades_per_subject']}-{config['max_grades_per_subject']}")
        print(f"Points range: {config['min_points']}-{config['max_points']}")
        print(f"Points actions per student: {config['pointsPerStudent']}")
        print(f"Quidditch team size: {config['min_team_size']}-{config['max_team_size']}")
        print(f"Minimum captain year: {config['min_captain_year']}")
        print("\nAdvanced Settings:")
        print(f"- Allow empty dormitories: {'Yes' if config['allow_empty_dormitories'] else 'No'}")
        print(f"- Enforce minimum subjects: {'Yes' if config['enforce_min_subjects'] else 'No'}")
        print(f"- Allow multiple captains: {'Yes' if config['allow_multiple_captains'] else 'No'}")
        
        debug_print("Configuration generator completed successfully")
        
    except KeyboardInterrupt:
        print("\nConfiguration generator interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 