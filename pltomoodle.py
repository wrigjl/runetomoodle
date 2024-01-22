
'''
Convert a PrairieLearn CSV file to something pleasing to Moodle
'''

import csv
import copy
import argparse
import sqlite3
import re
from xml.dom import minidom

# Don't need these fields and having "E-mail" come first
# makes this easier
fields_to_delete = ['UID', 'Name', 'Role', 'UIN']

skip_users = set()

db = sqlite3.connect('students.db')

def load_skip_users(su):
    """When students drop, we want to skip them (less noise on import)"""
    with open('skip_users.csv', encoding='UTF-8') as f:
        for line in f:
            line = line.strip()
            if len(line) > 0:
                su.add(line)


def fix_row(row):
    '''Fix up one PL gradebook row: ignore staff, and delete unnecessary fields.
    '''
    if row['Role'] == 'Staff':
        return None

    if row['UID'] in skip_users:
        return None

    zeros = []
    for i in row.keys():
        if i.startswith('HW') and len(row[i]) == 0:
            zeros.append(i)
    for i in zeros:
        row[i] = '0'

    cur = db.cursor()
    cur.execute('select id from studentid where email = ?', (row['UID'], ))
    rows = cur.fetchall()
    assert len(rows) < 2
    if len(rows) == 0:
        print(f"ID unknown for {row['UID']}... skipping")
        return None
    row['id'] = rows[0][0]

    for name in fields_to_delete:
        if name in row:
            del row[name]

    return row


def create_simple_text_node(docroot, parent, name, text):
    """create <name>text</name> and append it as a child to 'parent'"""

    n = docroot.createElement(name)
    parent.appendChild(n)
    t = docroot.createTextNode(text)
    n.appendChild(t)


def handle_row(docroot, results, row):
    """handle one row of data"""
    for field, value in row.items():
        if field in ('E-mail', 'id'):
            continue
        m = re.match(r'''^HW([0-9]+)$''', field)
        if m is None:
            print(f"skipping field {field}:{value}")
            continue

        if len(value) == 0:
            continue

        assignment = m.group(1)
        while assignment.startswith("0"):
            assignment = assignment[1:]

        result = docroot.createElement('result')
        results.appendChild(result)

        create_simple_text_node(docroot, result,
                                'assignment', f"Quiz{assignment}")

        create_simple_text_node(docroot, result,
                                'student', f"{row['id']}")

        create_simple_text_node(docroot, result,
                                'score', f"{value}")


def main():
    """Let's do this..."""
    load_skip_users(skip_users)

    parser = argparse.ArgumentParser(description='runetomoodle')
    parser.add_argument('-i', '--input', help="input csvfile", default="pl-input.csv")
    parser.add_argument('-o', '--output', help="output xml file", default="pl-output.xml")
    args = parser.parse_args()

    with open(args.input, encoding='UTF-8') as infile, \
        open(args.output, 'w', encoding='UTF-8') as outfile:
        reader = csv.DictReader(infile)

        fieldnames = copy.deepcopy(reader.fieldnames)
        for name in fields_to_delete:
            if name in fieldnames:
                fieldnames.remove(name)

        root = minidom.Document()
        results = root.createElement('results')
        root.appendChild(results)

        for row in reader:
            row = fix_row(row)
            if row:
                handle_row(root, results, row)

        outfile.write(root.toprettyxml(indent='    '))


if __name__ == "__main__":
    main()