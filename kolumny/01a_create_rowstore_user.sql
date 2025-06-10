-- Script to create the ROWSTORE_HOGWARD user for baseline performance testing.
-- This user will have standard tables with NO In-Memory optimizations.

SET ECHO ON
WHENEVER SQLERROR EXIT SQL.SQLCODE

PROMPT ====================================================================
PROMPT Verifying connection is to the Pluggable Database (XEPDB1)...
PROMPT ====================================================================
DECLARE
    v_db_name VARCHAR2(100);
BEGIN
    SELECT SYS_CONTEXT('USERENV', 'CON_NAME') INTO v_db_name FROM DUAL;
    IF v_db_name != 'XEPDB1' THEN
        RAISE_APPLICATION_ERROR(-20001, 'ERROR: Must be connected to the XEPDB1 pluggable database, not ' || v_db_name);
    ELSE
        DBMS_OUTPUT.PUT_LINE('✅ Connected to XEPDB1.');
    END IF;
END;
/

PROMPT ====================================================================
PROMPT Creating user ROWSTORE_HOGWARD...
PROMPT ====================================================================

DECLARE
    v_user_exists NUMBER;
BEGIN
    SELECT COUNT(*) INTO v_user_exists FROM dba_users WHERE username = 'ROWSTORE_HOGWARD';
    IF v_user_exists > 0 THEN
        EXECUTE IMMEDIATE 'DROP USER ROWSTORE_HOGWARD CASCADE';
        DBMS_OUTPUT.PUT_LINE('User ROWSTORE_HOGWARD dropped.');
    END IF;
END;
/

CREATE USER ROWSTORE_HOGWARD IDENTIFIED BY Rowstore_hogward123;

-- Grant necessary privileges
GRANT CREATE SESSION TO ROWSTORE_HOGWARD;
GRANT CREATE TABLE TO ROWSTORE_HOGWARD;
GRANT UNLIMITED TABLESPACE TO ROWSTORE_HOGWARD;
GRANT ADVISOR TO ROWSTORE_HOGWARD; -- For running performance analysis tools
GRANT CREATE SEQUENCE TO ROWSTORE_HOGWARD;

PROMPT ✅ User ROWSTORE_HOGWARD created successfully.
PROMPT ✅ Granted base privileges.

EXIT; 