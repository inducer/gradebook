import logging
from camelot.core.conf import settings, SimpleSettings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('main')

# begin custom settings
NO_CONF_ACK = [False]
class MySettings(SimpleSettings):
    def ENGINE( self ):
        import os
        from sqlalchemy import create_engine
        user_pw = os.environ.get("GRADEBOOK_USER_PW")
        if user_pw is None:
            db_file_name = os.environ.get("GRADEBOOK_DATABASE")
            if db_file_name is None:
                db_file_name = "gradebook-default.sqlite"
                if not NO_CONF_ACK[0]:
                    print "-"*75
                    print "No configuration detected"
                    print "-"*75
                    print "Neither GRADEBOOK_USER_PW nor GRADEBOOK_DATABASE was found"
                    print "as an environment variable. I'll run with a default"
                    print "database of '%s'." % db_file_name
                    print "-"*75
                    print "Hint [Enter] if that sounds good, and Ctrl-C[Enter] if you'd like to stop."
                    raw_input()
                    NO_CONF_ACK[0] = True

            return create_engine('sqlite:///'+db_file_name)
        else:
            return create_engine('mysql://%s@127.0.0.1:3307/gradebook' % user_pw)

    def setup_model( self ):
        from camelot.core.sql import metadata
        from sqlalchemy.orm import configure_mappers
        import camelot.model.authentication
        import camelot.model.i18n
        import camelot.model.memento
        import gradebook.model

        metadata.bind = self.ENGINE()
        configure_mappers()
        metadata.create_all()

        # ugh, breaks stuff
        from camelot.core.sql import update_database_from_model
        update_database_from_model()

my_settings = MySettings('My Company', 'Grade book')
settings.append(my_settings)
# end custom settings

def start_application():
    from camelot.view.main import main
    from gradebook.application_admin import MyApplicationAdmin
    main(MyApplicationAdmin())

if __name__ == '__main__':
    start_application()
