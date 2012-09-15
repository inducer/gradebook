from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Float, Unicode, Integer, DateTime, Boolean
from sqlalchemy.orm import relationship

from camelot.admin.entity_admin import EntityAdmin
from camelot.core.orm import Entity
from camelot.view.controls import delegates
from camelot.view.forms import Form, TabForm, WidgetOnlyForm
import camelot.types

import datetime

def assignment_choices(entity_instance):
    return [
    ((None),('')),
    (('homework'),('Homework')),
    (('midterm'),('Midterm')),
    (('quiz'),('Quiz')),
    (('final'),('Final')),
    (('project'),('Project')),
    ]

def contact_kind_choices(entity_instance):
    return [
    ((None),('')),
    (('email'),('Email')),
    (('cell'),('Cell phone')),
    (('phone'),('Phone')),
    ]

def process_state_choices(entity_instance):
    return [
    ((None),('')),
    (('completed'),('Completed')),
    (('started'),('Started')),
    (('blocked'),('Blocked')),
    ]


class School(Entity):
    __tablename__ = 'school'

    name = Column(Unicode(60))

    class Admin(EntityAdmin):
        list_display = ["name"]

    def __unicode__(self):
        return self.name or "<unnamed school>"

class Course(Entity):
    __tablename__ = 'course'

    name = Column(Unicode(60))
    school_id = Column(Integer, ForeignKey('school.id'))
    school = relationship("School")

    year = Column(Integer)
    year_part = Column(Integer)

    class Admin(EntityAdmin):
        list_display = ["name", "year", "year_part", "school"]

    def __unicode__(self):
        return u"%s %s/%s" % (self.name, self.year_part, self.year)

class GradeFromStudentAdmin(EntityAdmin):
    list_display = ["assignment", "points", "due", "completed", "remark"]

class ProcessStateChangeFromStudentAdmin(EntityAdmin):
    list_display = ["process", "remark", "when"]

class Student(Entity):
    __tablename__ = 'student'

    first_name = Column(Unicode(1024))
    last_name = Column(Unicode(1024), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'),
            nullable=False)
    course = relationship("Course")
    identifier = Column(Unicode(60))
    contacts = relationship("StudentContactInfo")
    grades = relationship("AssignmentGrade")
    processes = relationship("ProcessStateChange")
    is_active = Column(Boolean, default=True,
            nullable=False)

    class Admin(EntityAdmin):
        list_display = ["last_name", "first_name", "identifier", "course"]
        field_attributes = dict(
                contacts=dict(create_inline=True),
                grades=dict(
                    create_inline=True,
                    admin=GradeFromStudentAdmin,
                    ),
                processes=dict(
                    create_inline=True,
                    admin=ProcessStateChangeFromStudentAdmin,
                    ),
                )

        form_display = TabForm([
            ('Student', Form([
                "is_active",
                "first_name",
                "last_name",
                "identifier", 
                "course",
                "contacts"])),
            ('Grades', WidgetOnlyForm('grades')),
            ('Processes', WidgetOnlyForm('processes')),
            ])

    def __unicode__(self):
        return u"%s, %s (%s)" % (self.last_name, self.first_name, self.course)


class StudentContactInfo(Entity):
    __tablename__ = 'contact_info'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student")
    kind = Column(Unicode(60), nullable=False)
    value = Column(Unicode(1024), nullable=False)

    class Admin(EntityAdmin):
        list_display = ["kind", "value"]
        field_attributes = dict(
            kind=dict(
                choices=contact_kind_choices
                )
            )


# {{{ assignments

class GradeFromAssignmentAdmin(EntityAdmin):
    list_display = ["student", "points", "due", "completed", "remark"]

class Assignment(Entity):
    __tablename__ = 'assignment'

    name = Column(Unicode(1024))
    kind = Column(Unicode(60))
    number = Column(Integer)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    course = relationship("Course")
    possible_points = Column(Float)
    due = Column(DateTime)
    grades = relationship("AssignmentGrade")

    class Admin(EntityAdmin):
        list_display = ["course", "kind", "number", "possible_points", "due"]
        field_attributes = dict(
            kind=dict(choices=assignment_choices),
            grades=dict(
                create_inline=True,
                admin=GradeFromAssignmentAdmin,
                ),
            )

        form_display = TabForm([
            ('Assignment', Form(list_display)),
            ('Grades', WidgetOnlyForm('grades')),
            ])

    def __unicode__(self):
        kind_dict = dict(assignment_choices(None))
        kind = self.kind
        if kind in kind_dict:
            kind = kind_dict[kind]
        name = u"%s %s" % (kind, self.number)

        if self.name:
            name = self.name

        if self.course:
            name += u" (%s)" % self.course

        return name


class AssignmentGrade(Entity):
    __tablename__ = 'grade'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student")

    assignment_id = Column(Integer, ForeignKey('assignment.id'))
    assignment = relationship("Assignment")

    due = Column(DateTime)
    completion_time = Column(DateTime, default=datetime.datetime.now)

    points = Column(Float)
    remark = Column(Unicode(1024))

# }}}

# {{{ processes

class Process(Entity):
    __tablename__ = 'process'

    name = Column(Unicode(1024))
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship("Course")
    state_changes = relationship("ProcessStateChange")

    class Admin(EntityAdmin):
        verbose_name_plural = "Processes"

        list_display = ["name", "course"]

    def __unicode__(self):
        result = self.name or "<unnamed process>"

        if self.course:
            result += u" (%s)" % self.course

        return result


class ProcessStateChange(Entity):
    __tablename__ = 'process_state_change'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student")

    process_id = Column(Integer, ForeignKey('process.id'))
    process = relationship("Process")

    when = Column(DateTime,
            default=datetime.datetime.now)

    remark = Column(Unicode(1024))

# }}}
