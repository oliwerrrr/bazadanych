import json
import os

def get_int_input(prompt, default_value):
    while True:
        try:
            value = input(f"{prompt} [{default_value}]: ").strip()
            if not value:
                return default_value
            value = int(value)
            if value > 0:
                return value
            print("Value must be greater than 0!")
        except ValueError:
            print("Please enter a valid number!")

def get_range_input(prompt, default_min, default_max):
    while True:
        try:
            min_value = input(f"{prompt} (min) [{default_min}]: ").strip()
            if not min_value:
                min_value = default_min
            else:
                min_value = int(min_value)
            
            max_value = input(f"{prompt} (max) [{default_max}]: ").strip()
            if not max_value:
                max_value = default_max
            else:
                max_value = int(max_value)
            
            if min_value <= max_value:
                return min_value, max_value
            print("Minimum value must be less than or equal to maximum value!")
        except ValueError:
            print("Please enter valid numbers!")

def main():
    print("Hogwarts Data Generator Configuration")
    print("=====================================")
    
    config = {
        # Basic numbers
        'nTeachers': get_int_input("Number of teachers", 111),
        'nStudents': get_int_input("Number of students", 12137),
        
        # House parameters (fixed)
        'house_names': ["Gryffindor", "Slytherin", "Hufflepuff", "Ravenclaw"],
        'house_symbols': ["Lion", "Snake", "Badger", "Eagle"],
        
        # Grade parameters (fixed)
        'grade_values': ["O", "E", "A", "P", "D", "T"],
        
        # Date parameters
        'min_teacher_birth_year': get_int_input("Minimum teacher birth year", 1950),
        'max_teacher_birth_year': get_int_input("Maximum teacher birth year", 1990),
        'min_student_birth_year': get_int_input("Minimum student birth year", 2007),
        'max_student_birth_year': get_int_input("Maximum student birth year", 2013),
        
        # Subject parameters
        'min_classroom': get_int_input("Minimum classroom number", 1),
        'max_classroom': get_int_input("Maximum classroom number", 50),
        
        # Grade parameters
        'min_grades_per_subject': get_int_input("Minimum number of grades per subject", 2),
        'max_grades_per_subject': get_int_input("Maximum number of grades per subject", 5),
        
        # Points parameters
        'points_per_student': get_int_input("Average number of points per student", 3),
        'min_points': get_int_input("Minimum points value", -50),
        'max_points': get_int_input("Maximum points value", 50),
        
        # Quidditch team parameters
        'min_team_size': get_int_input("Minimum Quidditch team size", 6),
        'max_team_size': get_int_input("Maximum Quidditch team size", 10),
        'min_captain_year': get_int_input("Minimum year to be a team captain", 3)
    }
    
    # Save configuration to file
    with open('hogwarts_config.json', 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4, ensure_ascii=False)
    
    print("\nConfiguration has been saved to hogwarts_config.json")
    print("\nConfiguration Summary:")
    print(f"Number of teachers: {config['nTeachers']}")
    print(f"Number of students: {config['nStudents']}")
    print(f"Teacher birth year range: {config['min_teacher_birth_year']} - {config['max_teacher_birth_year']}")
    print(f"Student birth year range: {config['min_student_birth_year']} - {config['max_student_birth_year']}")
    print(f"Average points per student: {config['points_per_student']}")
    print(f"Points range: {config['min_points']} - {config['max_points']}")
    print(f"Quidditch team size: {config['min_team_size']} - {config['max_team_size']}")

if __name__ == "__main__":
    main() 