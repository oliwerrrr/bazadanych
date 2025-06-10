DECLARE
   workload SYS_REFCURSOR;
   curr_name VARCHAR2(32);
   plan VARCHAR2(32767);
BEGIN
    OPEN workload FOR
        SELECT workload_sql.name 
        FROM workload_sql;
    LOOP
        FETCH workload INTO curr_name;
        EXIT WHEN workload%NOTFOUND;
        
        SELECT workload_plans.plan INTO plan
        FROM workload_plans
            INNER JOIN workload_sql ON workload_plans.sql_id = workload_sql.id
        WHERE workload_sql.name = curr_name;
        DBMS_OUTPUT.PUT_LINE('================' || curr_name || '================');
        DBMS_OUTPUT.PUT_LINE(plan);
    END LOOP;
    CLOSE workload;
END;