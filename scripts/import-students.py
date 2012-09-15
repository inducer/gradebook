# {{{ boilerplate

from camelot.core.orm import Session
import os, sys
sys.path.append(os.environ["GRADEBOOK_ROOT"])
import main

from camelot.core.conf import settings
settings.setup_model()

# }}}

session = Session()

from gradebook.model import (Course,
        Student, Process, ProcessStateChange,
        StudentContactInfo)
course, = session.query(Course).all()

ml_process, = (session.query(Process)
        .filter(Process.course == course)
        .filter(Process.name.like("Mail%")))
hpc_process, = (session.query(Process)
        .filter(Process.course == course)
        .filter(Process.name.like("HPC%")))

import csv
with open('class-list.csv', 'rb') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        ln, fn = row["Name"].split(",")
        student = Student(first_name=unicode(fn.strip()),
                last_name=unicode(ln.strip()),
                user_name=unicode(row["NetID"]),
                course=course)

        session.add(student)
        session.add(StudentContactInfo(
            student=student,
            kind="email",
            value=row["Email"],
            ))

        if row["Email2"]:
            session.add(StudentContactInfo(
                student=student,
                kind="email",
                value=row["Email2"],
                ))

        if row["HPC"]:
            session.add(ProcessStateChange(
                student=student,
                process=hpc_process,
                new_state=unicode("started"),
                ))

        session.add(ProcessStateChange(
            student=student,
            process=ml_process,
            new_state=unicode("completed"),
            ))

        print unicode(student)

#from gradebook.model import Course
#for name in session.query(Course.name):
    #print name

session.flush()

