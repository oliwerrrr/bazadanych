-- =====================================================================
-- SKRYPT DIAGNOSTYCZNY DLA ORACLE IN-MEMORY
-- =====================================================================
--
-- Ten skrypt pomaga zdiagnozować, dlaczego baza danych nie używa
-- magazynu kolumnowego, mimo że tabele zostały oznaczone jako INMEMORY.
--
-- Uruchom go jako użytkownik z uprawnieniami administratora (np. SYSTEM),
-- aby mieć dostęp do widoków systemowych (v$).
-- =====================================================================

SET SERVEROUTPUT ON;
SET LINESIZE 200;
COLUMN parameter FORMAT A30;
COLUMN value FORMAT A40;
COLUMN segment_name FORMAT A30;
COLUMN populate_status FORMAT A20;
COLUMN bytes_not_populated FORMAT 999,999,999,999;

PROMPT
PROMPT =====================================================================
PROMPT 1. SPRAWDZENIE PARAMETRÓW INICJALIZACYJNYCH
PROMPT =====================================================================
PROMPT Kluczowy parametr to 'inmemory_size'. Musi być ustawiony na wartość
PROMPT większą niż 0 (zalecane kilka GB dla Twojego zestawu danych).
PROMPT

SELECT name AS parameter, value
FROM v$parameter
WHERE name IN ('inmemory_size', 'inmemory_query', 'optimizer_inmemory_aware');

PROMPT
PROMPT =====================================================================
PROMPT 2. SPRAWDZENIE STANU OBSZARU PAMIĘCI IN-MEMORY
PROMPT =====================================================================
PROMPT Sprawdza, ile pamięci jest dostępne, a ile używane.
PROMPT Jeśli 'Total Size' = 0, oznacza to, że obszar nie został zainicjowany.
PROMPT

SELECT
    pool,
    alloc_bytes AS "Total Size (Bytes)",
    used_bytes AS "Used Size (Bytes)",
    (alloc_bytes - used_bytes) AS "Free Space (Bytes)"
FROM v$inmemory_area;

PROMPT
PROMPT =====================================================================
PROMPT 3. SPRAWDZENIE STATUSU POPULACJI SEGMENTÓW (TABEL)
PROMPT =====================================================================
PROMPT Pokazuje, które tabele są ładowane i czy proces się zakończył.
PROMPT STATUS 'COMPLETED' jest oczekiwany.
PROMPT Jeśli 'BYTES_NOT_POPULATED' > 0, oznacza to, że zabrakło miejsca w pamięci.
PROMPT

SELECT
    segment_name,
    populate_status,
    bytes,
    inmemory_size,
    bytes_not_populated
FROM v$im_segments
WHERE owner = 'COLUMNS_HOGWARD'
ORDER BY segment_name;

PROMPT
PROMPT =====================================================================
PROMPT                   KONIEC DIAGNOSTYKI
PROMPT =====================================================================
PROMPT
PROMPT WNIOSKI:
PROMPT - Jeśli 'inmemory_size' to 0 lub jest zbyt mały, musisz go zwiększyć
PROMPT   i zrestartować bazę danych: ALTER SYSTEM SET inmemory_size = 4G SCOPE=SPFILE;
PROMPT - Jeśli 'BYTES_NOT_POPULATED' jest większe od zera, oznacza to, że
PROMPT   pamięć In-Memory jest pełna. Zwiększ 'inmemory_size'.
PROMPT - Upewnij się, że parametr 'inmemory_query' jest ustawiony na 'ENABLE'.
PROMPT ===================================================================== 