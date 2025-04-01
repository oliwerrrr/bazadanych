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

def plot_students_by_house(cursor):
    query = """
    SELECT h.name as house_name, COUNT(s.id) as student_count
    FROM houses h
    LEFT JOIN students s ON h.id = s.house_id
    GROUP BY h.name
    """
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='student_count')
    plt.title('Liczba uczniów w każdym domu')
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
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='grade_value', y='count')
    plt.title('Rozkład ocen')
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
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='total_points')
    plt.title('Suma punktów dla każdego domu')
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
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=df, x='student_count', y='subject_name')
    plt.title('Top 10 najpopularniejszych przedmiotów')
    plt.tight_layout()
    plt.savefig('visualizations/subjects_popularity.png')
    plt.close()

def plot_gender_distribution(cursor):
    query = """
    SELECT gender, COUNT(*) as count
    FROM students
    GROUP BY gender
    """
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(8, 8))
    plt.pie(df['count'], labels=df['gender'], autopct='%1.1f%%')
    plt.title('Rozkład płci wśród uczniów')
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
    df = pd.read_sql(query, cursor.connection)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df, x='house_name', y='team_size')
    plt.title('Wielkość drużyn Quidditcha w każdym domu')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig('visualizations/quidditch_teams.png')
    plt.close()

def generate_html_report(stats):
    html_content = f"""
    <html>
    <head>
        <title>Raport Hogwartu</title>
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
            <h1>Raport Hogwartu</h1>
            <div class="stats">
                <h2>Statystyki bazy danych</h2>
                <p>Data generowania: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <ul>
                    <li>Nauczyciele: {stats['teachers']}</li>
                    <li>Domy: {stats['houses']}</li>
                    <li>Dormitoria: {stats['dormitories']}</li>
                    <li>Uczniowie: {stats['students']}</li>
                    <li>Przedmioty: {stats['subjects']}</li>
                    <li>Oceny: {stats['grades']}</li>
                    <li>Punkty: {stats['points']}</li>
                    <li>Członkowie drużyn Quidditcha: {stats['quidditch_team_members']}</li>
                </ul>
            </div>
            <div class="visualization">
                <h2>Wizualizacje</h2>
                <h3>Liczba uczniów w każdym domu</h3>
                <img src="visualizations/students_by_house.png" alt="Uczniowie w domach">
                
                <h3>Rozkład ocen</h3>
                <img src="visualizations/grades_distribution.png" alt="Rozkład ocen">
                
                <h3>Suma punktów dla każdego domu</h3>
                <img src="visualizations/points_by_house.png" alt="Punkty w domach">
                
                <h3>Top 10 najpopularniejszych przedmiotów</h3>
                <img src="visualizations/subjects_popularity.png" alt="Popularność przedmiotów">
                
                <h3>Rozkład płci wśród uczniów</h3>
                <img src="visualizations/gender_distribution.png" alt="Rozkład płci">
                
                <h3>Wielkość drużyn Quidditcha</h3>
                <img src="visualizations/quidditch_teams.png" alt="Drużyny Quidditcha">
            </div>
        </div>
    </body>
    </html>
    """
    
    with open('hogwarts_report.html', 'w', encoding='utf-8') as f:
        f.write(html_content)

def main():
    # Konfiguracja połączenia z bazą danych
    connection_string = "SYSTEM/admin@localhost:1521/XE"
    
    try:
        # Połącz z bazą danych
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        debug_print("Połączono z bazą danych")
        
        # Utwórz katalog na wizualizacje
        os.makedirs('visualizations', exist_ok=True)
        
        # Pobierz statystyki
        debug_print("Pobieram statystyki...")
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
        
        # Generuj wizualizacje
        debug_print("Generuję wizualizacje...")
        plot_students_by_house(cursor)
        plot_grades_distribution(cursor)
        plot_points_by_house(cursor)
        plot_subjects_popularity(cursor)
        plot_gender_distribution(cursor)
        plot_quidditch_teams(cursor)
        
        # Generuj raport HTML
        debug_print("Generuję raport HTML...")
        generate_html_report(stats)
        
        debug_print("\nPODSUMOWANIE:")
        for table, count in stats.items():
            debug_print(f"{table}: {count} rekordów")
        
        debug_print("\nRaport został wygenerowany w pliku hogwarts_report.html")
        
    except Exception as e:
        debug_print(f"BŁĄD: {str(e)}")
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("Zamknięto połączenie z bazą danych")

if __name__ == "__main__":
    main() 