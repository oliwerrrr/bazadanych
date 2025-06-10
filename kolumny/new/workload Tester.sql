create or replace PROCEDURE WORKLOAD_TESTER 
(
    P_WORKLOAD IN SYS_REFCURSOR,
    P_RUN_NUMBER IN NUMBER
) AS     
    V_NAME VARCHAR2(32);
    V_SQL VARCHAR2(4000);
    V_PLAN VARCHAR2(32767);
    V_PLAN_ID NUMBER;
    V_START TIMESTAMP;
    V_END TIMESTAMP;
    V_ELAPSED NUMBER;
BEGIN 
    LOOP
        FETCH P_WORKLOAD INTO V_NAME, V_SQL;
        EXIT WHEN P_WORKLOAD%NOTFOUND;
        
        SELECT MAX(workload_plans.id) INTO V_PLAN_ID
        FROM workload_plans
            INNER JOIN workload_sql ON workload_plans.sql_id = workload_sql.id
        WHERE workload_sql.name = V_NAME;
        EXECUTE IMMEDIATE 'ALTER SYSTEM FLUSH BUFFER_CACHE';
        EXECUTE IMMEDIATE 'ALTER SYSTEM FLUSH SHARED_POOL';
        V_START := SYSTIMESTAMP;
        EXECUTE IMMEDIATE V_SQL;
        V_END := SYSTIMESTAMP;
        ROLLBACK;
        V_ELAPSED := EXTRACT(SECOND FROM (V_END - V_START)) * 1000;
        INSERT INTO workload_metrics (plan_id, run_number, execution_time) VALUES (v_plan_id, P_RUN_NUMBER, v_elapsed);
        COMMIT;
    END LOOP;
END WORKLOAD_TESTER;