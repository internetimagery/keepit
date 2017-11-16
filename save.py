# Save scene
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel

def kill(id_):
    """ Kill script job """
    if cmds.scriptJob(ex=id_):
        cmds.scriptJob(kill=id_)

def Save(callback, debug=False):
    """ Save scene! """
    job = cmds.scriptJob(e=('SceneSaved', callback), ro=True)
    cmds.scriptJob(e=('idle', lambda: kill(job)), ro=True)
    try:
        mel.eval("SaveScene") # Perform save, using mayas built in save
        # mel.eval("checkForUnknownNodes(); FileMenu_SaveItem") # Perform save, using mayas built in save
    except Exception as err:
        kill(job)
        raise err

def test():
    """ Quick test """
    def say():
        print("SAVE CALLBACK FIRED!!")
    Save(say)
