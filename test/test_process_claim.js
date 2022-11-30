const chai = require('chai');
const chaiAsPromised = require('chai-as-promised');
const fs = require('fs');
const mysql = require('mysql');
const _ = require('lodash');

const { processClaim } = require('../lib/process_claim.js');

chai.use(chaiAsPromised);
const { expect } = chai;


var db = null;
const schemaDir = "./schema";


function logAnyErrors(errorSource, callback) {
    return function(error, results, fields) {
        if (error) {
            console.log(`* Error from ${errorSource}: ${error}`);
            throw error;
        }

        if (callback) {
            return callback(results);
        } else {
            return results;
        }
    };
}

describe('lib/process_claim', function () {
    before(async function () {
        db = mysql.createConnection({
            host: 'db',
            user: 'root',
            password: 'tamagotchi',
            port: 3306,
            database: 'claims',
            multipleStatements: true
        });
        await db.connect(logAnyErrors('connect'));
        const sql = fs.readFileSync(`${schemaDir}/tables.sql`, 'utf8');
        await db.query(sql);
    });

    beforeEach(async function () {
        let sql = fs.readFileSync(`${schemaDir}/unload.sql`, 'utf8');
        await db.query(sql);
        sql = fs.readFileSync(`${schemaDir}/data.sql`, 'utf8');
        await db.query(sql);
    });

    after(async function () {
        await db.end();
    });

    describe('processClaim', function () {
        it('should process claim into db', async function () {
            const claimData = {
                'ssn_suffix': '1622',
                'last_name': 'Adams',
                'first_name': 'Adam',
                'date_of_birth': new Date('1975-07-05'),
                'claim_date': new Date('2020-11-30'),
                'claim_amount': 620.21
            };

            await processClaim(db, claimData);

            await new Promise((resolve, reject) => {
                db.query('SELECT * FROM employees WHERE ssn_suffix = ?',
                         ['1622'],
                         (err, employees) => {
                             if (err) {
                                 return reject(err);
                             } else {
                                 return resolve(employees);
                             }
                         });

            }).then((employees) => {
                expect(employees.length).to.equal(1);
                const employee = employees[0];
                expect(employee['employee_id']).to.equal('00000000-0000-0000-0000-000000000006');
                return employee;

            }).then(async (employee) => {

                await new Promise((resolve, reject) => {
                    db.query('SELECT * FROM claims WHERE claimant_type = \'employee\' AND claimant_id = ?',
                             [ employee['employee_id'] ],
                             (err, claims) => {
                                 if (err) {
                                     return reject(err);
                                 } else {
                                     return resolve(claims);
                                 }
                             });
                }).then((claims) => {
                    expect(claims.length).to.equal(1);
                    expect(claims[0]['claim_amount']).to.equal(620.21);
                });

            });
        });
    });
});
