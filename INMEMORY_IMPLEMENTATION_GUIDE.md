# Oracle DB In-Memory Feature: Implementation and Testing Guide

**Author:** Oliwer Figura

## 1. Introduction

This document provides a comprehensive, step-by-step guide to configuring, implementing, and testing the Oracle In-Memory Column Store (In-Memory) feature, specifically tailored for an Oracle Database Express Edition (XE) environment on Windows. The goal is to prepare the database for performance testing by loading tables into the In-Memory store and verifying the performance benefits for analytical queries.

We will walk through the entire process, including initial setup, troubleshooting common errors, creating dedicated users and table structures, importing data, and finally, running comparative performance tests.

### Prerequisites

- Oracle Database XE (this guide is based on 19c/21c) installed.
- `sqlplus` command-line client accessible from your terminal.
- Python 3.x installed, along with the `oracledb` and `pandas` libraries.
- The project files associated with this guide, including SQL and Python scripts.

---

## 2. Part 1: Database Configuration for In-Memory

The primary challenge with using the In-Memory feature on Oracle XE is that the default memory configuration is insufficient. We must manually reconfigure the database's memory parameters using a `pfile` (parameter file).

### 2.1. The Problem: Default Memory Limits

Attempting to start the database or enable In-Memory without changes will result in errors like:
- `ORA-12514`: Listener does not currently know of service requested. (Symptom that the DB is not running).
- `ORA-00821`: Specified value of `sga_target` is too small.
- `ORA-04031`: Unable to allocate bytes of shared memory ("shared pool").

### 2.2. Solution: Create a Custom Parameter File (`pfile`)

We will create a text-based `pfile` from scratch to control the database startup parameters precisely.

**Step 1: Locate your `control_files`**

Before creating the `pfile`, you must know the location of your control files. Connect as `sysdba` and run:

```sql
-- In sqlplus:
-- CONNECT sys/your_password as sysdba
SHOW PARAMETER control_files;
```
Note down the output. It will be something like `C:\APP\ORACLE\ORADATA\XE\CONTROL01.CTL`, `C:\APP\ORACLE\ORADATA\XE\CONTROL02.CTL`.

**Step 2: Create the `initINMEMORY.ora` file**

Create a new text file named `initINMEMORY.ora` in a known location (e.g., `C:\Users\YourUser\Desktop\bazadanych\`). Populate it with the following parameters.

**CRITICAL:** Replace the `control_files` value with the exact path you retrieved in the previous step. The path format should use single quotes and forward slashes.

```ini
# INMEMORY_IMPLEMENTATION_GUIDE.md - PFILE content
# This configuration is optimized for data import and subsequent In-Memory querying.
db_name='XE'
memory_target=2G
inmemory_size=512M # Reduced to prevent ORA-04031 during data import
pga_aggregate_target=512M
sga_target=1536M
compatible='19.0.0'
db_block_size=8192
open_cursors=300
processes=300
# IMPORTANT: Replace this path with the output from 'SHOW PARAMETER control_files;'
control_files=('C:/app/oracle/oradata/XE/control01.ctl', 'C:/app/oracle/oradata/XE/control02.ctl')
```

### 2.3. Starting the Database with the Custom `pfile`

**Step 1: Shut down the database**

Ensure any running instance is fully shut down.

```sql
-- In sqlplus, connected as sysdba:
SHUTDOWN IMMEDIATE;
```

**Step 2: Restart the Oracle Windows Service**

To ensure no old processes are lingering, it's best to restart the main Oracle service.
1. Open `services.msc` from the Run dialog (`Win + R`).
2. Find the service named `OracleServiceXE` (or similar).
3. Right-click and select **Restart**.

**Step 3: Start up using the `pfile`**

In a new terminal, connect to the idle instance and start it, explicitly pointing to your new `pfile`.

```powershell
# In cmd or PowerShell
sqlplus / as sysdba
```

```sql
-- In sqlplus:
-- Make sure to use the full, correct path to your pfile.
STARTUP PFILE='C:\Users\DUPSON\Desktop\bazadanych\initINMEMORY.ora';

-- Verify the In-Memory area is allocated:
SHOW PARAMETER inmemory_size;
-- Expected output should be 512M (or whatever you set).
```

**Step 4: (Optional) Create a new `spfile`**

To make future startups use these settings by default, create a binary `spfile` from your working `pfile`.

```sql
-- In sqlplus, while the DB is running:
CREATE SPFILE FROM PFILE='C:\Users\DUPSON\Desktop\bazadanych\initINMEMORY.ora';
```
Now, subsequent `STARTUP` commands (without a `PFILE` clause) will use these settings.

---

## 3. Part 2: Creating Users and Table Structures

**CRITICAL:** All subsequent steps must be performed on the **Pluggable Database (PDB)**, which is `XEPDB1` by default, not the root container `XE`.

### 3.1. Connecting to the Pluggable Database (`XEPDB1`)

Connecting to the wrong container (`XE`) will cause `ORA-65096: invalid common user or role name` errors when you run the user creation scripts.

Use this connection string format:
`your_user/your_password@//hostname:port/service_name`

**Example Connection Command:**
```powershell
# In cmd or PowerShell
sqlplus sys/your_password@//localhost:1521/XEPDB1 as sysdba
```

### 3.2. Script 1: Create the User (`01a_create_rowstore_user.sql`)

This script creates a dedicated user (`INMEMORY_USER`) for our testing. The key privilege is `ADVISOR`, which is required for certain In-Memory functionalities.

```sql
-- File: kolumny/01a_create_rowstore_user.sql
-- Purpose: Creates the user for In-Memory testing.
-- IMPORTANT: Run this script while connected to the XEPDB1 service.

-- Safety check to ensure connection is not to the root container
DECLARE
  v_con_name VARCHAR2(100);
BEGIN
  SELECT SYS_CONTEXT('USERENV', 'CON_NAME') INTO v_con_name FROM DUAL;
  IF v_con_name = 'CDB$ROOT' THEN
    RAISE_APPLICATION_ERROR(-20001, 'ERROR: Connected to the root container (CDB$ROOT). Please connect to the pluggable database (XEPDB1).');
  END IF;
END;
/

-- Drop user if it exists
BEGIN
   EXECUTE IMMEDIATE 'DROP USER INMEMORY_USER CASCADE';
EXCEPTION
   WHEN OTHERS THEN
      IF SQLCODE != -1918 THEN
         RAISE;
      END IF;
END;
/

-- Create the user and grant necessary privileges
CREATE USER INMEMORY_USER IDENTIFIED BY your_strong_password;
GRANT CREATE SESSION, CREATE TABLE, UNLIMITED TABLESPACE TO INMEMORY_USER;
GRANT ADVISOR TO INMEMORY_USER;

-- Verify
SELECT username, account_status FROM dba_users WHERE username = 'INMEMORY_USER';
```

### 3.3. Script 2: Create Table Structures (`02a_create_rowstore_structure.sql`)

This script creates two identical tables. `SALES_ROWSTORE` is a standard row-based table, while `SALES_INMEMORY` is configured to be populated into the In-Memory store.

The key clause is `INMEMORY PRIORITY CRITICAL`, which tells Oracle to load the table into the IM column store as soon as possible after the database opens and the table data is accessed.

```sql
-- File: kolumny/02a_create_rowstore_structure.sql
-- Purpose: Creates a standard table and an In-Memory enabled table.
-- IMPORTANT: Run this as the INMEMORY_USER.

-- Connect using: sqlplus INMEMORY_USER/your_strong_password@//localhost:1521/XEPDB1

-- Standard Row-Store Table (for comparison)
CREATE TABLE SALES_ROWSTORE (
    SALE_ID NUMBER GENERATED BY DEFAULT AS IDENTITY,
    PRODUCT_ID NUMBER NOT NULL,
    CUSTOMER_ID NUMBER NOT NULL,
    SALE_DATE DATE NOT NULL,
    SALE_AMOUNT NUMBER(10, 2) NOT NULL,
    PRODUCT_CATEGORY VARCHAR2(50),
    REGION VARCHAR2(50),
    PRIMARY KEY (SALE_ID)
);

-- In-Memory Column-Store Table
CREATE TABLE SALES_INMEMORY (
    SALE_ID NUMBER GENERATED BY DEFAULT AS IDENTITY,
    PRODUCT_ID NUMBER NOT NULL,
    CUSTOMER_ID NUMBER NOT NULL,
    SALE_DATE DATE NOT NULL,
    SALE_AMOUNT NUMBER(10, 2) NOT NULL,
    PRODUCT_CATEGORY VARCHAR2(50),
    REGION VARCHAR2(50),
    PRIMARY KEY (SALE_ID)
)
INMEMORY PRIORITY CRITICAL; -- This is the key clause!

-- Verify table creation
SELECT table_name, inmemory, inmemory_priority FROM user_tables
WHERE table_name LIKE 'SALES%';
```

---

## 4. Part 3: Data Import

Now we will populate both tables with a large amount of sample data using a Python script.

### 4.1. The Script (`import_rowstore_data.py`)

This script uses `pandas` to generate random data and `oracledb` to perform a fast bulk insert. Ensure the connection details within the script are correct.

```python
# File: src/database/import_rowstore_data.py
import oracledb
import pandas as pd
import numpy as np
from rich.progress import track

# --- Configuration ---
# IMPORTANT: Use the XEPDB1 service name for the pluggable database
DB_USER = "inmemory_user"
DB_PASSWORD = "your_strong_password"
DB_HOST = "localhost"
DB_PORT = 1521
DB_SERVICE_NAME = "XEPDB1"
DSN = f"{DB_HOST}:{DB_PORT}/{DB_SERVICE_NAME}"

NUM_ROWS = 5_000_000  # 5 Million rows
CHUNK_SIZE = 50_000

# ... (rest of the python script content remains the same) ...
# ... it generates data and inserts into both SALES_ROWSTORE and SALES_INMEMORY ...
```

### 4.2. Running the Import

Execute the script from your terminal. This will take several minutes.

```powershell
python src/database/import_rowstore_data.py
```

If you encounter an `ORA-04031` error during this process, it means the database ran out of shared pool memory. The solution is to reduce the `inmemory_size` in your `pfile` (e.g., from `512M` to `256M`), restart the database (Part 1), and run the import again.

---

## 5. Part 4: Verification and Performance Testing

After the data import, we need to verify that the `SALES_INMEMORY` table has been populated in the IM column store and then run queries to see the performance difference.

### 5.1. Verify In-Memory Population

Connect as `INMEMORY_USER` and run the following query.

```sql
-- sqlplus INMEMORY_USER/your_password@//localhost:1521/XEPDB1

-- Check In-Memory segment status
SELECT
    segment_name,
    inmemory_size,
    bytes_not_populated
FROM v$im_segments
WHERE segment_name = 'SALES_INMEMORY';
```

The first time you run this, `BYTES_NOT_POPULATED` may be non-zero. Oracle populates the table in the background after it's accessed. Run a simple `SELECT count(*) FROM SALES_INMEMORY;` to trigger the population, wait a minute, and run the verification query again. The desired state is `BYTES_NOT_POPULATED` being `0`.

### 5.2. Run Performance Queries

The following queries perform a typical analytical aggregation. We will run them against both tables and compare the execution time.

```sql
-- In sqlplus, turn on timing
SET TIMING ON;

-- Query 1: Against the standard Row-Store table
SELECT REGION, PRODUCT_CATEGORY, AVG(SALE_AMOUNT)
FROM SALES_ROWSTORE
WHERE SALE_AMOUNT > 100
GROUP BY REGION, PRODUCT_CATEGORY
ORDER BY REGION, PRODUCT_CATEGORY;

-- Query 2: Against the In-Memory table
SELECT REGION, PRODUCT_CATEGORY, AVG(SALE_AMOUNT)
FROM SALES_INMEMORY
WHERE SALE_AMOUNT > 100
GROUP BY REGION, PRODUCT_CATEGORY
ORDER BY REGION, PRODUCT_CATEGORY;
```

### 5.3. Analyze the Results

- **Elapsed Time:** Compare the "Elapsed" time printed after each query. The query against `SALES_INMEMORY` should be significantly faster.
- **Execution Plan:** To see *why* it's faster, check the execution plan.

```sql
-- For the In-Memory query
EXPLAIN PLAN FOR
SELECT REGION, PRODUCT_CATEGORY, AVG(SALE_AMOUNT)
FROM SALES_INMEMORY
WHERE SALE_AMOUNT > 100
GROUP BY REGION, PRODUCT_CATEGORY
ORDER BY REGION, PRODUCT_CATEGORY;

-- Display the plan
SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY);
```

In the execution plan for the `SALES_INMEMORY` query, you should look for the operation `TABLE ACCESS INMEMORY FULL`. This confirms the database is using the optimized, in-memory columnar access path instead of a traditional `TABLE ACCESS FULL` on-disk read.

---
**Signed,**
**Oliwer Figura** 