#!/usr/bin/env python

import argparse
import json
from lib.process_claim import process_claim
import sys
import mysql.connector


def main():
    # create db connection to pass to process_claim
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

    # process data from stdin
    for line in sys.stdin:
        try:
            result = process_claim(db_connection, json.loads(line))
        except Exception as e:
            print(e)
            continue

    db_connection.close()
    return


if __name__ == '__main__':
    main()
