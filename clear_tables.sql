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

COMMIT; 