CREATE OR REPLACE PROCEDURE GENERATE_PLANS 
(
    P_WORKLOAD IN SYS_REFCURSOR 
) AS 
    V_PLAN CLOB;
    V_SQL_ID NUMBER;
    V_NAME VARCHAR2(32);
    V_SQL VARCHAR2(4000);
BEGIN
    LOOP
        FETCH P_WORKLOAD INTO V_NAME, V_SQL;
        EXIT WHEN P_WORKLOAD%NOTFOUND;
        
        V_PLAN := '';
        
        SELECT workload_sql.id INTO V_SQL_ID
        FROM workload_sql
        WHERE workload_sql.name = V_NAME;

        EXECUTE IMMEDIATE 'EXPLAIN PLAN FOR ' || V_SQL;

        FOR r IN (SELECT plan_table_output FROM TABLE(DBMS_XPLAN.DISPLAY)) LOOP
            V_PLAN := V_PLAN || r.plan_table_output || CHR(10);
        END LOOP;
        
        INSERT INTO workload_plans (sql_id, generation_time, plan) VALUES (V_SQL_ID, SYSTIMESTAMP, V_PLAN);
        COMMIT;
    END LOOP;
END GENERATE_PLANS;