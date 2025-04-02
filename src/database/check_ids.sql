SELECT 'Students' as table_name, MIN(id) as min_id, MAX(id) as max_id, COUNT(*) as count FROM Students
UNION ALL
SELECT 'Subjects', MIN(id), MAX(id), COUNT(*) FROM Subjects; 