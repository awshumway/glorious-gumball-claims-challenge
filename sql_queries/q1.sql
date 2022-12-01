-- How many employees have become retirees, 
-- versus how many have just dropped out of the Glorious Gumball system?

-- We can find all retirees in the retirees table
-- Termination date is null for current employees, and has a value for those who have left/retired
-- Termination date is also nullable in the retirees table, so we can't rely just on this field

SELECT DISTINCT COUNT(r.employee_id) AS Retirees_Count, 
(SELECT DISTINCT COUNT(e.employee_ID)
FROM employees e
LEFT JOIN retirees r
ON r.employee_id = e.employee_id
WHERE e.term_date is not null
AND r.employee_id is null) AS Dropped_Count
FROM retirees r;
