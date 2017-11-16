# Pop up a message when maya scene loads
from __future__ import print_function
import maya.cmds as cmds
import os.path
import random
import base64
import time
import os

IMG_ROOT = os.path.join(os.path.dirname(__file__), "images")
IMAGES = [(os.path.join(IMG_ROOT, a), os.path.splitext(a)[1][1:]) for a in os.listdir(IMG_ROOT) if a.endswith("png")]

def embedImage():
    """
    Grab a random image and embed it in the scene.
    """
    if IMAGES:
        img_path, img_ext = random.choice(IMAGES)
        with open(img_path, "rb") as f:
            image = "<img src=\\\"data:image/%s;base64,%s\\\">" % (img_ext, base64.b64encode(f.read()))
        return "cmds.text(hl=True, l=\"%s\", h=100, w=100)" % image
    else:
        return "cmds.iconTextStaticLabel(image=\"envChrome.svg\", h=100, w=100)  # file.svg looks nice too..."

class Startup(object):
    """
    Create a one time startup popup
    """
    def __init__(s, message):
        s.uid = "POPUP_%s" % int((time.time() * 100))  # Generate unique ID
        s.message = message
        # TODO: Stringify this message also?

    def stringify(s, data):
        return "python(\"%s\");" % data.replace("\\", "\\\\").replace("\"", "\\\"").replace("\n", r"\n")

    def __enter__(s):
        s.job = cmds.scriptNode(n=s.uid, st=2, bs="")
        s.code = """
import maya.cmds as cmds
uid = "%(uid)s"
job = "%(job)s"
if cmds.fileInfo(uid, q=True) == ["ok"]:
    def makepopup():
        p = cmds.setParent(q=True)
        cmds.rowLayout(nc=2, ad2=2, p=p)
        cmds.columnLayout()
        %(image)s
        cmds.setParent("..")
        cmds.columnLayout(adj=True)
        cmds.text(al="left", hl=True, l=\"\"\"%(message)s\"\"\", h=70)
        cmds.button(l="Thanks", c="cmds.layoutDialog(dismiss=\\"gone\\")", h=30)
        cmds.setParent("..")
    cmds.layoutDialog(ui=makepopup, t="Welcome Back")
if cmds.objExists(job):
    cmds.delete(job)
cmds.fileInfo(rm=uid)
""" % {"uid": s.uid, "job": s.job, "image": embedImage(), "message": s.message}
        cmds.scriptNode(s.job, e=True, bs=s.stringify(s.code))
        cmds.fileInfo(s.uid, "ok")
        return s

    def __exit__(s, err, val, trace):
        """
        Remove those things from the scene
        """
        cmds.fileInfo(rm=s.uid)
        if cmds.objExists(s.job):
            cmds.delete(s.job)

def Prompt():
    """ Prompt for response """
    save = "Save"
    result = cmds.promptDialog(
		title='Scene is saving...',
		message='Archive note:',
		button=[save])
    if result == save:
    	return cmds.promptDialog(query=True, text=True).strip()
    return ""

def test1():
    """ test prompt """
    print(Prompt())

def test2():
    """ test image """
    print(embedImage())

def test3():
    """ Test startup popup """
    import tempfile
    import shutil
    root = tempfile.mkdtemp()
    try:
        cmds.file(new=True, force=True)
        sup = Startup("Hi there. \"Test\" worked!")
        place = os.path.join(root, "test.ma")
        with sup:
            cmds.file(rename=place)
            cmds.file(save=True, type="mayaAscii")
        cmds.file(place, open=True, force=True)
    finally:
        shutil.rmtree(root)
        assert not os.path.isdir(root)
