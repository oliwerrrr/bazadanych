CREATE TABLE Students (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    gender CHAR NOT NULL,
    date_of_birth DATE NOT NULL,
    year NUMBER NOT NULL,
    hogsmeade_consent NUMBER(1) DEFAULT 0 NOT NULL,
    house_id NUMBER NOT NULL,
    dormitory_id NUMBER
);

CREATE TABLE Dormitories (
    id NUMBER NOT NULL PRIMARY KEY,
    gender CHAR NOT NULL,
    room_number NUMBER NOT NULL,
    house_id NUMBER NOT NULL
);

CREATE TABLE Houses (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(16) NOT NULL,
    symbol VARCHAR2(16) NOT NULL,
    location VARCHAR2(128),
    teacher_id NUMBER
);

CREATE TABLE Quidditch_Team_Members (
    id NUMBER NOT NULL PRIMARY KEY,
    position VARCHAR2(64),
    is_captain NUMBER(1) DEFAULT 0 NOT NULL,
    student_id NUMBER NOT NULL
);

CREATE TABLE Teachers (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    surname VARCHAR2(64) NOT NULL,
    date_of_birth DATE NOT NULL,
    date_of_employment DATE NOT NULL
);

CREATE TABLE Points (
    id NUMBER NOT NULL PRIMARY KEY,
    value NUMBER NOT NULL,
    description VARCHAR2(1024),
    award_date DATE NOT NULL,
    student_id NUMBER NOT NULL,
    teacher_id NUMBER
);

CREATE TABLE Grades (
    id NUMBER NOT NULL PRIMARY KEY,
    value VARCHAR2(1) NOT NULL,
    award_date DATE NOT NULL,
    student_id NUMBER NOT NULL,
    subject_id NUMBER NOT NULL,
    teacher_id NUMBER NOT NULL
);

CREATE TABLE Subjects (
    id NUMBER NOT NULL PRIMARY KEY,
    name VARCHAR2(64) NOT NULL,
    classroom NUMBER NOT NULL,
    year NUMBER NOT NULL,
    teacher_id NUMBER NOT NULL
);

CREATE TABLE Students_Subjects (
    student_id NUMBER NOT NULL,
    subject_id NUMBER NOT NULL
);


ALTER TABLE Students 
    ADD FOREIGN KEY (house_id) REFERENCES Houses(id);

ALTER TABLE Students 
    ADD FOREIGN KEY (dormitory_id) REFERENCES Dormitories(id);

ALTER TABLE Dormitories
    ADD FOREIGN KEY (house_id) REFERENCES Houses(id);

ALTER TABLE Houses
    ADD FOREIGN KEY (teacher_id) REFERENCES Teachers(id);

ALTER TABLE Quidditch_Team_Members
    ADD FOREIGN KEY (student_id) REFERENCES Students(id);

ALTER TABLE Points
    ADD FOREIGN KEY (student_id) REFERENCES Students(id);
    
ALTER TABLE Points
    ADD FOREIGN KEY (teacher_id) REFERENCES Teachers(id);

ALTER TABLE Grades
    ADD FOREIGN KEY (student_id) REFERENCES Students(id);

ALTER TABLE Grades
    ADD FOREIGN KEY (subject_id) REFERENCES Subjects(id);

ALTER TABLE Grades
    ADD FOREIGN KEY (teacher_id) REFERENCES Teachers(id);

ALTER TABLE Subjects
    ADD FOREIGN KEY (teacher_id) REFERENCES Teachers(id);

ALTER TABLE Students_Subjects
    ADD FOREIGN KEY (student_id) REFERENCES Students(id);

ALTER TABLE Students_Subjects
    ADD FOREIGN KEY (subject_id) REFERENCES Subjects(id);
