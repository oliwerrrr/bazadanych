import cx_Oracle
import json
from datetime import datetime
import os

# Get absolute paths
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
DOCS_DIR = os.path.join(BASE_DIR, 'docs')

def run_workload():
    # Database connection details
    connection = cx_Oracle.connect(
        user="SYSTEM",
        password="admin",
        dsn="localhost:1521/XE"
    )
    
    cursor = connection.cursor()
    
    # Read the workload.sql file
    workload_path = os.path.join(os.path.dirname(__file__), 'workload.sql')
    with open(workload_path, 'r') as file:
        sql_commands = file.read()
    
    # Split the commands and execute them
    commands = sql_commands.split(';')
    results = []
    
    for command in commands:
        if command.strip():
            try:
                cursor.execute(command)
                if cursor.description:  # If it's a SELECT query
                    columns = [col[0] for col in cursor.description]
                    rows = cursor.fetchall()
                    results.append({
                        'query': command.strip(),
                        'columns': columns,
                        'rows': [dict(zip(columns, row)) for row in rows]
                    })
            except cx_Oracle.Error as error:
                print(f"Error executing command: {error}")
    
    # Save results to JSON file
    results_path = os.path.join(DOCS_DIR, 'workload_results.json')
    os.makedirs(DOCS_DIR, exist_ok=True)
    with open(results_path, 'w') as f:
        json.dump({
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'results': results
        }, f, indent=2)
    
    cursor.close()
    connection.close()

if __name__ == "__main__":
    run_workload() 