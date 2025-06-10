-- =====================================================================
-- TWORZENIE STRUKTURY BAZY DANYCH HOGWARTS (WERSJA KOLUMNOWA)
-- =====================================================================
-- 
-- Ten skrypt odtwarza całą strukturę bazy danych z włączonym 
-- magazynem In-Memory dla wybranych tabel analitycznych.
--
-- Uruchom go jako użytkownik `Columns_hogward` PO uruchomieniu
-- skryptu `01_create_user.sql` przez administratora.
-- =====================================================================

SET SERVEROUTPUT ON;

-- =====================================================================
-- USUŃ ISTNIEJĄCE OBIEKTY (jeśli istnieją)
-- =====================================================================
BEGIN
    FOR i IN (SELECT sequence_name FROM user_sequences WHERE sequence_name IN ('TEACHERS_SEQ', 'SUBJECTS_SEQ', 'STUDENTS_SEQ', 'DORMITORIES_SEQ', 'GRADES_SEQ', 'POINTS_SEQ', 'QUIDDITCH_SEQ')) LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || i.sequence_name;
    END LOOP;
    FOR i IN (SELECT table_name FROM user_tables WHERE table_name IN ('QUIDDITCH_TEAM_MEMBERS', 'POINTS', 'GRADES', 'STUDENTS_SUBJECTS', 'STUDENTS', 'SUBJECTS', 'DORMITORIES', 'HOUSES', 'TEACHERS', 'GRADES_ENUM')) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || i.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('✅ Stare tabele i sekwencje usunięte.');
EXCEPTION
    WHEN OTHERS THEN
        DBMS_OUTPUT.PUT_LINE('INFO: Niektóre tabele lub sekwencje mogły nie istnieć, co jest oczekiwane przy pierwszym uruchomieniu.');
END;
/

-- =====================================================================
-- UTWÓRZ SEKWENCJE
-- =====================================================================
CREATE SEQUENCE teachers_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE subjects_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE students_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE dormitories_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE grades_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE points_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE quidditch_seq START WITH 1 INCREMENT BY 1;
PROMPT ✅ Sekwencje utworzone.

-- =====================================================================
-- UTWÓRZ TABELE
-- =====================================================================

-- Tabele wymiarów (małe, standardowe, bez In-Memory)
-------------------------------------------------------------
CREATE TABLE teachers (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    date_of_birth DATE NOT NULL,
    date_of_employment DATE NOT NULL
);

CREATE TABLE houses (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    symbol VARCHAR2(16) NOT NULL,
    location VARCHAR2(128) NOT NULL,
    teacher_id NUMBER,
    CONSTRAINT fk_houses_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
);

CREATE TABLE dormitories (
    id NUMBER NOT NULL PRIMARY KEY,
    gender CHAR(1) NOT NULL,
    room_number NUMBER NOT NULL,
    house_id NUMBER NOT NULL,
    CONSTRAINT fk_dormitories_house FOREIGN KEY (house_id) REFERENCES houses(id),
    CONSTRAINT chk_gender CHECK (gender IN ('M', 'F'))
);

CREATE TABLE grades_enum (
    symbol VARCHAR2(1) PRIMARY KEY,
    value NUMBER(2) NOT NULL,
    description VARCHAR2(20)
);

CREATE TABLE quidditch_team_members (
    id NUMBER NOT NULL PRIMARY KEY,
    position VARCHAR2(64) NOT NULL,
    is_captain NUMBER(1) DEFAULT 0 NOT NULL,
    student_id NUMBER NOT NULL
);

PROMPT ✅ Małe tabele pomocnicze utworzone.

-- Tabele analityczne (duże, kluczowe dla wydajności, z In-Memory)
---------------------------------------------------------------------
-- Tabela SUBJECTS: Często łączona z ocenami i uczniami.
-- In-Memory przyspiesza te złączenia.
CREATE TABLE subjects (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(128) NOT NULL,
    classroom VARCHAR2(64) NOT NULL,
    year NUMBER NOT NULL,
    teacher_id NUMBER NOT NULL,
    CONSTRAINT fk_subjects_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
) INMEMORY PRIORITY HIGH MEMCOMPRESS FOR QUERY LOW;

-- Tabela STUDENTS: Centralna, duża tabela wymiarów.
-- In-Memory przyspiesza filtrowanie i złączenia z tabelami faktów.
CREATE TABLE students (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    gender CHAR(1) NOT NULL,
    date_of_birth DATE NOT NULL,
    year NUMBER NOT NULL,
    hogsmeade_consent NUMBER(1) DEFAULT 0 NOT NULL,
    house_id NUMBER NOT NULL,
    dormitory_id NUMBER,
    CONSTRAINT fk_students_house FOREIGN KEY (house_id) REFERENCES houses(id),
    CONSTRAINT fk_students_dormitory FOREIGN KEY (dormitory_id) REFERENCES dormitories(id),
    CONSTRAINT chk_student_gender CHECK (gender IN ('M', 'F')),
    CONSTRAINT chk_hogsmeade CHECK (hogsmeade_consent IN (0, 1))
) INMEMORY PRIORITY HIGH MEMCOMPRESS FOR QUERY LOW;

-- Tabela STUDENTS_SUBJECTS: Tabela łącząca M:N.
-- Kluczowa dla wydajności złączeń między uczniami a przedmiotami.
CREATE TABLE students_subjects (
    student_id NUMBER NOT NULL,
    subject_id NUMBER NOT NULL,
    PRIMARY KEY (student_id, subject_id),
    CONSTRAINT fk_ss_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_ss_subject FOREIGN KEY (subject_id) REFERENCES subjects(id)
) INMEMORY PRIORITY HIGH MEMCOMPRESS FOR QUERY LOW;

-- Tabela GRADES: Duża tabela faktów (miliony rekordów).
-- In-Memory drastycznie przyspiesza agregacje i skanowanie.
CREATE TABLE grades (
    id NUMBER NOT NULL PRIMARY KEY,
    value VARCHAR2(1) NOT NULL,
    award_date DATE NOT NULL,
    student_id NUMBER NOT NULL,
    subject_id NUMBER NOT NULL,
    teacher_id NUMBER NOT NULL,
    CONSTRAINT fk_grades_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_grades_subject FOREIGN KEY (subject_id) REFERENCES subjects(id),
    CONSTRAINT fk_grades_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id),
    CONSTRAINT fk_grades_enum FOREIGN KEY (value) REFERENCES grades_enum(symbol)
) INMEMORY PRIORITY CRITICAL MEMCOMPRESS FOR QUERY LOW;

-- Tabela POINTS: Duża tabela faktów (miliony rekordów).
-- In-Memory drastycznie przyspiesza agregacje i skanowanie.
CREATE TABLE points (
    id NUMBER NOT NULL PRIMARY KEY,
    value NUMBER NOT NULL,
    description VARCHAR2(1024),
    award_date DATE NOT NULL,
    student_id NUMBER NOT NULL,
    teacher_id NUMBER NOT NULL,
    CONSTRAINT fk_points_student FOREIGN KEY (student_id) REFERENCES students(id),
    CONSTRAINT fk_points_teacher FOREIGN KEY (teacher_id) REFERENCES teachers(id)
) INMEMORY PRIORITY CRITICAL MEMCOMPRESS FOR QUERY LOW;

PROMPT ✅ Duże tabele analityczne (z In-Memory) utworzone.

-- =====================================================================
-- UZUPEŁNIJ DANE POMOCNICZE
-- =====================================================================
INSERT INTO grades_enum VALUES ('T', 1, 'Troll');
INSERT INTO grades_enum VALUES ('D', 2, 'Dreadful');
INSERT INTO grades_enum VALUES ('P', 3, 'Poor');
INSERT INTO grades_enum VALUES ('A', 4, 'Acceptable');
INSERT INTO grades_enum VALUES ('E', 5, 'Exceeds Expectations');
INSERT INTO grades_enum VALUES ('O', 6, 'Outstanding');
COMMIT;
PROMPT ✅ Tabela GRADES_ENUM uzupełniona danymi.

-- =====================================================================
-- DODAJ OSTATNIE WIĘZY (po utworzeniu tabeli STUDENTS)
-- =====================================================================
ALTER TABLE quidditch_team_members ADD CONSTRAINT fk_qttm_student_final FOREIGN KEY (student_id) REFERENCES students(id);
PROMPT ✅ Dodano ostatnie więzy klucza obcego.

-- =====================================================================
-- SPRAWDŹ UTWORZONE TABELE
-- =====================================================================
PROMPT
PROMPT 📊 SPRAWDZAM UTWORZONE TABELE (statystyki będą puste do czasu importu danych):
SELECT table_name, inmemory, num_rows 
FROM user_tables 
WHERE table_name IN (
    'TEACHERS', 'HOUSES', 'DORMITORIES', 'SUBJECTS', 
    'STUDENTS', 'STUDENTS_SUBJECTS', 'GRADES', 'POINTS', 
    'QUIDDITCH_TEAM_MEMBERS', 'GRADES_ENUM'
)
ORDER BY table_name;

PROMPT
PROMPT ===============================================================
PROMPT          STRUKTURA BAZY DANYCH (KOLUMNOWA) UTWORZONA!
PROMPT ===============================================================

