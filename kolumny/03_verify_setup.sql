SET SERVEROUTPUT ON;
SET LINESIZE 200;
COLUMN table_name FORMAT A30;
COLUMN owner FORMAT A20;
COLUMN inmemory FORMAT A10;
COLUMN status FORMAT A15;
COLUMN num_rows FORMAT 999,999,999;

PROMPT
PROMPT ===============================================================
PROMPT          WERYFIKACJA KONFIGURACJI BAZY `Columns_hogward`
PROMPT ===============================================================
PROMPT
PROMPT !!! UWAGA: Ten skrypt należy uruchomić jako użytkownik SYSTEM   !!!
PROMPT !!! połączony z bazą PDB (np. XEPDB1).                        !!!
PROMPT

PROMPT 📊 SPRAWDZAM TABELE, LICZBĘ WIERSZY I STATUS IN-MEMORY:
PROMPT -------------------------------------------------------------

SELECT
    t.table_name,
    t.inmemory,
    s.populate_status AS status,
    t.num_rows
FROM
    dba_tables t
LEFT JOIN
    v$im_segments s ON t.table_name = s.segment_name AND t.owner = s.owner
WHERE
    t.owner = 'COLUMNS_HOGWARD' AND
    t.table_name IN (
        'TEACHERS', 'HOUSES', 'DORMITORIES', 'SUBJECTS',
        'STUDENTS', 'STUDENTS_SUBJECTS', 'GRADES', 'POINTS',
        'QUIDDITCH_TEAM_MEMBERS', 'GRADES_ENUM'
    )
ORDER BY
    t.table_name;

PROMPT
PROMPT UWAGI:
PROMPT - Kolumna INMEMORY powinna mieć wartość 'ENABLED' dla tabel:
PROMPT   GRADES, POINTS, STUDENTS, STUDENTS_SUBJECTS, SUBJECTS.
PROMPT - Kolumna STATUS pokazuje status populacji danych w pamięci.
PROMPT   'COMPLETED' oznacza, że dane są już w pamięci. 'NOT POPULATED'
PROMPT   może oznaczać, że zostaną załadowane przy pierwszym zapytaniu.
PROMPT - Kolumna NUM_ROWS pokazuje szacunkową liczbę wierszy (może wymagać
PROMPT   zebrania statystyk, by była dokładna).
PROMPT
PROMPT ===============================================================
PROMPT                   KONIEC WERYFIKACJI
PROMPT =============================================================== 