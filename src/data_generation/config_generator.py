import json
import os

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
CONFIG_FILE = os.path.join(BASE_DIR, 'hogwarts_config.json')

def get_int_input(prompt, default):
    while True:
        try:
            value = input(f"{prompt} [{default}]: ").strip()
            if not value:
                return default
            value = int(value)
            if value > 0:
                return value
            print("Please enter a positive number.")
        except ValueError:
            print("Please enter a valid number.")

def get_range_input(prompt, min_default, max_default):
    while True:
        try:
            min_value = input(f"{prompt} (min) [{min_default}]: ").strip()
            if not min_value:
                min_value = min_default
            else:
                min_value = int(min_value)
            
            max_value = input(f"{prompt} (max) [{max_default}]: ").strip()
            if not max_value:
                max_value = max_default
            else:
                max_value = int(max_value)
            
            if min_value <= max_value:
                return min_value, max_value
            print("Minimum value must be less than or equal to maximum value.")
        except ValueError:
            print("Please enter valid numbers.")

def main():
    print("\nHogwarts Data Generator Configuration")
    print("=====================================")
    
    config = {
        "nTeachers": get_int_input("Number of teachers", 100),
        "nStudents": get_int_input("Number of students", 10000),
        "min_teacher_birth_year": get_int_input("Minimum teacher birth year", 1960),
        "max_teacher_birth_year": get_int_input("Maximum teacher birth year", 1990),
        "min_student_birth_year": get_int_input("Minimum student birth year", 2000),
        "max_student_birth_year": get_int_input("Maximum student birth year", 2010),
        "min_classroom": get_int_input("Minimum classroom number", 101),
        "max_classroom": get_int_input("Maximum classroom number", 999),
        "grade_values": ["A", "B", "C", "D", "E", "F"],
        "min_grades_per_subject": get_int_input("Minimum grades per subject", 3),
        "max_grades_per_subject": get_int_input("Maximum grades per subject", 5),
        "min_points": get_int_input("Minimum points", -50),
        "max_points": get_int_input("Maximum points", 50),
        "points_per_student": get_int_input("Points per student", 10),
        "min_team_size": get_int_input("Minimum Quidditch team size", 7),
        "max_team_size": get_int_input("Maximum Quidditch team size", 7),
        "min_captain_year": get_int_input("Minimum year for Quidditch captain", 5),
        "female_percentage": get_int_input("Percentage of female students", 50),
        "house_names": ["Gryffindor", "Hufflepuff", "Ravenclaw", "Slytherin"],
        "house_symbols": ["Lion", "Badger", "Eagle", "Snake"]
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=4)
    
    print("\nConfiguration Summary:")
    print("=====================")
    print(f"Teachers: {config['nTeachers']}")
    print(f"Students: {config['nStudents']}")
    print(f"Teacher birth years: {config['min_teacher_birth_year']}-{config['max_teacher_birth_year']}")
    print(f"Student birth years: {config['min_student_birth_year']}-{config['max_student_birth_year']}")
    print(f"Classrooms: {config['min_classroom']}-{config['max_classroom']}")
    print(f"Grades per subject: {config['min_grades_per_subject']}-{config['max_grades_per_subject']}")
    print(f"Points range: {config['min_points']}-{config['max_points']}")
    print(f"Points per student: {config['points_per_student']}")
    print(f"Quidditch team size: {config['min_team_size']}-{config['max_team_size']}")
    print(f"Minimum captain year: {config['min_captain_year']}")
    print(f"Female students: {config['female_percentage']}%")
    
    print(f"\nConfiguration saved to {CONFIG_FILE}")

if __name__ == "__main__":
    main() 