# Simple save and archive functionality
from __future__ import print_function
import maya.cmds as cmds
import datetime
import popup

def build_message(message):
    """ Create a nice message with relevant info """
    return """
<div>- This Scene was last saved on <em>%(time)s</em>.</div>
<div>- Completing the task: <code>%(message)s</code></div>
<div>- The file <strong>has not been modified since.</strong></div><br>
""" % {"time": datetime.datetime.today().strftime("%I:%M%p %A %d-%m-%Y"), "message": message}

def main():
    """ Perform an archive save! """
    note = popup.Prompt()
    if note:
        pass


def test1():
    """ test message """
    print(build_message("TEST SUCCESS!"))
