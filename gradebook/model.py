from sqlalchemy.schema import Column, ForeignKey
from sqlalchemy import Float, Unicode, Integer, Date, DateTime, Boolean
from sqlalchemy.orm import relationship

from camelot.admin.entity_admin import EntityAdmin
from camelot.types import RichText
from camelot.core.orm import Entity
from camelot.view.forms import Form, TabForm, WidgetOnlyForm

import datetime

def student_kind_choices(entity_instance):
    return [
    ((None),('')),
    (('credit'),('Credit')),
    (('audit'),('Audit')),
    ]
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

def assignment_state_change_choices(entity_instance):
    return [
    ((None),('')),
    (('submitted'),('Submitted')),
    (('graded'),('Graded')),
    (('rejected'),('Rejected')),
    (('extension'),('Extension')),
    ]

class School(Entity):
    __tablename__ = 'school'

    name = Column(Unicode(60))

    class Admin(EntityAdmin):
        list_display = ["name"]

        field_attributes = dict(
                name=dict(minimal_column_width=60)
                )

    def __unicode__(self):
        return self.name or "<unnamed school>"

class Course(Entity):
    __tablename__ = 'course'

    name = Column(Unicode(60), nullable=False)
    school_id = Column(Integer, ForeignKey('school.id'), nullable=False)
    school = relationship("School")

    start_date = Column(Date, nullable=False)

    class Admin(EntityAdmin):
        list_display = ["name", "start_date", "school"]

        field_attributes = dict(
                name=dict(minimal_column_width=50),
                )

    def __unicode__(self):
        return u"%s %s/%s" % (self.name, self.start_date.month,
                self.start_date.year)

class AssignmentFromStudentAdmin(EntityAdmin):
    list_display = ["assignment", "new_state", "due_date", "points", "timestamp", "remark"]

    field_attributes = dict(
            new_state=dict(choices=assignment_state_change_choices),
            points=dict(calculator=False))

class ProcessStateChangeFromStudentAdmin(EntityAdmin):
    list_display = ["process", "new_state", "remark", "timestamp"]

    field_attributes = dict(
            new_state=dict(choices=process_state_choices))


class Student(Entity):
    __tablename__ = 'student'

    is_active = Column(Boolean, default=True,
            nullable=False)
    kind = Column(Unicode(60))
    student = Column(Unicode(1024))
    first_name = Column(Unicode(1024))
    last_name = Column(Unicode(1024), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'),
            nullable=False)
    course = relationship("Course")
    identifier = Column(Unicode(60))
    user_name = Column(Unicode(60))
    notes = Column(RichText())

    class Admin(EntityAdmin):
        list_display = ["last_name", "first_name", "identifier", "user_name", "course"]
        field_attributes = dict(
                kind=dict(choices=student_kind_choices),
                contacts=dict(create_inline=True),
                assignments=dict(
                    create_inline=True,
                    admin=AssignmentFromStudentAdmin,
                    ),
                processes=dict(
                    create_inline=True,
                    admin=ProcessStateChangeFromStudentAdmin,
                    ),
                )

        form_display = TabForm([
            ('Student', Form([
                "is_active",
                "kind",
                "first_name",
                "last_name",
                "user_name", 
                "identifier", 
                "course",
                "notes",
                "contacts"])),
            ('Assignments', WidgetOnlyForm('assignments')),
            ('Processes', WidgetOnlyForm('processes')),
            ])

    def __unicode__(self):
        return u"%s, %s (%s)" % (self.last_name, self.first_name, self.course)


class StudentContactInfo(Entity):
    __tablename__ = 'contact_info'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", backref="contacts")
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

class StateChangeFromAssignmentAdmin(EntityAdmin):
    list_display = ["student", "new_state", "points", "due_date", "remark", "timestamp"]

    field_attributes = AssignmentFromStudentAdmin.field_attributes

class Assignment(Entity):
    __tablename__ = 'assignment'

    name = Column(Unicode(1024))
    kind = Column(Unicode(60))
    number = Column(Integer)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    course = relationship("Course")
    possible_points = Column(Float)
    due = Column(Date)

    class Admin(EntityAdmin):
        list_display = ["course", "kind", "number", "possible_points", "due"]
        form_display = ["course", "kind", "number", "name", "possible_points", "due"]
        field_attributes = dict(
            kind=dict(choices=assignment_choices),
            state_changes=dict(
                create_inline=True,
                admin=StateChangeFromAssignmentAdmin,
                ),
            name=dict(
                tooltip="Alternative description to kind/number",
                )
            )

        form_display = TabForm([
            ('Assignment', Form(list_display)),
            ('State Changes', WidgetOnlyForm('state_changes')),
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


class AssignmentStateChange(Entity):
    __tablename__ = 'assignment_state_change'

    student_id = Column(Integer, ForeignKey('student.id'),
            nullable=False)
    student = relationship("Student", backref="assignments")

    assignment_id = Column(Integer, ForeignKey('assignment.id'),
            nullable=False)
    assignment = relationship("Assignment", backref="state_changes")

    new_state = Column(Unicode(60))
    due_date = Column(Date)
    timestamp = Column(DateTime, default=datetime.datetime.now)
    points = Column(Float)
    remark = Column(Unicode(1024))

# }}}

# {{{ processes

class Process(Entity):
    __tablename__ = 'process'

    name = Column(Unicode(1024), nullable=False)
    course_id = Column(Integer, ForeignKey('course.id'), nullable=False)
    course = relationship("Course")

    class Admin(EntityAdmin):
        verbose_name_plural = "Processes"

        list_display = ["name", "course"]

        field_attributes = dict(
                name=dict(minimal_column_width=60)
                )

    def __unicode__(self):
        result = self.name or "<unnamed process>"

        if self.course:
            result += u" (%s)" % self.course

        return result


class ProcessStateChange(Entity):
    __tablename__ = 'process_state_change'

    student_id = Column(Integer, ForeignKey('student.id'))
    student = relationship("Student", backref="processes")

    process_id = Column(Integer, ForeignKey('process.id'))
    process = relationship("Process", backref="state_changes")

    timestamp = Column(DateTime,
            default=datetime.datetime.now,
            nullable=False)

    new_state = Column(Unicode(1024), nullable=False)

    remark = Column(Unicode(1024))

# }}}
