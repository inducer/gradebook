# {{{ boilerplate

from camelot.core.orm import Session
import os, sys
sys.path.append(os.environ["GRADEBOOK_ROOT"])
import main

from camelot.core.conf import settings
settings.setup_model()

# }}}

session = Session()

from gradebook.model import Course
for name in session.query(Course.name):
    print name

session.flush()

