-- Sprawdź, czy wszystkie student_id w students_subjects istnieją w tabeli students
SELECT DISTINCT ss.student_id
FROM students_subjects ss
WHERE NOT EXISTS (
    SELECT 1 FROM students s WHERE s.id = ss.student_id
)
ORDER BY ss.student_id;

-- Sprawdź, czy wszystkie subject_id w students_subjects istnieją w tabeli subjects
SELECT DISTINCT ss.subject_id
FROM students_subjects ss
WHERE NOT EXISTS (
    SELECT 1 FROM subjects s WHERE s.id = ss.subject_id
)
ORDER BY ss.subject_id;

-- Sprawdź duplikaty w students_subjects
SELECT student_id, subject_id, COUNT(*)
FROM students_subjects
GROUP BY student_id, subject_id
HAVING COUNT(*) > 1
ORDER BY COUNT(*) DESC;

-- Sprawdź zgodność lat między studentami a przedmiotami
SELECT ss.student_id, ss.subject_id, s.year as student_year, sub.year as subject_year
FROM students_subjects ss
JOIN students s ON ss.student_id = s.id
JOIN subjects sub ON ss.subject_id = sub.id
WHERE s.year != sub.year
ORDER BY ss.student_id;

-- Sprawdź oceny bez powiązań student-przedmiot
SELECT g.id, g.student_id, g.subject_id
FROM grades g
WHERE NOT EXISTS (
    SELECT 1 
    FROM students_subjects ss 
    WHERE ss.student_id = g.student_id 
    AND ss.subject_id = g.subject_id
)
ORDER BY g.id;

-- Sprawdź oceny z nieistniejącymi nauczycielami
SELECT g.id, g.teacher_id
FROM grades g
WHERE NOT EXISTS (
    SELECT 1 FROM teachers t WHERE t.id = g.teacher_id
)
ORDER BY g.id;

-- Pokaż statystyki dla każdej tabeli
SELECT 'students' as table_name, COUNT(*) as count FROM students
UNION ALL
SELECT 'subjects', COUNT(*) FROM subjects
UNION ALL
SELECT 'teachers', COUNT(*) FROM teachers
UNION ALL
SELECT 'students_subjects', COUNT(*) FROM students_subjects
UNION ALL
SELECT 'grades', COUNT(*) FROM grades;

-- Sprawdź zakres ID w każdej tabeli
SELECT 'students' as table_name, MIN(id) as min_id, MAX(id) as max_id FROM students
UNION ALL
SELECT 'subjects', MIN(id), MAX(id) FROM subjects
UNION ALL
SELECT 'teachers', MIN(id), MAX(id) FROM teachers
UNION ALL
SELECT 'students_subjects', MIN(student_id), MAX(student_id) FROM students_subjects
UNION ALL
SELECT 'grades', MIN(id), MAX(id) FROM grades;

SELECT table_name, COUNT(*) as row_count
FROM (
    SELECT 'Students' as table_name FROM Students
    UNION ALL
    SELECT 'Teachers' FROM Teachers
    UNION ALL
    SELECT 'Houses' FROM Houses
    UNION ALL
    SELECT 'Dormitories' FROM Dormitories
    UNION ALL
    SELECT 'Subjects' FROM Subjects
    UNION ALL
    SELECT 'Grades' FROM Grades
)
GROUP BY table_name
ORDER BY table_name; 