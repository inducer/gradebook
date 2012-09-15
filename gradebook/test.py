
#
# Default unittests for a camelot application.  These unittests will create
# screenshots of all the views in the application.  Run them with this command :
#
# python -m nose.core -v -s gradebook/test.py
#

import os

from camelot.test import EntityViewsTest

# screenshots will be put in this directory
static_images_path = os.path.join( os.path.dirname( __file__ ), 'images' )

class MyApplicationViewsTest( EntityViewsTest ):

    images_path = static_images_path
    