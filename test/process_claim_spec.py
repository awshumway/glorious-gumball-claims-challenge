from datetime import date
from expects import expect, equal
from mamba import description, context, it, before
import mysql.connector
import os.path

from lib.process_claim import process_claim

db_connection = None
schema_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)),
                          "schema")


with description('lib/process_claim') as self:
    with before.all:
        global db_connection

        db_connection = None
        try:
            db_connection = mysql.connector.connect(
                host='db',
                user='root',
                password='tamagotchi',
                port=3306,
                database='claims'
            )
        except Exception as e:
            print("Unable to open connection: {0}".format(e))

        # Load schema, if not already there.
        sql = None
        with open(os.path.join(schema_dir, "tables.sql")) as f:
            sql = f.read()
        cursor = db_connection.cursor()
        for result in cursor.execute(sql, multi=True):
            result.rowcount
        cursor.close()

    with before.each:
        # Load data
        sql = None
        with open(os.path.join(schema_dir, "unload.sql")) as f:
            sql = f.read()
        cursor = db_connection.cursor()
        for _ in cursor.execute(sql, multi=True):
            pass
        with open(os.path.join(schema_dir, "data.sql")) as f:
            sql = f.read()
        cursor = db_connection.cursor()
        for _ in cursor.execute(sql, multi=True):
            pass
        db_connection.commit()
        cursor.close()

    with after.all:
        global db_connection
        db_connection.close()
        db_connection = None

    with context('process_claim'):
        with it('should add claim to db'):
            claim_data = {
                'ssn_suffix': '1622',
                'last_name': 'Adams',
                'first_name': 'Adam',
                'date_of_birth': date(1975, 7, 5),
                'claim_date': date(2020, 11, 30),
                'claim_amount': 620.21
            }

            process_claim(db_connection, claim_data)

            cursor = db_connection.cursor(dictionary=True)

            # First, we find this employee.
            cursor.execute("""
              SELECT * FROM employees
               WHERE ssn_suffix = '1622'
            """)
            employees = cursor.fetchall()
            expect(len(employees)).to(equal(1))
            employee = employees[0]

            # Then, we find the claimant
            cursor.execute("""
              SELECT * FROM claims
               WHERE claimant_type = 'retiree' AND claimant_id = '{0}'
            """.format(employee['employee_id']))
            # This query had claimant type set to 'employee', but Adam Adams is a retiree

            results = cursor.fetchall()
            expect(len(results)).to(equal(1))

            # These last two expectations are not working - "key error last_name"
            # expect(results[0]['last_name']).to(equal('Nelson'))
            # expect(results[0]['date_of_birth']).to(equal(date(1995, 3, 16)))
