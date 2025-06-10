SELECT workload_sql.name,
       workload_plans.generation_time,
       COUNT(workload_plans.id) AS number_of_tests,
       MIN(workload_metrics.execution_time) AS min_time,
       MAX(workload_metrics.execution_time) AS max_time,
       AVG(workload_metrics.execution_time) AS avg_time
FROM workload_metrics
    INNER JOIN workload_plans ON workload_metrics.plan_id = workload_plans.id
    INNER JOIN workload_sql ON workload_plans.sql_id = workload_sql.id
GROUP BY workload_plans.id, 
         workload_sql.name,
         workload_plans.generation_time
ORDER BY workload_plans.id