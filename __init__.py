# Simple save and archive functionality
from __future__ import print_function
import functools
import datetime
import archive
import popup
import save

def build_message(message):
    """ Create a nice message with relevant info """
    return """
<div>- This Scene was last saved on <em>%(time)s</em>.</div>
<div>- Completing the task: <code>%(message)s</code></div>
<div>- The file <strong>has not been modified since.</strong></div><br>
""" % {"time": datetime.datetime.today().strftime("%I:%M%p %A %d-%m-%Y"), "message": message}

def keepit(note, path):
    """ Kick off an archive """
    # TODO: Potentially add thumbnails etc
    archive.archive(note, [path])

def main():
    """ Perform an archive save! """
    # Ask for a message. If no message, save as normal without archive.
    note = popup.Prompt()
    if note:
        # Perform archive
        sup = popup.Startup(note)
        with sup:
            save.save_and_call(functools.partial(keepit, note))
    else:
        # Save normally. Thank you, come again!
        save.save()

def test1():
    """ test message """
    print(build_message("TEST SUCCESS!"))
