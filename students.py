
# Import a CSV file from moodle into students.db (sqlite).
# Sanity check the mappings.

import argparse
import csv
import sqlite3

def handle_file(db, fname):
    cur = db.cursor()
    with open(fname) as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            cur.execute('SELECT id, email FROM studentid WHERE id = ? or email = ?',
                              (row['ID number'], row['Email address']))
            dbrows = cur.fetchall()
            if len(dbrows) == 0:
                cur.execute('INSERT INTO studentid (id, email) VALUES (?, ?)',
                              (row['ID number'], row['Email address']))
            elif len(dbrows) == 1:
                if int(dbrows[0][0]) != int(row['ID number']) or \
                   dbrows[0][1] != row['Email address']:
                    print(f"Conflict: CSV {row['ID number']}, {row['Email address']} DB {dbrows[0][1]}, {dbrows[0][1]}")
            else:
                print(f"Conflict: CSV {row['ID number']}, {row['Email address']}")
                for i in dbrows:
                    print(f"DB {i[0]}, {i[1]}")
    db.commit()    

def main():
    parser = argparse.ArgumentParser("student id parser")
    parser.add_argument("filename", nargs='+', help="csv filename from moodle")

    db = sqlite3.connect("students.db")
    cur = db.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS studentid (id integer NOT NULL PRIMARY KEY, email varchar(20) NOT NULL UNIQUE)')
    db.commit()

    args = parser.parse_args()
    for f in args.filename:
        handle_file(db, f)

if __name__ == "__main__":
    main()
