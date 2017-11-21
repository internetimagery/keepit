# Save scene
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import os.path
import time

def kill(id_):
    """ Kill script job """
    cmds.file(modified=False)
    if cmds.scriptJob(ex=id_):
        cmds.scriptJob(kill=id_)

def save():
    """ Run maya's built in save """
    if cmds.file(q=True, sn=True):
        mel.eval("SaveScene")
    else:
        mel.eval("SaveSceneAs") # Use manually in case it's overriden
    # mel.eval("checkForUnknownNodes(); FileMenu_SaveItem") # Perform save, using mayas built in save

def save_and_call(callback):
    """ Save scene! """
    def validate():
        """ Validate scene was saved """
        path = cmds.file(q=True, sn=True)
        if path and os.path.isfile(path):
            if os.path.getmtime(path) > time.time() - 3: # tolerance
                callback(path)
    cmds.scriptJob(e=('idle', validate), ro=True)
    save()

def test():
    """ Quick test """
    def say():
        print("SAVE CALLBACK FIRED!!")
    save_and_call(say)
