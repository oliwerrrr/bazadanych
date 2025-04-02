-- Hogwarts Database Workload Measurement Script
-- This script measures execution time of various database operations

-- Enable timing
SET TIMING ON

-- 1. Simple SELECT queries
-- 1.1 Count students per house
SELECT h.name, COUNT(s.id) as student_count
FROM houses h
LEFT JOIN students s ON h.id = s.house_id
GROUP BY h.name
ORDER BY student_count DESC;

-- 1.2 Average grade per subject
SELECT sub.name, AVG(g.value) as avg_grade
FROM subjects sub
JOIN grades g ON sub.id = g.subject_id
GROUP BY sub.name
ORDER BY avg_grade DESC;

-- 2. Complex JOIN queries
-- 2.1 Student performance by house
SELECT 
    h.name as house_name,
    sub.name as subject,
    AVG(g.value) as avg_grade,
    COUNT(DISTINCT s.id) as student_count
FROM houses h
JOIN students s ON h.id = s.house_id
JOIN students_subjects ss ON s.id = ss.student_id
JOIN subjects sub ON ss.subject_id = sub.id
JOIN grades g ON s.id = g.student_id AND sub.id = g.subject_id
GROUP BY h.name, sub.name
ORDER BY h.name, avg_grade DESC;

-- 3. Aggregation queries
-- 3.1 House points ranking
SELECT 
    h.name,
    SUM(p.value) as total_points,
    COUNT(DISTINCT s.id) as student_count
FROM houses h
JOIN students s ON h.id = s.house_id
LEFT JOIN points p ON s.id = p.student_id
GROUP BY h.name
ORDER BY total_points DESC;

-- 4. Subqueries
-- 4.1 Top performing students (above average in all subjects)
SELECT 
    s.name,
    s.surname,
    h.name as house,
    AVG(g.value) as avg_grade
FROM students s
JOIN houses h ON s.house_id = h.id
JOIN grades g ON s.id = g.student_id
WHERE g.value > (
    SELECT AVG(value)
    FROM grades
    WHERE subject_id = g.subject_id
)
GROUP BY s.id, s.name, s.surname, h.name
HAVING COUNT(DISTINCT g.subject_id) = (
    SELECT COUNT(DISTINCT id)
    FROM subjects
)
ORDER BY avg_grade DESC;

-- 5. Transaction operations
-- 5.1 Award points to a house
DECLARE
    v_house_id NUMBER;
    v_student_id NUMBER;
BEGIN
    -- Get a random student from Gryffindor
    SELECT s.id INTO v_student_id
    FROM students s
    JOIN houses h ON s.house_id = h.id
    WHERE h.name = 'Gryffindor'
    ORDER BY DBMS_RANDOM.VALUE
    FETCH FIRST 1 ROW ONLY;

    -- Award points
    INSERT INTO points (id, value, description, award_date, student_id, teacher_id)
    VALUES (
        (SELECT NVL(MAX(id), 0) + 1 FROM points),
        10,
        'Outstanding performance in class',
        SYSDATE,
        v_student_id,
        (SELECT id FROM teachers ORDER BY DBMS_RANDOM.VALUE FETCH FIRST 1 ROW ONLY)
    );
    COMMIT;
END;
/

-- 6. Complex updates
-- 6.1 Update student grades based on house points
UPDATE grades g
SET g.value = g.value + 1
WHERE g.student_id IN (
    SELECT s.id
    FROM students s
    JOIN points p ON s.id = p.student_id
    GROUP BY s.id
    HAVING SUM(p.value) > 100
)
AND g.value < 6;

-- 7. Delete operations
-- 7.1 Remove inactive Quidditch team members
DELETE FROM quidditch_team_members
WHERE student_id IN (
    SELECT s.id
    FROM students s
    LEFT JOIN points p ON s.id = p.student_id
    WHERE p.id IS NULL
    OR p.award_date < ADD_MONTHS(SYSDATE, -6)
);

-- 8. Index usage test
-- 8.1 Query using multiple indexes
SELECT 
    s.name,
    s.surname,
    h.name as house,
    sub.name as subject,
    g.value as grade
FROM students s
JOIN houses h ON s.house_id = h.id
JOIN students_subjects ss ON s.id = ss.student_id
JOIN subjects sub ON ss.subject_id = sub.id
JOIN grades g ON s.id = g.student_id AND sub.id = g.subject_id
WHERE h.name = 'Gryffindor'
AND g.value >= 5
ORDER BY g.value DESC;

-- 9. Full table scan test
-- 9.1 Complex aggregation without index usage
SELECT 
    h.name,
    COUNT(DISTINCT s.id) as total_students,
    COUNT(DISTINCT CASE WHEN g.value >= 5 THEN s.id END) as excellent_students,
    AVG(g.value) as avg_grade
FROM houses h
JOIN students s ON h.id = s.house_id
LEFT JOIN grades g ON s.id = g.student_id
GROUP BY h.name
ORDER BY avg_grade DESC;

-- 10. Transaction isolation test
-- 10.1 Concurrent updates simulation
DECLARE
    v_student_id NUMBER;
BEGIN
    -- Get a random student
    SELECT id INTO v_student_id
    FROM students
    ORDER BY DBMS_RANDOM.VALUE
    FETCH FIRST 1 ROW ONLY;

    -- Start transaction
    UPDATE students
    SET year = year + 1
    WHERE id = v_student_id;

    -- Simulate some work
    DBMS_LOCK.SLEEP(1);

    -- Update related records
    UPDATE grades
    SET value = value + 1
    WHERE student_id = v_student_id
    AND value < 6;

    COMMIT;
END;
/

-- Disable timing
SET TIMING OFF 