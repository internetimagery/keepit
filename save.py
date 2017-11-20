# Save scene
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel

class Save(object):
    """ Monitor scene saving """
    def __init__(s, func):
        s.func = func
        s.note = ""
        cmds.scriptJob(e=("SceneSaved", s.save_callback))

    def save_callback(s):
        """ Triggered on scene save """
        path = cmds.file(q=True, sn=True)
        if path and s.note:
            s.func(s.note, path)
        s.note = ""

    def save(s):
        """ Run maya's built in save """
        if cmds.file(q=True, sn=True):
            mel.eval("SaveScene")
        else:
            mel.eval("SaveSceneAs") # Use manually in case it's overriden
