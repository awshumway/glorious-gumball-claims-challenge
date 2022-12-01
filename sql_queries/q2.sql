-- What the average number of dependents per employee?
-- First we will need to count the # of dependents each employee has, then find the average

SELECT AVG(subquery.count_dependents) 
AS Average_Dependents
FROM (
    SELECT DISTINCT e.employee_id, COUNT(d.employee_id) as count_dependents
    FROM employees e
    LEFT JOIN dependents d
    ON e.employee_id = d.employee_id
    GROUP BY e.employee_id
    ) AS subquery;
