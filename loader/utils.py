import datetime
import logging
import markupsafe

logging.basicConfig(filename='wdl-error.log', encoding='utf-8', level=logging.ERROR)


def catch_err(e, proc=None):
    """General function for error processing."""

    dt = datetime.datetime.now()
    the_log = logging.getLogger('wdl-error')
    try:
        the_message = str(e.args)
        the_log.error(str(dt) + ": " + the_message + ", " + proc)

        return "Error: " + markupsafe.escape(the_message)
    except Exception as internal_e:
        the_log.error(str(dt) + ": " + str(internal_e.args) + ", " + proc)
        return "There was an error while handling an application exception. Contact your administrator."
