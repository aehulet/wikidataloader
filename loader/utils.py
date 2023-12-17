import datetime
import logging
import markupsafe


def catch_err(e, proc=None):
    """General function for error processing."""
    # generic handler for error messages and logging

    dt = datetime.datetime.now()
    the_log = logging.getLogger(__name__)
    try:
        the_message = str(e.args)
        the_log.error(str(dt) + ": " + the_message + ", " + proc)

        return "Error: " + markupsafe.escape(the_message)
    except Exception as internal_e:
        the_log.error(str(dt) + ": " + str(internal_e.args) + ", " + proc)
        return "There was an error while handling an application exception. Contact your administrator."
