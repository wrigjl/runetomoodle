
'''
Convert a Runestone CSV file to something pleasing to Moodle
'''

import csv
import copy
import argparse

# Don't need these fields and having "E-mail" come first
# makes this easier
fields_to_delete = ['FName', 'LName', 'UName', 'Practice']

# No grade markers
nograde_markers = ['Not Started', 'Finished']

skip_users = set()

def load_skip_users(su):
    with open('skip_users.txt') as f:
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

    return row
    

def main():
    load_skip_users(skip_users)

    parser = argparse.ArgumentParser(description='runetomoodle')
    parser.add_argument('-i', '--input', help="input csvfile", default="input.csv")
    parser.add_argument('-o', '--output', help="output csv file", default="output.csv")
    args = parser.parse_args()

    with open(args.input) as infile, \
        open(args.output, 'w', newline='') as outfile:
        reader = csv.DictReader(infile)

        fieldnames = copy.deepcopy(reader.fieldnames)
        for name in fields_to_delete:
            if name in fieldnames:
                fieldnames.remove(name)

        writer = csv.DictWriter(outfile, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            if row['E-mail'] == '':
                continue

            row = fix_row(row)
            if row is None:
                continue

            writer.writerow(fix_row(row))


if __name__ == "__main__":
    main()
