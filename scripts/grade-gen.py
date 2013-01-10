#! /usr/bin/env python

from __future__ import division
from optparse import OptionParser
import numpy as np


parser = OptionParser(usage="usage: %prog [options] COURSE_ID")
parser.add_option("-c", "--credit-only",
                  action="store_true")
parser.add_option("-d", "--print-detail",
                  action="store_true")

(options, args) = parser.parse_args()

if len(args) < 1:
    parser.print_usage()
    import sys
    sys.exit(1)

course_id, = args

# {{{ boilerplate

from camelot.core.orm import Session
import os, sys
sys.path.append(os.environ["GRADEBOOK_ROOT"])
import main

from camelot.core.conf import settings
settings.setup_model()

# }}}

session = Session()

from gradebook.model import (Student,
        Assignment, AssignmentStateChange as ASC)

assignments = list(session.query(Assignment)
        .filter(Assignment.course_id == course_id)
        .filter(Assignment.kind == "homework")
        )

proj_pres, = list(session.query(Assignment)
        .filter(Assignment.course_id == course_id)
        .filter(Assignment.kind == "project")
        .filter(Assignment.number == 0)
        )

proj_report, = list(session.query(Assignment)
        .filter(Assignment.course_id == course_id)
        .filter(Assignment.kind == "project")
        .filter(Assignment.number == 1)
        )

qry = session.query(Student)

if options.credit_only is not None:
    qry = qry.filter(Student.kind == "credit")

qry = qry.order_by(Student.last_name)

def drop_nones(values):
    return [i for i in values if i is not None]
def drop_exempts(values):
    return [i for i in values if i != "exempt"]

LETTER_GRADES = ["A", "A-", "B+", "B", "B-", "C+", "C", "C-", "D+", "D"]
distances = [
        # A range
        0, 5,
        # B range
        4, 9, 6,
        # C range
        9, 9, 5,
        # D range
        5, 9]
GRADE_CUTOFFS = 92-np.cumsum(distances)
print "grade cutoffs:", zip(LETTER_GRADES, GRADE_CUTOFFS)


class GradeStateMachine:
    def __init__(self):
        self.graded_sc = None
        self.unavailable_sc = None
        self.exempt_sc = None

    def consume_state_change(self, student, sc):
        if sc.new_state == "graded":
            self.graded_sc = sc
        elif sc.new_state == "unavailable":
            self.unavailable_sc = sc
        elif sc.new_state == "do-over":
            self.graded_sc = None
            self.unavailable_sc = None
            self.exempt_sc = None
        elif sc.new_state == "exempt":
            self.exempt_sc = sc
        elif sc.new_state in ["grading-started", "retrieved",
                "retrieved", "report-sent", "extension"]:
            pass
        else:
            raise RuntimeError("invalid assignment state '%s' for '%s'"
                    % (sc.new_state, student.user_name))

    def consume_state_changes(self, student, iterable):
        for sc in iterable:
            self.consume_state_change(student, sc)
        return self

for student in qry:
    # {{{ homework

    hws = [None]*6
    for assmt in assignments:
        state_changes = list(session.query(ASC)
                .filter(ASC.assignment == assmt)
                .filter(ASC.student == student)
                .order_by(ASC.timestamp))

        gsm = GradeStateMachine().consume_state_changes(student, state_changes)

        if gsm.unavailable_sc:
            hws[assmt.number-1] = 0
        if gsm.graded_sc:
            hws[assmt.number-1] = gsm.graded_sc.points/assmt.possible_points
        if gsm.exempt_sc:
            hws[assmt.number-1] = "exempt"

    hws = drop_exempts(hws)

    # }}}

    # {{{ presentation

    state_changes = list(session.query(ASC)
            .filter(ASC.assignment == proj_pres)
            .filter(ASC.student == student)
            .order_by(ASC.timestamp))
    gsm = GradeStateMachine().consume_state_changes(student, state_changes)

    pres_grade = None
    if gsm.unavailable_sc:
        pres_grade = 0
    if gsm.graded_sc:
        pres_grade = gsm.graded_sc.points/proj_pres.possible_points

    # }}}

    # {{{ report

    state_changes = list(session.query(ASC)
            .filter(ASC.assignment == proj_report)
            .filter(ASC.student == student)
            .order_by(ASC.timestamp))
    gsm = GradeStateMachine().consume_state_changes(student, state_changes)

    report_grade = None
    if gsm.unavailable_sc:
        report_grade = 0
    if gsm.graded_sc:
        report_grade = gsm.graded_sc.points/proj_pres.possible_points

    # }}}

    # {{{ error check

    issues = []
    if pres_grade is None:
        issues.append("no presentation")
    if report_grade is None:
        issues.append("no report")
    if any(hw is None for hw in hws):
        issues.append("not all hw done")

    if issues:
        print "%-10s %-40s: /!\ %s" % (
                student.user_name,
                "%s, %s" % (student.last_name, student.first_name),
                ", ".join(issues))
        continue

    del issues

    # }}}

    grade = 60 * sum(hws)/len(hws) + 20 * pres_grade + 20 * report_grade
    rounded_grade = round(grade)


    letter = "F"
    for potential_letter, cutoff in zip(LETTER_GRADES, GRADE_CUTOFFS):
        if cutoff > rounded_grade >= cutoff-2:
            print "Close call: %s -> %s (cutoff: %s)" % (
                    student.user_name, potential_letter, cutoff)
        if rounded_grade >= cutoff:
            letter = potential_letter
            break

    print "%-10s %-40s: %.0f points -> %s (out of %d assignments)" % (
            student.user_name,
            "%s, %s" % (student.last_name, student.first_name),
            rounded_grade, letter, len(hws))
    if options.print_detail:
        print "    HW:", ", ".join("%.1f" % (100*hw) for hw in hws)
        print "    Presentation: %.1f" % (100*pres_grade)
        print "    Report: %.1f" % (100*report_grade)
