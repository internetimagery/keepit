# Pop up a message when maya scene loads
import maya.cmds as cmds

class Startup(object):
    """
    Create a one time startup popup
    """
    def __init__(s, message):
        s.uid = "POPUP_%s" % int((time.time() * 100))  # Generate unique ID
        s.message = message
        # TODO: Stringify this message also!

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
