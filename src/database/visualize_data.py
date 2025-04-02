import os
import sys
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import oracledb
from tqdm import tqdm

# Get absolute paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VISUALIZATION_DIR = os.path.join(BASE_DIR, 'docs', 'visualizations')

def ensure_directories():
    """Ensure all required directories exist"""
    os.makedirs(VISUALIZATION_DIR, exist_ok=True)

def get_database_connection():
    """Get database connection with proper error handling"""
    try:
        connection = oracledb.connect("SYSTEM/admin@localhost:1521/XE")
        print("Database connection successful")
        return connection
    except oracledb.Error as e:
        print(f"Database connection error: {str(e)}")
        raise Exception(f"Failed to connect to database: {str(e)}")

def execute_query_to_df(cursor, query):
    """Execute a query and return results as a DataFrame"""
    try:
        cursor.execute(query)
        columns = [col[0] for col in cursor.description]
        data = cursor.fetchall()
        df = pd.DataFrame(data, columns=columns)
        print(f"Retrieved {len(df)} rows from query")
        return df
    except Exception as e:
        print(f"Error executing query: {str(e)}")
        if hasattr(e, 'help'):
            print("Help:", e.help)
        raise

def plot_students_by_house(cursor):
    """Plot number of students by house"""
    try:
        query = """
        SELECT h.name as house_name, COUNT(s.id) as student_count
        FROM houses h
        LEFT JOIN students s ON h.id = s.house_id
        GROUP BY h.name
        ORDER BY COUNT(s.id) DESC
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='HOUSE_NAME', y='STUDENT_COUNT')
        plt.title('Number of Students by House')
        plt.xlabel('House')
        plt.ylabel('Number of Students')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'students_by_house.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved students by house plot to {output_path}")
    except Exception as e:
        print(f"Error plotting students by house: {str(e)}")

def plot_grades_distribution(cursor):
    """Plot grade distribution"""
    try:
        query = """
        SELECT value as grade, COUNT(*) as count
        FROM grades
        GROUP BY value
        ORDER BY value
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='GRADE', y='COUNT')
        plt.title('Grade Distribution')
        plt.xlabel('Grade')
        plt.ylabel('Count')
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'grades_distribution.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved grades distribution plot to {output_path}")
    except Exception as e:
        print(f"Error plotting grades distribution: {str(e)}")

def plot_subjects_popularity(cursor):
    """Plot subject popularity"""
    try:
        query = """
        SELECT s.name as subject_name, COUNT(g.id) as grade_count
        FROM subjects s
        LEFT JOIN grades g ON s.id = g.subject_id
        GROUP BY s.name
        ORDER BY COUNT(g.id) DESC
        FETCH FIRST 10 ROWS ONLY
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(12, 6))
        sns.barplot(data=df, x='GRADE_COUNT', y='SUBJECT_NAME')
        plt.title('Top 10 Most Popular Subjects')
        plt.xlabel('Number of Grades')
        plt.ylabel('Subject')
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'subjects_popularity.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved subjects popularity plot to {output_path}")
    except Exception as e:
        print(f"Error plotting subjects popularity: {str(e)}")

def plot_points_by_house(cursor):
    """Plot points by house"""
    try:
        query = """
        SELECT h.name as house_name, SUM(p.value) as total_points
        FROM houses h
        LEFT JOIN students s ON h.id = s.house_id
        LEFT JOIN points p ON s.id = p.student_id
        GROUP BY h.name
        ORDER BY SUM(p.value) DESC
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='HOUSE_NAME', y='TOTAL_POINTS')
        plt.title('Total Points by House')
        plt.xlabel('House')
        plt.ylabel('Total Points')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'points_by_house.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved points by house plot to {output_path}")
    except Exception as e:
        print(f"Error plotting points by house: {str(e)}")

def plot_gender_distribution(cursor):
    """Plot gender distribution"""
    try:
        query = """
        SELECT gender, COUNT(*) as count
        FROM students
        GROUP BY gender
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(8, 8))
        plt.pie(df['COUNT'], labels=df['GENDER'], autopct='%1.1f%%')
        plt.title('Gender Distribution')
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'gender_distribution.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved gender distribution plot to {output_path}")
    except Exception as e:
        print(f"Error plotting gender distribution: {str(e)}")

def plot_quidditch_teams(cursor):
    """Plot Quidditch team composition"""
    try:
        query = """
        SELECT h.name as house_name, COUNT(q.id) as team_size
        FROM houses h
        LEFT JOIN students s ON h.id = s.house_id
        LEFT JOIN quidditch_team_members q ON s.id = q.student_id
        GROUP BY h.name
        ORDER BY COUNT(q.id) DESC
        """
        df = execute_query_to_df(cursor, query)
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=df, x='HOUSE_NAME', y='TEAM_SIZE')
        plt.title('Quidditch Team Size by House')
        plt.xlabel('House')
        plt.ylabel('Team Size')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        output_path = os.path.join(VISUALIZATION_DIR, 'quidditch_teams.png')
        plt.savefig(output_path)
        plt.close()
        print(f"Saved Quidditch teams plot to {output_path}")
    except Exception as e:
        print(f"Error plotting Quidditch teams: {str(e)}")

def main():
    try:
        ensure_directories()
        print("Starting data visualization...")
        
        with get_database_connection() as conn:
            cursor = conn.cursor()
            
            print("Generating visualizations...")
            plot_students_by_house(cursor)
            plot_grades_distribution(cursor)
            plot_subjects_popularity(cursor)
            plot_points_by_house(cursor)
            plot_gender_distribution(cursor)
            plot_quidditch_teams(cursor)
            
            print("All visualizations generated successfully!")
            
    except Exception as e:
        print(f"Error in main: {str(e)}")
        raise e

if __name__ == '__main__':
    main() 