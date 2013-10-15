# {{{ boilerplate

from camelot.core.orm import Session
import os
import sys
sys.path.append(os.environ["GRADEBOOK_ROOT"])
import main  # noqa

from camelot.core.conf import settings
settings.setup_model()

# }}}

session = Session()

from gradebook.model import (Course,
        Student, StudentContactInfo)
course, = session.query(Course).all()

import csv
with open('class-list.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile, delimiter=";")
    for row in reader:
        print row
        ln = row["Last"]
        fn = row["First"]
        student = Student(first_name=unicode(fn.strip()),
                last_name=unicode(ln.strip()),
                user_name=unicode(row["NetID"]),
                course=course)

        session.add(student)
        session.add(StudentContactInfo(
            student=student,
            kind="email",
            value=row["NetID"]+"@illinois.edu",
            ))

        print unicode(student)

#from gradebook.model import Course
#for name in session.query(Course.name):
    #print name

session.flush()
