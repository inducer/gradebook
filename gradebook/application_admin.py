from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section
from camelot.core.utils import ugettext_lazy as _
import model as m

class MyApplicationAdmin(ApplicationAdmin):
    name = 'Grade book'
    application_url = 'http://tiker.net'
    help_url = 'http://tiker.net'
    author = 'My Company'
    domain = 'tiker.net'

    def get_sections(self):
        from camelot.model.memento import Memento
        from camelot.model.i18n import Translation
        return [ Section( _('Grade book'),
                          self,
                          Icon('tango/22x22/apps/system-users.png'),
                          items = [m.School, m.Course, m.Assignment, 
                              m.Process, m.Student]),
                 Section( _('Configuration'),
                          self,
                          Icon('tango/22x22/categories/preferences-system.png'),
                          items = [Memento, Translation] )
                ]

