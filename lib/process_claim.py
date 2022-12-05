from datetime import date
import json


def process_claim(db, claim):
    print("Claim: ", claim)
    # check if the claim has already been processed - no point in doing it twice!
    # One pitfall of this approach is that it is conceivable that a person could have two claims for the same amount on the same day.
    check_claims_query = f"""
        SELECT c.* FROM claims c
        JOIN employees e
        ON c.claimant_id = e.employee_id
        WHERE e.ssn_suffix = '{claim['ssn_suffix']}'
        AND e.last_name = '{claim['last_name']}'
        AND e.first_name = '{claim['first_name']}'
        AND e.date_of_birth = '{claim['date_of_birth']}' 
        AND c.claim_date = '{claim['claim_date']}' 
        AND c.claim_amount = '{claim['claim_amount']}' 
    """
    check_claims_result = execute_query(db, check_claims_query)
    if len(check_claims_result) == 1:
        resp_json = json.dumps(check_claims_result[0], default=str)
        claim_id = resp_json[0]
        print(f"Claim has already been processed. Claim ID is {claim_id}")
    else:
        # Search the database for the right person in the employees table first
        check_employees_query = f"""
            SELECT * FROM employees 
            WHERE ssn_suffix = '{claim['ssn_suffix']}'
            AND last_name = '{claim['last_name']}'
            AND first_name = '{claim['first_name']}'
            AND date_of_birth = '{claim['date_of_birth']}'
            """
        check_employees_result = execute_query(db, check_employees_query)

        # Ensure exactly one person is found
        if len(check_employees_result) == 1:
            # found one employee record that matches claim data
            resp_json = json.dumps(check_employees_result[0], default=str)
            employee_id = resp_json[0]
        elif len(check_employees_result) > 1:
            print("More than one person found with details of: ", claim)
            raise Exception
        else:
            print("No records found in employees table with details of: ", claim)
            raise Exception

        # claimant_type can be employee, dependent, or retiree. 
        # Based on given data,it appears that no person could be in the dependents or retirees table 
        # without also being in the employees table. If this is untrue, this code will need to be refactored
        # Check if the person appears in dependents or retirees table to determine the claimant_type
        check_dependents_query = f"""
            SELECT * FROM dependents
            WHERE dependent_id = '{employee_id}'
        """
        check_retirees_query = f"""
            SELECT * FROM retirees
            WHERE employee_id = '{employee_id}'
        """
        check_dependents_result=execute_query(db, check_dependents_query)
        check_retirees_result=execute_query(db, check_retirees_query)

        # Can a clamant be both a dependent and a retiree? If so, which should take precedence?
        # I've written this to use dependent as precident over retiree.
        if len(check_dependents_result) == 1:
            # update claimant type to dependent
            claim['claimant_type'] = 'dependent'
        elif len(check_retirees_result) == 1:
            # update claimant type to retiree
            claim['claimant_type'] = 'retiree'
        else:
            # update claimant type to employee
            claim['claimant_type'] = 'employee'

        # Generate unique UUID for the claim ID
        
        # Write to database


    pass


def execute_query(db, query:str):
    mycursor = db.cursor()
    try:
        mycursor.execute(query)
    except Exception:
        print("Unable to execute query. Failed query:", query)
        raise
    try:
        result = mycursor.fetchall()
    except Exception:
        print("Unable to retrieve result from query execution")
        raise
    
    return result