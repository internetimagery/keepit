# Simple save and archive functionality
from __future__ import print_function
import functools
import archive
import popup
import view
import save

def keep():
    """ Perform an archive save! """
    # Ask for a message. If no message, save as normal without archive.
    note = popup.Prompt()
    if note:
        # Perform archive
        sup = popup.Startup(note)
        with sup:
            save.save_and_call(functools.partial(archive.archive, note))
    else:
        # Save normally. Thank you, come again!
        save.save()

def look():
    """ Look at what we have """
    view.Window()

def test1():
    """ test message """
    print(build_message("TEST SUCCESS!"))
