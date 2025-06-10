CREATE OR REPLACE PROCEDURE GENERATE_PLANS 
(
    P_WORKLOAD IN SYS_REFCURSOR 
) AS 
    V_PLAN VARCHAR2(32767);
    V_SQL_ID NUMBER;
    V_NAME VARCHAR(32);
    V_SQL VARCHAR(4000);
BEGIN
    LOOP
        FETCH P_WORKLOAD INTO V_NAME, V_SQL;
        EXIT WHEN P_WORKLOAD%NOTFOUND;
        
        SELECT workload_sql.id INTO V_SQL_ID
        FROM workload_sql
        WHERE workload_sql.name = V_NAME;
        EXECUTE IMMEDIATE 'EXPLAIN PLAN FOR ' || V_SQL;
        FOR r IN (SELECT * FROM TABLE(DBMS_XPLAN.DISPLAY)) LOOP
            v_plan := v_plan || r.plan_table_output || CHR(10);
        END LOOP;
        INSERT INTO workload_plans (sql_id, generation_time, plan) VALUES (V_SQL_ID, SYSTIMESTAMP, v_plan);
        COMMIT;
    END LOOP;

    
END GENERATE_PLANS;