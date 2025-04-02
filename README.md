# Hogwarts Database Management System

This project contains a comprehensive database management system for Hogwarts School of Witchcraft and Wizardry, including information about students, teachers, grades, and other aspects of the magical school.

## Project Structure

```
hogwarts-db/
├── src/
│   ├── data_generation/     # Data generation scripts
│   │   ├── generate_hogwarts_data.py
│   │   └── config_generator.py
│   ├── database/           # Database operations
│   │   ├── import_data.py
│   │   └── clear_tables.sql
│   └── visualization/      # Data visualization scripts
│       └── visualize_data.py
├── config/                 # Configuration files
│   └── hogwarts_config.json
├── data/
│   ├── names/             # Name data files
│   │   ├── feminineNames.csv
│   │   ├── masculineNames.csv
│   │   └── surnames.csv
│   └── hogwarts_data/     # Generated data files
│       ├── teachers.csv
│       ├── houses.csv
│       ├── dormitories.csv
│       ├── students.csv
│       ├── subjects.csv
│       ├── students_subjects.csv
│       ├── grades.csv
│       ├── points.csv
│       └── quidditch_team_members.csv
└── docs/                  # Documentation
    └── README.md
```

## Requirements

- Python 3.8 or newer
- Oracle Database (XE or newer)
- Python packages:
  - oracledb
  - pandas
  - matplotlib
  - seaborn
  - tqdm

## Installation

1. Install required Python packages:
```bash
pip install oracledb pandas matplotlib seaborn tqdm
```

2. Make sure your Oracle database is configured with:
   - Username: SYSTEM
   - Password: admin
   - Host: localhost
   - Port: 1521
   - Service: XE

## Usage

1. Generate data:
```bash
python src/data_generation/generate_hogwarts_data.py
```

2. Import data into the database:
```bash
python src/database/import_data.py
```

3. Visualize the data:
```bash
python src/visualization/visualize_data.py
```

## Database Structure

### Tables

1. **teachers**
   - id (PK)
   - name
   - surname
   - date_of_birth
   - date_of_employment

2. **houses**
   - id (PK)
   - name
   - symbol
   - location
   - teacher_id (FK -> teachers)

3. **dormitories**
   - id (PK)
   - gender
   - room_number
   - house_id (FK -> houses)

4. **students**
   - id (PK)
   - name
   - surname
   - gender
   - date_of_birth
   - year
   - hogsmeade_consent
   - house_id (FK -> houses)
   - dormitory_id (FK -> dormitories)

5. **subjects**
   - id (PK)
   - name
   - classroom
   - year
   - teacher_id (FK -> teachers)

6. **students_subjects**
   - student_id (FK -> students)
   - subject_id (FK -> subjects)

7. **grades**
   - id (PK)
   - value
   - award_date
   - student_id (FK -> students)
   - subject_id (FK -> subjects)
   - teacher_id (FK -> teachers)

8. **points**
   - id (PK)
   - value
   - description
   - award_date
   - student_id (FK -> students)
   - teacher_id (FK -> teachers)

9. **quidditch_team_members**
   - id (PK)
   - position
   - is_captain
   - student_id (FK -> students)

## Data Generation Order
The system generates data in this specific order to maintain data integrity:
1. teachers.csv
2. houses.csv
3. dormitories.csv
4. subjects.csv
5. students.csv
6. students_subjects.csv
7. grades.csv
8. points.csv
9. quidditch_team_members.csv

## Troubleshooting

1. If you encounter database connection errors:
   - Check if the Oracle server is running
   - Verify login credentials
   - Ensure port 1521 is available

2. If you encounter import errors:
   - Check if all CSV files exist in the data/hogwarts_data directory
   - Verify CSV file formats
   - Ensure database tables are properly created

3. If you encounter data generation problems:
   - Check if all required name files exist in data/names directory
   - Verify config/hogwarts_config.json exists and is properly formatted
   - Ensure you have sufficient disk space

## Additional Notes
- You can stop any process at any time using Ctrl+C
- The system will safely clean up and save progress before stopping
- All data is generated in English
- The system maintains referential integrity between all tables
- Progress bars show real-time status of operations
- The system provides detailed logging of all operations 