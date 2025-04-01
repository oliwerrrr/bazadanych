-- Skrypt do sprawdzenia danych w tabelach Hogwarts

-- 1. Podstawowe statystyki dla każdej tabeli
SELECT 'HOUSES' as nazwa_tabeli, COUNT(*) as liczba_rekordow FROM HOUSES
UNION ALL
SELECT 'DORMITORIES', COUNT(*) FROM DORMITORIES
UNION ALL
SELECT 'TEACHERS', COUNT(*) FROM TEACHERS
UNION ALL
SELECT 'SUBJECTS', COUNT(*) FROM SUBJECTS
UNION ALL
SELECT 'STUDENTS', COUNT(*) FROM STUDENTS
UNION ALL
SELECT 'STUDENTS_SUBJECTS', COUNT(*) FROM STUDENTS_SUBJECTS
UNION ALL
SELECT 'QUIDDITCH_TEAM_MEMBERS', COUNT(*) FROM QUIDDITCH_TEAM_MEMBERS
UNION ALL
SELECT 'POINTS', COUNT(*) FROM POINTS
UNION ALL
SELECT 'GRADES', COUNT(*) FROM GRADES
ORDER BY 1;

-- 2. Zakresy ID w każdej tabeli
SELECT 'HOUSES' as nazwa_tabeli, 
       MIN(id) as min_id, 
       MAX(id) as max_id 
FROM HOUSES
UNION ALL
SELECT 'DORMITORIES', MIN(id), MAX(id) FROM DORMITORIES
UNION ALL
SELECT 'TEACHERS', MIN(id), MAX(id) FROM TEACHERS
UNION ALL
SELECT 'SUBJECTS', MIN(id), MAX(id) FROM SUBJECTS
UNION ALL
SELECT 'STUDENTS', MIN(id), MAX(id) FROM STUDENTS
UNION ALL
SELECT 'STUDENTS_SUBJECTS', MIN(student_id), MAX(student_id) FROM STUDENTS_SUBJECTS
UNION ALL
SELECT 'QUIDDITCH_TEAM_MEMBERS', MIN(id), MAX(id) FROM QUIDDITCH_TEAM_MEMBERS
UNION ALL
SELECT 'POINTS', MIN(id), MAX(id) FROM POINTS
UNION ALL
SELECT 'GRADES', MIN(id), MAX(id) FROM GRADES
ORDER BY 1;

-- 3. Przykładowe rekordy z każdej tabeli
SELECT 'HOUSES' as nazwa_tabeli, 
       TO_CHAR(id) as id,
       name,
       symbol 
FROM HOUSES WHERE ROWNUM <= 3
UNION ALL
SELECT 'DORMITORIES', 
       TO_CHAR(id),
       gender,
       TO_CHAR(room_number) 
FROM DORMITORIES WHERE ROWNUM <= 3
UNION ALL
SELECT 'TEACHERS', 
       TO_CHAR(id),
       name,
       surname 
FROM TEACHERS WHERE ROWNUM <= 3
UNION ALL
SELECT 'SUBJECTS', 
       TO_CHAR(id),
       name,
       TO_CHAR(classroom) 
FROM SUBJECTS WHERE ROWNUM <= 3
UNION ALL
SELECT 'STUDENTS', 
       TO_CHAR(id),
       name,
       surname 
FROM STUDENTS WHERE ROWNUM <= 3
UNION ALL
SELECT 'STUDENTS_SUBJECTS', 
       TO_CHAR(student_id),
       TO_CHAR(subject_id),
       'NULL' 
FROM STUDENTS_SUBJECTS WHERE ROWNUM <= 3
UNION ALL
SELECT 'QUIDDITCH_TEAM_MEMBERS', 
       TO_CHAR(id),
       position,
       TO_CHAR(is_captain) 
FROM QUIDDITCH_TEAM_MEMBERS WHERE ROWNUM <= 3
UNION ALL
SELECT 'POINTS', 
       TO_CHAR(id),
       TO_CHAR(value),
       description 
FROM POINTS WHERE ROWNUM <= 3
UNION ALL
SELECT 'GRADES', 
       TO_CHAR(id),
       value,
       TO_CHAR(award_date) 
FROM GRADES WHERE ROWNUM <= 3
ORDER BY 1;

-- 4. Sprawdzenie kluczy obcych
SELECT 'STUDENTS' as nazwa_tabeli, 
       COUNT(*) as liczba_rekordow,
       COUNT(DISTINCT house_id) as unikalne_house_ids,
       COUNT(DISTINCT dormitory_id) as unikalne_dormitory_ids
FROM STUDENTS
UNION ALL
SELECT 'STUDENTS_SUBJECTS', 
       COUNT(*),
       COUNT(DISTINCT student_id),
       COUNT(DISTINCT subject_id)
FROM STUDENTS_SUBJECTS
UNION ALL
SELECT 'GRADES', 
       COUNT(*),
       COUNT(DISTINCT student_id),
       COUNT(DISTINCT subject_id)
FROM GRADES
ORDER BY 1;

-- 5. Sprawdzenie dat
SELECT 'STUDENTS' as nazwa_tabeli, 
       MIN(date_of_birth) as min_data,
       MAX(date_of_birth) as max_data
FROM STUDENTS
UNION ALL
SELECT 'TEACHERS', 
       MIN(date_of_birth),
       MAX(date_of_birth) 
FROM TEACHERS
UNION ALL
SELECT 'POINTS', 
       MIN(award_date),
       MAX(award_date) 
FROM POINTS
UNION ALL
SELECT 'GRADES', 
       MIN(award_date),
       MAX(award_date) 
FROM GRADES
ORDER BY 1; 