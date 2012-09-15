from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Float, Unicode, Integer, DateTime
from sqlalchemy.orm import relationship

from camelot.admin.entity_admin import EntityAdmin
from camelot.core.orm import Entity
from camelot.view.controls import delegates
from camelot.view.forms import Form, TabForm, WidgetOnlyForm
import camelot.types

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
        return "%s %d/%d" % (self.name, self.year_part, self.year)

class Student(Entity):
    __tablename__ = 'student'

    first_name = Column(Unicode(1024))
    last_name = Column(Unicode(1024))
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship("Course")
    identifier = Column(Unicode(60))
    contacts = relationship("StudentContactInfo")
    grades = relationship("AssignmentGrade")

    class Admin(EntityAdmin):
        list_display = ["last_name", "first_name", "identifier", "course"]
        form_display = list_display + ["contacts"]
        field_attributes = dict(
                contacts=dict(create_inline=True),
                grades=dict(create_inline=True),
                )

        form_display = TabForm([
          ('Student', Form(list_display + ["contacts"])),
          ('Grades', WidgetOnlyForm('grades')),
        ])

class StudentContactInfo(Entity):
    __tablename__ = 'contact_info'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student")
    kind = Column(Unicode(60))
    value = Column(Unicode(1024))

    class Admin(EntityAdmin):
        list_display = ["kind", "value"]
        field_attributes = dict(
            kind=dict(
                choices=contact_kind_choices
                )
            )


class Assignment(Entity):
    __tablename__ = 'assignment'

    name = Column(Unicode(1024))
    kind = Column(Unicode(60))
    number = Column(Integer)
    course_id = Column(Integer, ForeignKey('course.id'))
    course = relationship("Course")
    possible_points = Column(Float)
    due = Column(DateTime)

    class Admin(EntityAdmin):
        list_display = ["name", "kind", "identifier", "course"]
        field_attributes = dict(
            kind=dict(
                choices=assignment_choices
                )
            )

    def __unicode__(self):
        name = "%u %u" % (self.kind, self.number)
        if self.name:
            name += " (%u)" % self.name
        return name


class AssignmentGrade(Entity):
    __tablename__ = 'grade'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student")

    assignment_id = Column(Integer, ForeignKey('assignment.id'))
    assignment = relationship("Assignment")

    due = Column(DateTime)
    completed = Column(DateTime)

    points = Column(Float)
    remark = Column(Unicode(1024))
