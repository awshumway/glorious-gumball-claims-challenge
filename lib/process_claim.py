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
        # Search the database for the right person described in the claim
        check_employees_query = f"""
            SELECT * FROM employees 
            WHERE ssn_suffix = '{claim['ssn_suffix']}'
            AND last_name = '{claim['last_name']}'
            AND first_name = '{claim['first_name']}'
            AND date_of_birth = '{claim['date_of_birth']}'
            """
        check_dependents_query = f"""
        SELECT * FROM dependents 
            WHERE ssn_suffix = '{claim['ssn_suffix']}'
            AND last_name = '{claim['last_name']}'
            AND first_name = '{claim['first_name']}'
            AND date_of_birth = '{claim['date_of_birth']}'
            """
        check_employees_result = execute_query(db, check_employees_query)
        check_dependents_result = execute_query(db, check_dependents_query)
        # Ensure exactly one person is found
        # It seems possible that a person can be both an employee and a dependent. 
        # ASSUMPTION: It strikes me as reasonable that being a dependent would take precedence over being an employee for insurance claim purposes
        # Is it possible for  a person to be both a dependent and a retiree? I've given precedence to dependent here as well
        if len(check_dependents_result) == 1:
            # found one dependent record that matches claim data
            claim['claimant_type'] = 'dependent'
            resp_list = list(check_dependents_result[0])
            dependent_id = resp_list[0]
            claim['claimant_id'] = dependent_id
        if len(check_employees_result) == 1:
            # found one employee record that matches claim data
            resp_list = list(check_employees_result[0])
            employee_id = resp_list[0]
            claim['claimant_id'] = employee_id
            
            # check to see if this person is a retiree to assign claimant_type
            check_retirees_query = f"""
            SELECT * FROM retirees
            WHERE employee_id = '{employee_id}'
            """
            check_retirees_result=execute_query(db, check_retirees_query)
            if len(check_retirees_result) == 1:
                # update claimant type to retiree
                claim['claimant_type'] = 'retiree'
            else:
                # update claimant type to employee
                claim['claimant_type'] = 'employee'
        elif len(check_employees_result) > 1:
            print("More than one person found in employees table with details of: ", claim)
            raise Exception
        elif len(check_dependents_result) > 1:
            print("More than one person found in dependents table with details of: ", claim)
            raise Exception
        else:
            print("No records found in employees nor dependents table with details of: ", claim)
            raise Exception

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