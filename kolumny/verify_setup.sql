-- =====================================================================
-- SKRYPT WERYFIKACYJNY: ŚRODOWISKO BAZY KOLUMNOWEJ HOGWARTS
-- =====================================================================
--
-- Uruchom ten skrypt jako użytkownik z uprawnieniami DBA (np. SYS)
-- połączony z bazą PDB (XEPDB1), aby sprawdzić, czy wszystko jest
-- gotowe do importu danych i testów wydajnościowych.
--
-- =====================================================================

SET SERVEROUTPUT ON
SET PAGESIZE 100
SET LINESIZE 200

PROMPT ====================================================================
PROMPT KROK 1: Weryfikacja parametrów globalnych In-Memory
PROMPT ====================================================================

COLUMN name FORMAT A30
COLUMN value FORMAT A20

SELECT name, value 
FROM v$parameter 
WHERE name IN ('inmemory_size', 'inmemory_query');

PROMPT
PROMPT Sprawdzam alokację pamięci w SGA...
COLUMN component FORMAT A30
COLUMN current_size_mb FORMAT 999,999.99

SELECT 
    component,
    current_size/1024/1024 as current_size_mb
FROM v$sga_dynamic_components
WHERE component = 'In-Memory Area';

PROMPT
PROMPT Oczekiwany wynik: Powinieneś zobaczyć "In-Memory Area" z rozmiarem > 0 MB.
PROMPT Jeśli rozmiar to 0, baza danych nie została uruchomiona z włączonym In-Memory.

PROMPT
PROMPT ====================================================================
PROMPT KROK 2: Weryfikacja użytkownika COLUMNS_HOGWARD
PROMPT ====================================================================

DECLARE
  v_user_exists NUMBER;
  v_priv_exists NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_user_exists FROM dba_users WHERE username = 'COLUMNS_HOGWARD';
  IF v_user_exists > 0 THEN
    DBMS_OUTPUT.PUT_LINE('✅ Użytkownik COLUMNS_HOGWARD istnieje.');
    
    -- Sprawdź kluczowe uprawnienie
    SELECT COUNT(*) INTO v_priv_exists 
    FROM dba_sys_privs 
    WHERE grantee = 'COLUMNS_HOGWARD' AND privilege = 'ADVISOR';
    
    IF v_priv_exists > 0 THEN
      DBMS_OUTPUT.PUT_LINE('✅ Użytkownik COLUMNS_HOGWARD ma uprawnienie ADVISOR.');
    ELSE
      DBMS_OUTPUT.PUT_LINE('❌ BŁĄD: Użytkownik COLUMNS_HOGWARD NIE MA uprawnienia ADVISOR!');
    END IF;
    
  ELSE
    DBMS_OUTPUT.PUT_LINE('❌ BŁĄD: Użytkownik COLUMNS_HOGWARD nie istnieje!');
  END IF;
END;
/

PROMPT
PROMPT ====================================================================
PROMPT KROK 3: Weryfikacja struktury tabel w schemacie COLUMNS_HOGWARD
PROMPT ====================================================================
PROMPT Oczekiwany wynik: Poniższe tabele powinny mieć status 'ENABLED'
PROMPT i odpowiednie priorytety (CRITICAL/HIGH).
PROMPT

COLUMN table_name FORMAT A20
COLUMN inmemory FORMAT A10
COLUMN inmemory_priority FORMAT A10
COLUMN inmemory_compression FORMAT A25

SELECT 
    table_name,
    inmemory,
    inmemory_priority,
    inmemory_compression
FROM dba_tables 
WHERE owner = 'COLUMNS_HOGWARD' 
  AND table_name IN ('GRADES', 'POINTS', 'STUDENTS', 'SUBJECTS', 'STUDENTS_SUBJECTS')
ORDER BY inmemory_priority, table_name;

PROMPT
PROMPT ====================================================================
PROMPT KROK 4: Weryfikacja statusu populacji (przed importem danych)
PROMPT ====================================================================
PROMPT Oczekiwany wynik: Poniższa lista powinna być PUSTA, ponieważ
PROMPT dane nie zostały jeszcze zaimportowane. Po imporcie i odczekaniu
PROMPT chwili, powinny się tu pojawić tabele ze statusem 'COMPLETED'.
PROMPT

COLUMN owner FORMAT A15
COLUMN segment_name FORMAT A20
COLUMN populate_status FORMAT A15
COLUMN INMEMORY_SIZE_MB FORMAT 999,999.99
COLUMN BYTES_NOT_POPULATED_MB FORMAT 999,999.99

SELECT 
    owner,
    segment_name,
    populate_status,
    inmemory_size/1024/1024 AS INMEMORY_SIZE_MB,
    bytes_not_populated/1024/1024 AS NOT_POPULATED_MB
FROM v$im_segments
WHERE owner = 'COLUMNS_HOGWARD';

PROMPT
PROMPT ====================================================================
PROMPT PODSUMOWANIE KONTROLI
PROMPT ====================================================================
PROMPT Jeśli wszystkie punkty w krokach 1, 2 i 3 wyglądają dobrze
PROMPT (In-Memory Area > 0, użytkownik istnieje z uprawnieniami,
PROMPT a tabele mają status INMEMORY ENABLED z priorytetami),
PROMPT to środowisko jest GOTOWE do importu danych.
PROMPT ==================================================================== 