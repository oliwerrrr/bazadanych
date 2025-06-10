DECLARE
   workload SYS_REFCURSOR;
BEGIN
    DELETE FROM workload_metrics;
    DELETE FROM workload_plans;
    
    OPEN workload FOR
        SELECT name, code FROM WORKLOAD_SQL;
    generate_plans(workload);
    CLOSE workload;
    
    FOR i IN 1..10 LOOP
        OPEN workload FOR
            SELECT name, code FROM WORKLOAD_SQL;
        workload_tester(workload);
        CLOSE workload;
    END LOOP;
END;