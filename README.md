This is my workflow for managing grades coming from Runestone Academy
to Moodle for Idaho State's CS1181 course.

# Beginning of the semester

## Runestone

- Configure the assignments in Runestone to match the expression: `Chapter ([0-9]+) - .*`

## Moodle

- Make sure assignments have an ID of the form `Reading[0-9]+`

## Local

- delete all of the email addresses from `skip_users.csv`.

# Weekly-ish

## Runestone

Go through each assignment that is currently due and:

  - Hide grades
  - uncheck "only grade work before"
  - autograde
  - Release grades

Download the current gradebook into this directory and call it `input.csv`.

## Moodle

Download a current grade list CSV. It doesn't actually need any assignment grades.
We're just going to use it to extrace the student email address and ID.  Call the file
`students.csv`.

Run the following to get the student ID/email addresses into the local database:

```bash
python students.py students.csv
```

Now, let's produce the Moodle grade XML:

```bash
python runetomoodlexml.py
```

This reads `input.csv` and produces `output.xml` which can be uploaded to Moodle.
All of the assignments and student IDs should line up and you should get no errors.
The usual failure mode is a student ID that matches a student who has dropped the
class. To skip this student in the future, put their email address in `skip_users.csv`
