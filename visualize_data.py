import oracledb
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

def debug_print(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data is not None:
        print(f"Data: {data}")

def get_table_stats(cursor, table_name):
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]
    return count

def execute_query_to_df(cursor, query):
    cursor.execute(query)
    columns = [desc[0].lower() for desc in cursor.description]
    data = cursor.fetchall()
    return pd.DataFrame(data, columns=columns)

def plot_students_by_house(cursor):
    query = """
    SELECT h.name as house_name, COUNT(s.id) as student_count
    FROM houses h
    LEFT JOIN students s ON h.id = s.house_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='student_count')
    plt.title('Number of Students per House')
    plt.xlabel('House')
    plt.ylabel('Number of Students')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/students_by_house.png')
    plt.close()

def plot_grades_distribution(cursor):
    query = """
    SELECT g.value as grade_value, COUNT(*) as count
    FROM grades g
    GROUP BY g.value
    ORDER BY 
        CASE g.value
            WHEN 'O' THEN 1
            WHEN 'E' THEN 2
            WHEN 'A' THEN 3
            WHEN 'P' THEN 4
            WHEN 'D' THEN 5
            WHEN 'T' THEN 6
        END
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='grade_value', y='count')
    plt.title('Grade Distribution')
    plt.xlabel('Grade')
    plt.ylabel('Number of Grades')
    plt.tight_layout()
    plt.savefig('visualizations/grades_distribution.png')
    plt.close()

def plot_points_by_house(cursor):
    query = """
    SELECT h.name as house_name, SUM(p.value) as total_points
    FROM houses h
    JOIN students s ON h.id = s.house_id
    JOIN points p ON s.id = p.student_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='total_points')
    plt.title('Total Points per House')
    plt.xlabel('House')
    plt.ylabel('Total Points')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/points_by_house.png')
    plt.close()

def plot_subjects_popularity(cursor):
    query = """
    SELECT s.name as subject_name, COUNT(ss.student_id) as student_count
    FROM subjects s
    JOIN students_subjects ss ON s.id = ss.subject_id
    GROUP BY s.name
    ORDER BY COUNT(ss.student_id) DESC
    FETCH FIRST 10 ROWS ONLY
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='student_count', y='subject_name')
    plt.title('Top 10 Most Popular Subjects')
    plt.xlabel('Number of Students')
    plt.ylabel('Subject')
    plt.tight_layout()
    plt.savefig('visualizations/subjects_popularity.png')
    plt.close()

def plot_gender_distribution(cursor):
    query = """
    SELECT gender, COUNT(*) as count
    FROM students
    GROUP BY gender
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(8, 8))
    plt.pie(df['count'], labels=df['gender'], autopct='%1.1f%%')
    plt.title('Gender Distribution Among Students')
    plt.tight_layout()
    plt.savefig('visualizations/gender_distribution.png')
    plt.close()

def plot_quidditch_teams(cursor):
    query = """
    SELECT h.name as house_name, COUNT(qtm.id) as team_size
    FROM houses h
    LEFT JOIN students s ON h.id = s.house_id
    LEFT JOIN quidditch_team_members qtm ON s.id = qtm.student_id
    GROUP BY h.name
    """
    df = execute_query_to_df(cursor, query)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='team_size')
    plt.title('Quidditch Team Size by House')
    plt.xlabel('House')
    plt.ylabel('Team Size')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/quidditch_teams.png')
    plt.close()

def generate_html_report(stats):
    html_content = f"""
    <html>
    <head>
        <title>Hogwarts Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .container {{ max-width: 1200px; margin: 0 auto; }}
            .stats {{ background-color: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }}
            .visualization {{ margin-bottom: 30px; }}
            img {{ max-width: 100%; height: auto; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Hogwarts School Statistics Report</h1>
            <div class="stats">
                <h2>Database Statistics</h2>
                <p>Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <ul>
                    <li>Teachers: {stats['teachers']}</li>
                    <li>Houses: {stats['houses']}</li>
                    <li>Dormitories: {stats['dormitories']}</li>
                    <li>Students: {stats['students']}</li>
                    <li>Subjects: {stats['subjects']}</li>
                    <li>Grades: {stats['grades']}</li>
                    <li>Points: {stats['points']}</li>
                    <li>Quidditch Team Members: {stats['quidditch_team_members']}</li>
                </ul>
            </div>
            <div class="visualization">
                <h2>Visualizations</h2>
                <h3>Number of Students per House</h3>
                <img src="visualizations/students_by_house.png" alt="Students per House">
                
                <h3>Grade Distribution</h3>
                <img src="visualizations/grades_distribution.png" alt="Grade Distribution">
                
                <h3>Total Points per House</h3>
                <img src="visualizations/points_by_house.png" alt="Points per House">
                
                <h3>Top 10 Most Popular Subjects</h3>
                <img src="visualizations/subjects_popularity.png" alt="Subject Popularity">
                
                <h3>Gender Distribution Among Students</h3>
                <img src="visualizations/gender_distribution.png" alt="Gender Distribution">
                
                <h3>Quidditch Team Size by House</h3>
                <img src="visualizations/quidditch_teams.png" alt="Quidditch Teams">
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('hogwarts_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # Database connection configuration
    connection_string = "SYSTEM/admin@localhost:1521/XE"
    
    try:
        # Connect to database
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        debug_print("Connected to database")
        
        # Create visualizations directory
        os.makedirs('visualizations', exist_ok=True)
        
        # Get statistics
        debug_print("Getting statistics...")
        stats = {
            'teachers': get_table_stats(cursor, 'teachers'),
            'houses': get_table_stats(cursor, 'houses'),
            'dormitories': get_table_stats(cursor, 'dormitories'),
            'students': get_table_stats(cursor, 'students'),
            'subjects': get_table_stats(cursor, 'subjects'),
            'grades': get_table_stats(cursor, 'grades'),
            'points': get_table_stats(cursor, 'points'),
            'quidditch_team_members': get_table_stats(cursor, 'quidditch_team_members')
        }
        
        # Generate visualizations
        debug_print("Generating visualizations...")
        plot_students_by_house(cursor)
        plot_grades_distribution(cursor)
        plot_points_by_house(cursor)
        plot_subjects_popularity(cursor)
        plot_gender_distribution(cursor)
        plot_quidditch_teams(cursor)
        
        # Generate HTML report
        debug_print("Generating HTML report...")
        generate_html_report(stats)
        
        debug_print("\nSUMMARY:")
        for table, count in stats.items():
            debug_print(f"{table}: {count} records")
        
        debug_print("\nReport has been generated in hogwarts_report.html")
        
    except Exception as e:
        debug_print(f"ERROR: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("Database connection closed")

if __name__ == "__main__":
    main() 