-- Script to create the ROWSTORE_HOGWARD schema with standard, row-based tables.
-- NO IN-MEMORY clauses are used.

SET ECHO ON
WHENEVER SQLERROR EXIT SQL.SQLCODE

PROMPT ====================================================================
PROMPT Creating tables for ROWSTORE_HOGWARD...
PROMPT ====================================================================

-- Drop existing tables to ensure a clean slate
BEGIN
    FOR t IN (SELECT table_name FROM user_tables) LOOP
        EXECUTE IMMEDIATE 'DROP TABLE ' || t.table_name || ' CASCADE CONSTRAINTS';
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('All existing tables dropped.');
END;
/

-- Drop existing sequences
BEGIN
    FOR s IN (SELECT sequence_name FROM user_sequences) LOOP
        EXECUTE IMMEDIATE 'DROP SEQUENCE ' || s.sequence_name;
    END LOOP;
    DBMS_OUTPUT.PUT_LINE('All existing sequences dropped.');
END;
/


-- Create sequences for primary keys
CREATE SEQUENCE teachers_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE subjects_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE houses_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE dormitories_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE students_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE grades_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE points_seq START WITH 1 INCREMENT BY 1;
CREATE SEQUENCE quidditch_seq START WITH 1 INCREMENT BY 1;

PROMPT ✅ Sequences created.

-- Table Creation

CREATE TABLE Teachers (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    date_of_birth DATE,
    date_of_employment DATE
);

CREATE TABLE Houses (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(64) NOT NULL UNIQUE,
    symbol VARCHAR2(16),
    location VARCHAR2(128),
    teacher_id NUMBER,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
);

CREATE TABLE Dormitories (
    id NUMBER PRIMARY KEY,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    room_number NUMBER,
    house_id NUMBER,
    FOREIGN KEY (house_id) REFERENCES Houses(id)
);

CREATE TABLE Students (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    gender CHAR(1) CHECK (gender IN ('M', 'F')),
    date_of_birth DATE,
    year NUMBER CHECK (year BETWEEN 1 AND 7),
    hogsmeade_consent NUMBER(1) CHECK (hogsmeade_consent IN (0, 1)),
    house_id NUMBER,
    dormitory_id NUMBER,
    FOREIGN KEY (house_id) REFERENCES Houses(id),
    FOREIGN KEY (dormitory_id) REFERENCES Dormitories(id)
);

CREATE TABLE Subjects (
    id NUMBER PRIMARY KEY,
    name VARCHAR2(128) NOT NULL,
    classroom VARCHAR2(32),
    year NUMBER,
    teacher_id NUMBER,
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
);

CREATE TABLE Grades_Enum (
    symbol CHAR(1) PRIMARY KEY,
    description VARCHAR2(32) NOT NULL,
    value NUMBER NOT NULL UNIQUE
);

CREATE TABLE Grades (
    id NUMBER PRIMARY KEY,
    value CHAR(1),
    award_date DATE,
    student_id NUMBER,
    subject_id NUMBER,
    teacher_id NUMBER,
    FOREIGN KEY (student_id) REFERENCES Students(id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id),
    FOREIGN KEY (value) REFERENCES Grades_Enum(symbol)
);

CREATE TABLE Points (
    id NUMBER PRIMARY KEY,
    value NUMBER NOT NULL,
    description VARCHAR2(256),
    award_date DATE,
    student_id NUMBER,
    teacher_id NUMBER,
    FOREIGN KEY (student_id) REFERENCES Students(id),
    FOREIGN KEY (teacher_id) REFERENCES Teachers(id)
);

CREATE TABLE Students_Subjects (
    student_id NUMBER,
    subject_id NUMBER,
    PRIMARY KEY (student_id, subject_id),
    FOREIGN KEY (student_id) REFERENCES Students(id),
    FOREIGN KEY (subject_id) REFERENCES Subjects(id)
);

CREATE TABLE Quidditch_Team_Members (
    id NUMBER PRIMARY KEY,
    position VARCHAR2(32),
    is_captain NUMBER(1) CHECK (is_captain IN (0, 1)),
    student_id NUMBER,
    FOREIGN KEY (student_id) REFERENCES Students(id)
);

PROMPT ✅ All tables created successfully for ROWSTORE_HOGWARD.

-- Populate Grades_Enum lookup table
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('O', 'Outstanding', 7);
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('E', 'Exceeds Expectations', 6);
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('A', 'Acceptable', 5);
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('P', 'Poor', 4);
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('D', 'Dreadful', 3);
INSERT INTO Grades_Enum (symbol, description, value) VALUES ('T', 'Troll', 2);

PROMPT ✅ Grades_Enum lookup table populated.

EXIT; 