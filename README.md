# System Zarządzania Hogwartem

Ten projekt zawiera system zarządzania danymi Hogwartu, w tym informacje o uczniach, nauczycielach, ocenach i innych aspektach szkoły.

## Wymagania

- Python 3.8 lub nowszy
- Oracle Database (XE lub nowsza wersja)
- Pakiety Python:
  - oracledb
  - pandas
  - matplotlib
  - seaborn

## Instalacja

1. Zainstaluj wymagane pakiety Python:
```bash
pip install oracledb pandas matplotlib seaborn
```

2. Upewnij się, że masz skonfigurowaną bazę danych Oracle z następującymi danymi:
   - Username: SYSTEM
   - Password: admin
   - Host: localhost
   - Port: 1521
   - Service: XE

## Struktura projektu

- `generate_hogwarts_data.py` - skrypt generujący przykładowe dane
- `import_data.py` - skrypt importujący dane do bazy
- `visualize_data.py` - skrypt wizualizujący dane
- `clear_tables.sql` - skrypt SQL do czyszczenia tabel
- `hogwarts_data/` - katalog z plikami CSV
  - teachers.csv
  - houses.csv
  - dormitories.csv
  - students.csv
  - subjects.csv
  - students_subjects.csv
  - grades.csv
  - points.csv
  - quidditch_team_members.csv

## Użycie

1. Generowanie danych:
```bash
python generate_hogwarts_data.py
```

2. Import danych do bazy:
```bash
python import_data.py
```

3. Wizualizacja danych:
```bash
python visualize_data.py
```

## Struktura bazy danych

### Tabele

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

## Rozwiązywanie problemów

1. Jeśli występuje błąd połączenia z bazą danych:
   - Sprawdź, czy serwer Oracle jest uruchomiony
   - Upewnij się, że dane logowania są poprawne
   - Sprawdź, czy port 1521 jest dostępny

2. Jeśli występują błędy podczas importu:
   - Sprawdź, czy wszystkie pliki CSV są w katalogu hogwarts_data
   - Upewnij się, że format danych w plikach CSV jest poprawny
   - Sprawdź, czy tabele w bazie danych zostały utworzone poprawnie 