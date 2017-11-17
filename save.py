# Save scene
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel

def kill(id_):
    """ Kill script job """
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
    job = cmds.scriptJob(e=('SceneSaved', lambda: callback(cmds.file(q=True, sn=True))), ro=True)
    cmds.scriptJob(e=('idle', lambda: kill(job)), ro=True)
    try:
        save()
    except Exception as err:
        kill(job)
        raise err

def test():
    """ Quick test """
    def say():
        print("SAVE CALLBACK FIRED!!")
    save_and_call(say)
