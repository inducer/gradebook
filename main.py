import logging
from camelot.core.conf import settings, SimpleSettings

logging.basicConfig( level = logging.ERROR )
logger = logging.getLogger( 'main' )

# begin custom settings
class MySettings( SimpleSettings ):

    # add an ENGINE or a CAMELOT_MEDIA_ROOT method here to connect
    # to another database or change the location where files are stored

    def ENGINE( self ):
        import os
        from sqlalchemy import create_engine
        return create_engine('sqlite:///'+os.environ["GRADEBOOK_DATABASE"])

    def setup_model( self ):
        """This function will be called at application startup, it is used to
        setup the model"""
        from camelot.core.sql import metadata
        from sqlalchemy.orm import configure_mappers
        metadata.bind = self.ENGINE()
        import camelot.model.authentication
        import camelot.model.i18n
        import camelot.model.memento
        import gradebook.model
        configure_mappers()
        metadata.create_all()

my_settings = MySettings('My Company', 'Grade book')
settings.append(my_settings)
# end custom settings

def start_application():
    from camelot.view.main import main
    from gradebook.application_admin import MyApplicationAdmin
    main(MyApplicationAdmin())

if __name__ == '__main__':
    start_application()
