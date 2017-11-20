# View recent versions based on "file" archive
# TODO: This is not well structured. Should be integrated into archive directly
from __future__ import print_function
import maya.utils as utils
import maya.cmds as cmds
import threading
import datetime
import os.path
import zipfile
import base64
import os
import re

WIDTH, HEIGHT = 160, 90

class Version(object):
    def __init__(s, parent, root, version):
        """ Version! """
        s.archive = os.path.join(root, version.group(0))
        # time = datetime.datetime.fromtimestamp(int(version.group(2))* 0.001)
        note = version.group(3)

        with zipfile.ZipFile(s.archive, "r") as z:
            files = z.namelist()
            thumb = ""
            for f in files:
                if "thumb" in f:
                    print("thumb")
                    ext = os.path.splitext(f)[1][1:]
                    thumb = "<img width={} src='data:image/{};base64,{}' >".format(WIDTH, ext, base64.b64encode(z.read(f)))
            cmds.text(hl=True, l=thumb, p=parent, ann=note)
            cmds.popupMenu(p=parent)
            cmds.menuItem(l="Load this version.", c=s.load)
            cmds.menuItem(l="Revert back to this version.", c=s.revert)

    def load(s):
        """ Load version """
        print("Loading temporary file!")

    def revert(s):
        """ Revert back to old version! """
        print("Replacing old file!!")


class Window(object):
    def __init__(s):
        """ Load up window! """
        cmds.window(t="Versions")
        col = cmds.columnLayout(adj=True)
        placeholder = cmds.text(l="No versions can be found...")
        grid = cmds.gridLayout()
        cmds.showWindow()

        path = cmds.file(q=True, sn=True)
        if path:
            root = os.path.join(os.path.dirname(path), "archive")
            scene = os.path.splitext(os.path.basename(path))[0]
            if os.path.isdir(root):
                strip = re.compile(r"[^\w]")
                scene_strip = strip.sub("", scene)
                form = re.compile(r"(.+)_(\d+)_(.+?)\.zip")
                scan = (form.match(a) for a in os.listdir(root))
                versions = [a for a in scan if a and strip.sub("", a.group(1)) == scene_strip]
                if versions:
                    cmds.deleteUI(placeholder)
                    grid = cmds.gridLayout(p=col, cw=WIDTH, ch=HEIGHT)
                    for version in versions:
                        col = cmds.columnLayout(p=grid, adj=True)
                        Version(col, root, version)
                        # threading.Thread(
                        #     target=Version,
                        #     args=(grid, root, version))
