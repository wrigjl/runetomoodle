
'''
Convert a Runestone CSV file to something pleasing to Moodle XML

One huge assumption here is that the assignments are named:
  ^Chapter ([0-9]+) - .*$

Also, each corresponding assignment in Moodle needs to have
a unique number.  I assume it is Reading[0-9+] (in other words,
I use the chapter title's number to generate the Moodle assignment
number).
'''

import csv
import copy
import argparse
import sqlite3
import re
from xml.dom import minidom

db = sqlite3.connect('students.db')

# Don't need these fields and having "E-mail" come first
# makes this easier
fields_to_delete = ['FName', 'LName', 'UName', 'Practice']

# No grade markers
nograde_markers = ['Not Started', 'Finished']

skip_users = set()

def load_skip_users(su):
    with open('skip_users.csv') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                su.add(line)

def fix_row(row):
    '''Fix up one Runestone gradebook row: delete uncessary fields,
    strip away %'s, and mark empty those fields which have no grade
    '''

    if row['E-mail'] in skip_users:
        return None

    for name in fields_to_delete:
        if name in row:
            del row[name]

    for field, value in row.items():
        # Skip the email field
        if field == 'E-mail':
            continue

        # Mark the nograde markers empty
        if value in nograde_markers:
            row[field] = ''
            continue

        # Get rid of trailing %'s in the grades
        row[field] = value.rstrip('%')

    cur = db.cursor()
    cur.execute('select id from studentid where email = ?', (row['E-mail'], ))
    rows = cur.fetchall()
    assert len(rows) < 2
    if len(rows) == 0:
        print(f"ID unknown for {row['E-mail']}... skipping")
        return None
    row['id'] = rows[0][0]

    return row


def handle_row(docroot, results, row):
    for field, value in row.items():
        if field in ('E-mail', 'id'):
            continue
        m = re.match(r'''^Chapter ([0-9]+) - .*$''', field)
        if m is None:
            print(f"skipping field {field}:{value}")
            continue

        if len(value) == 0:
            continue

        result = docroot.createElement('result')
        results.appendChild(result)

        x = docroot.createElement('assignment')
        t = docroot.createTextNode(f"Reading{m.group(1)}")
        x.appendChild(t)
        result.appendChild(x)

        x = docroot.createElement('student')
        t = docroot.createTextNode(f"{row['id']}")
        x.appendChild(t)
        result.appendChild(x)

        x = docroot.createElement('score')
        t = docroot.createTextNode(f"{value}")
        x.appendChild(t)
        result.appendChild(x)


def main():
    load_skip_users(skip_users)

    parser = argparse.ArgumentParser(description='runetomoodle')
    parser.add_argument('-i', '--input', help="input csvfile", default="input.csv")
    parser.add_argument('-o', '--output', help="output csv file", default="output.xml")
    args = parser.parse_args()

    with open(args.input) as infile, \
        open(args.output, 'w') as outfile:
        reader = csv.DictReader(infile)

        fieldnames = copy.deepcopy(reader.fieldnames)
        for name in fields_to_delete:
            if name in fieldnames:
                fieldnames.remove(name)

        root = minidom.Document()
        results = root.createElement('results')
        root.appendChild(results)

        for row in reader:
            if row['E-mail'] == '':
                continue

            row = fix_row(row)
            if row is None:
                continue

            handle_row(root, results, row)

        outfile.write(root.toprettyxml(indent='    '))


if __name__ == "__main__":
    main()
