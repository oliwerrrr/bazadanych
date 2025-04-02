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
│   │   ├── run_workload.py
│   │   └── clear_tables.sql
│   ├── server.py           # Web server for the application
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
└── docs/                  # Documentation and web files
    ├── hogwarts_report.html
    ├── HogwartRelations.png
    ├── schema.png
    ├── visualizations/
    │   ├── students_by_house.png
    │   ├── grades_distribution.png
    │   └── [...other visualization files]
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
  - flask
  - flask-socketio

## Installation

1. Install required Python packages:
```bash
pip install oracledb pandas matplotlib seaborn tqdm flask flask-socketio
```

2. Make sure your Oracle database is configured with:
   - Username: SYSTEM
   - Password: admin
   - Host: localhost
   - Port: 1521
   - Service: XE

## Usage

### Manual Scripts Execution

You can execute individual scripts manually for specific tasks:

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

### Running the Web Server

The project includes a web server that provides a user-friendly interface for database management, visualization, and performance testing:

1. Start the web server:
```bash
python src/server.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. The web interface allows you to:
   - Generate configuration and sample data
   - Import data to the database
   - Clear the database
   - Run performance tests
   - View database statistics and visualizations
   - Analyze SQL query performance

## Deployment Guide

If you want to deploy this system on another machine or server, follow these steps:

### Prerequisites

1. Install Python 3.8 or newer
2. Install Oracle Database XE (or a compatible version)
3. Clone or download this repository

### Setup Process

1. Create and configure your Oracle database:
   - Create a new user 'SYSTEM' with password 'admin' (or modify src/server.py to use different credentials)
   - Ensure the database is running on localhost:1521
   - Make sure the service name is set to 'XE'

2. Install required Python dependencies:
```bash
pip install oracledb pandas matplotlib seaborn tqdm flask flask-socketio
```

3. Generate initial configuration:
```bash
python src/data_generation/config_generator.py
```

4. Generate sample data:
```bash
python src/data_generation/generate_hogwarts_data.py
```

5. Import data into the database:
```bash
python src/database/import_data.py
```

6. Start the web server:
```bash
python src/server.py
```

7. Access the web interface at http://localhost:5000

### System Maintenance

- To backup your data, export the database tables to CSV files
- To update visualizations, run `python src/visualization/visualize_data.py`
- To clear all data and start fresh, use the "Clear Database" option in the web interface or run:
```bash
python src/database/import_data.py --clear
```

### Production Deployment Notes

For production environments:
- Use a production WSGI server like Gunicorn or uWSGI instead of Flask's development server
- Consider setting up proper authentication for the database and web interface
- Configure firewall rules to restrict access to the database port (1521)
- Set up regular database backups
- Consider using environment variables for sensitive information like database credentials

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

## Performance Tests

The system includes several performance tests that can be run from the web interface:

1. **Simple SELECT** - Basic select query on the students table
2. **Complex JOIN** - Complex join between students, grades, and subjects tables
3. **Aggregation** - Complex aggregation with grouping and having
4. **Nested Subquery** - Complex nested subquery with multiple conditions
5. **Transaction - Batch Insert** - Insert multiple grades with transaction control
6. **Transaction - Batch Update** - Update multiple grades with transaction control
7. **Transaction - Complex Delete** - Delete with complex conditions and restore data
8. **Full Table Scan Analysis** - Analyze grade distribution with full table scan

These tests help evaluate database performance and demonstrate various SQL operations.

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

4. If the web server fails to start:
   - Check if port 5000 is already in use (try a different port with `python src/server.py --port 8080`)
   - Verify all dependencies are installed
   - Check if the database connection parameters are correct
   - Look for error messages in the console output

5. If performance tests fail:
   - Ensure the database contains sufficient data
   - Check that you have proper table indexes
   - Verify Oracle database resource limits (memory, connections)

## Additional Notes
- You can stop any process at any time using Ctrl+C
- The system will safely clean up and save progress before stopping
- All data is generated in English
- The system maintains referential integrity between all tables
- Progress bars show real-time status of operations
- The system provides detailed logging of all operations 
- The web interface provides a real-time update of database statistics
- Performance tests run on 10-30% of the available data for accurate metrics 