This is my workflow for managing grades coming from Runestone Academy
and PrairieLean to Moodle for Idaho State's CS1181 course.

# For Runestone
## Beginning of the semester

### On Runestone

- Configure the assignments in Runestone to match the expression: `Chapter ([0-9]+) - .*`

### Moodle

- Make sure assignments have an ID of the form `Reading[0-9]+` 

### Local

- delete all of the email addresses from `skip_users.csv`.

## Weekly-ish

### On Runestone

Go through each assignment that is currently due and:

  - Hide grades
  - autograde
  - Release grades

Download the current gradebook into this directory and call it `input.csv`.

### On Moodle

Download a current grade list CSV. It doesn't actually need any assignment grades.
We're just going to use it to extract the student email address and ID.  Call the file
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

Note: `runetomoodle.py` is present here as well. It is less sophisticated and
produces `output.csv` from `input.csv`. This output CSV can be used with CSV
grade imports, but I find this process tedious.

# For PrairieLearn

## Beginning of semester

Create empty `skip_users.csv`.

Create `students.db` using `students.py` and a current class roster (described above).

Ensure all quiz assignments have an ID of the form: `HW[0-9]`. There's ID's are found under "Common Module Settings" in the assignment settings.

## Every week or so

Download the gradebook from prairielearn. Open the
CSV file in Excel and delete the columns corresponding
to homeworks that are not yet due. Save it as `pl-input.csv`.

Now, convert the PL csv gradebook to Moodle XML grades:

```sh
python pltomoodle.py
```

This produces a `pl-output.xml` file, which can be uploaded via Grades|Import. Import As: XML FIle.

### The long version

Prairielearn uses an email address to identify students.
Moodle uses a userID (integer). `students.py` is used to
create the mapping of email to userID.

`pltomoodle.py` uses the mapping database and the grades to produce the moodle XML file. You could use the CSV file, but its a very manual process for each grade import (and error prone).
