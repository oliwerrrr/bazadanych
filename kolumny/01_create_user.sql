-- =====================================================================
-- KROK 1: UTWORZENIE UŻYTKOWNIKA `Columns_hogward`
-- =====================================================================
--
-- Tę część skryptu należy uruchomić jako użytkownik z uprawnieniami
-- administratora (np. SYS lub SYSTEM), **koniecznie połączony z bazą PDB**,
-- czyli XEPDB1.
--
-- PRAWIDŁOWE POŁĄCZENIE: sqlplus sys/twoje_haslo@localhost:1521/XEPDB1 as sysdba
-- BŁĘDNE POŁĄCZENIE:    sqlplus sys/twoje_haslo@localhost:1521/XE as sysdba
--
-- Hasło dla nowego użytkownika to: Columns_hogward123
-- =====================================================================
SET SERVEROUTPUT ON;

-- Sprawdzenie, czy połączenie jest z właściwą bazą danych (PDB)
DECLARE
  v_con_name VARCHAR2(128);
BEGIN
  SELECT SYS_CONTEXT('USERENV', 'CON_NAME') INTO v_con_name FROM DUAL;
  IF v_con_name != 'XEPDB1' THEN
    RAISE_APPLICATION_ERROR(-20001, 'BŁĄD: Ten skrypt musi być uruchomiony w PDB (XEPDB1), a nie w "' || v_con_name || '". Zmień swoje połączenie w SQL Developerze, aby używać nazwy usługi (Service Name) XEPDB1.');
  END IF;
END;
/

PROMPT
PROMPT 🔌 KROK 1: TWORZENIE UŻYTKOWNIKA `Columns_hogward` w PDB (XEPDB1)...
PROMPT ----------------------------------------------------

BEGIN
    EXECUTE IMMEDIATE 'DROP USER Columns_hogward CASCADE';
    DBMS_OUTPUT.PUT_LINE('✅ Poprzedni użytkownik Columns_hogward usunięty.');
EXCEPTION
    WHEN OTHERS THEN
        IF SQLCODE = -1918 THEN
            DBMS_OUTPUT.PUT_LINE('INFO: Użytkownik Columns_hogward nie istniał.');
        ELSE
            RAISE;
        END IF;
END;
/

CREATE USER Columns_hogward IDENTIFIED BY Columns_hogward123;

-- Nadanie podstawowych uprawnień oraz ADVISOR, który jest potrzebny do In-Memory
GRANT CONNECT, RESOURCE, CREATE VIEW, UNLIMITED TABLESPACE, ADVISOR TO Columns_hogward;

PROMPT ✅ Użytkownik Columns_hogward utworzony i nadano uprawnienia.
PROMPT
PROMPT ===============================================================
PROMPT WAŻNE - PAMIĘĆ IN-MEMORY
PROMPT ===============================================================
PROMPT
PROMPT Aby skorzystać z magazynu kolumnowego, upewnij się, że w bazie
PROMPT danych jest skonfigurowany obszar pamięci In-Memory.
PROMPT Jeśli nie, uruchom jako SYSTEM (wymaga restartu bazy):
PROMPT
PROMPT ALTER SYSTEM SET INMEMORY_SIZE = 500M SCOPE=SPFILE;
PROMPT SHUTDOWN IMMEDIATE;
PROMPT STARTUP;
PROMPT
PROMPT ===============================================================
PROMPT
PROMPT 🚀 NASTĘPNY KROK:
PROMPT    Połącz się z bazą jako nowy użytkownik `Columns_hogward`
PROMPT    (np. przez XEPDB1) i uruchom skrypt:
PROMPT    kolumny/02_create_columnar_structure.sql
PROMPT
PROMPT =============================================================== 