# Hogwarts Database Management System

This project is a comprehensive database management system for Hogwarts School of Witchcraft and Wizardry. It allows you to generate, import, and visualize data about students, teachers, houses, and other aspects of the magical school.

## What This System Does

1. Generates realistic data for:
   - Teachers and their employment details
   - Hogwarts houses (Gryffindor, Hufflepuff, Ravenclaw, Slytherin)
   - Student dormitories
   - Students with their personal information
   - School subjects and classes
   - Student grades and points
   - Quidditch team members

2. Imports all data into an Oracle database
3. Provides visualization tools for analyzing the data

## How to Use

### Prerequisites
- Python 3.8 or newer
- Oracle Database (XE or newer)
- Required Python packages:
  ```
  pip install oracledb pandas matplotlib seaborn tqdm
  ```

### Database Setup
Make sure your Oracle database is configured with:
- Username: SYSTEM
- Password: admin
- Host: localhost
- Port: 1521
- Service: XE

### Running the System

1. First, generate the data:
   ```
   python generate_hogwarts_data.py
   ```
   This will create CSV files in the `hogwarts_data` folder.

2. Then, import the data into the database:
   ```
   python import_data.py
   ```
   This will populate your Oracle database with the generated data.

3. Finally, visualize the data:
   ```
   python visualize_data.py
   ```
   This will create various charts and graphs showing different aspects of the school.

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

## Database Structure

The system uses the following tables:

1. **teachers**
   - Basic information about Hogwarts teachers
   - Includes name, surname, birth date, and employment date

2. **houses**
   - Information about the four Hogwarts houses
   - Includes house name, symbol, location, and head of house

3. **dormitories**
   - Student living quarters
   - Organized by house and gender

4. **students**
   - Student information
   - Includes personal details, house assignment, and dormitory

5. **subjects**
   - All Hogwarts classes
   - Includes classroom assignments and teacher assignments

6. **students_subjects**
   - Links students to their classes
   - Tracks which students take which subjects

7. **grades**
   - Student academic performance
   - Records grades for each subject

8. **points**
   - House points system
   - Tracks points awarded or deducted

9. **quidditch_team_members**
   - Quidditch team information
   - Includes player positions and team captains

## Troubleshooting

If you encounter any issues:

1. Database Connection Problems:
   - Check if Oracle server is running
   - Verify login credentials
   - Ensure port 1521 is available

2. Data Import Issues:
   - Check if all CSV files exist in hogwarts_data folder
   - Verify CSV file formats
   - Ensure database tables are properly created

3. Data Generation Problems:
   - Check if all required name files exist (feminineNames.csv, masculineNames.csv, surnames.csv)
   - Verify hogwarts_config.json exists and is properly formatted
   - Ensure you have sufficient disk space

## Notes
- You can stop any process at any time using Ctrl+C
- The system will safely clean up and save progress before stopping
- All data is generated in English
- The system maintains referential integrity between all tables 