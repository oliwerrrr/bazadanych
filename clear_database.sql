-- Wyłącz sprawdzanie kluczy obcych
ALTER SESSION SET CONSTRAINTS = DEFERRED;

-- Usuń dane z tabel w odpowiedniej kolejności (od najbardziej zależnych do najmniej zależnych)
DELETE FROM grades;
DELETE FROM points;
DELETE FROM quidditch_team_members;
DELETE FROM students_subjects;
DELETE FROM subjects;
DELETE FROM students;
DELETE FROM dormitories;
DELETE FROM houses;
DELETE FROM teachers;

-- Włącz z powrotem sprawdzanie kluczy obcych
ALTER SESSION SET CONSTRAINTS = IMMEDIATE;

-- Wyczyść sekwencje (jeśli są używane)
-- ALTER SEQUENCE grades_seq RESTART WITH 1;
-- ALTER SEQUENCE points_seq RESTART WITH 1;
-- ALTER SEQUENCE quidditch_team_members_seq RESTART WITH 1;
-- ALTER SEQUENCE subjects_seq RESTART WITH 1;
-- ALTER SEQUENCE students_seq RESTART WITH 1;
-- ALTER SEQUENCE dormitories_seq RESTART WITH 1;
-- ALTER SEQUENCE houses_seq RESTART WITH 1;
-- ALTER SEQUENCE teachers_seq RESTART WITH 1;

COMMIT; 