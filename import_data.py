import oracledb
import csv
import os
from datetime import datetime

def debug_print(message, data=None):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {message}")
    if data is not None:
        print(f"Data: {data}")

def count_rows_in_file(filename):
    if not os.path.exists(filename):
        debug_print(f"BŁĄD: Plik {filename} nie istnieje!")
        return 0
    with open(filename, "r", newline='', encoding='utf-8') as f:
        return sum(1 for row in f) - 1  # -1 dla nagłówka

def import_csv(cursor, filename, table_name, columns):
    if not os.path.exists(filename):
        debug_print(f"BŁĄD: Plik {filename} nie istnieje!")
        return False
    
    debug_print(f"Importuję dane do tabeli {table_name}...")
    row_count = 0
    
    try:
        with open(filename, "r", newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f, delimiter=';')
            for row in reader:
                # Przygotuj wartości do wstawienia
                values = [row[col] for col in columns]
                
                # Przygotuj zapytanie SQL
                placeholders = ','.join([':' + str(i+1) for i in range(len(columns))])
                sql = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
                
                # Wykonaj wstawienie
                cursor.execute(sql, values)
                row_count += 1
                
                if row_count % 1000 == 0:
                    debug_print(f"Zaimportowano {row_count} wierszy do {table_name}")
        
        debug_print(f"Zakończono import {row_count} wierszy do {table_name}")
        return True
    except Exception as e:
        debug_print(f"BŁĄD podczas importu do {table_name}: {str(e)}")
        return False

def main():
    # Konfiguracja połączenia z bazą danych
    connection_string = "SYSTEM/admin@localhost:1521/XE"
    data_dir = r"C:\Users\DUPSON\Desktop\bazadanych\hogwarts_data"
    
    try:
        # Połącz z bazą danych
        connection = oracledb.connect(connection_string)
        cursor = connection.cursor()
        debug_print("Połączono z bazą danych")
        
        # Najpierw wyczyść tabele
        debug_print("Czyszczę tabele...")
        with open("clear_tables.sql", "r", encoding='utf-8') as f:
            sql_commands = f.read()
            for command in sql_commands.split(';'):
                if command.strip():
                    cursor.execute(command)
        connection.commit()
        debug_print("Tabele zostały wyczyszczone")
        
        # Definicje tabel i ich kolumn
        tables = [
            ("teachers.csv", "teachers", ["id", "name", "surname", "date_of_birth", "date_of_employment"]),
            ("houses.csv", "houses", ["id", "name", "symbol", "location", "teacher_id"]),
            ("dormitories.csv", "dormitories", ["id", "gender", "room_number", "house_id"]),
            ("students.csv", "students", ["id", "name", "surname", "gender", "date_of_birth", "year", "hogsmeade_consent", "house_id", "dormitory_id"]),
            ("subjects.csv", "subjects", ["id", "name", "classroom", "year", "teacher_id"]),
            ("students_subjects.csv", "students_subjects", ["student_id", "subject_id"]),
            ("grades.csv", "grades", ["id", "value", "award_date", "student_id", "subject_id", "teacher_id"]),
            ("points.csv", "points", ["id", "value", "description", "award_date", "student_id", "teacher_id"]),
            ("quidditch_team_members.csv", "quidditch_team_members", ["id", "position", "is_captain", "student_id"])
        ]
        
        # Importuj dane dla każdej tabeli
        for filename, table_name, columns in tables:
            file_path = os.path.join(data_dir, filename)
            debug_print(f"Sprawdzam plik {filename}")
            
            if not os.path.exists(file_path):
                debug_print(f"BŁĄD: Plik {filename} nie istnieje w katalogu {data_dir}")
                continue
                
            row_count = count_rows_in_file(file_path)
            debug_print(f"Znaleziono {row_count} wierszy w pliku {filename}")
            
            if row_count == 0:
                debug_print(f"BŁĄD: Plik {filename} jest pusty!")
                continue
                
            if import_csv(cursor, file_path, table_name, columns):
                connection.commit()
                debug_print(f"Pomyślnie zaimportowano dane do {table_name}")
            else:
                connection.rollback()
                debug_print(f"Nie udało się zaimportować danych do {table_name}")
        
        # Sprawdź liczbę rekordów w każdej tabeli
        debug_print("\nPODSUMOWANIE IMPORTU:")
        for _, table_name, _ in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            debug_print(f"{table_name}: {count} rekordów")
        
        debug_print("\nImport zakończony")
        
    except Exception as e:
        debug_print(f"BŁĄD: {str(e)}")
        if 'connection' in locals():
            connection.rollback()
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()
            debug_print("Zamknięto połączenie z bazą danych")

if __name__ == "__main__":
    main() 