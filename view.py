# View recent versions based on "file" archive
# TODO: This is not well structured. Should be integrated into archive directly
from __future__ import print_function
import maya.utils as utils
import maya.cmds as cmds
import threading
import tempfile
import datetime
import os.path
import zipfile
import base64
import shutil
import json
import os
import re

WIDTH = HEIGHT = 160


SEM = threading.BoundedSemaphore(1)

def ucmds(func, *args, **kwargs):
    SEM.acquire()
    try:
        return utils.executeInMainThreadWithResult(func, *args, **kwargs)
    finally:
        SEM.release()

class Version(object):
    def __init__(s, parent, root, version):
        """ Version! """
        s.archive = os.path.join(root, version.group(0))
        with zipfile.ZipFile(s.archive, "r") as z:
            try:
                s.index = index_data = json.loads(z.read("index.json"))

                thumb = "<img width={} src='data:image/{};base64,{}'>".format(
                    WIDTH, os.path.splitext(index_data["thumb"])[1][1:], base64.b64encode(z.read(index_data["thumb"])))
                desc = "created: {}\nnote: {}".format(datetime.datetime.fromtimestamp(index_data["time"]), index_data["note"])
                if ucmds(cmds.layout, parent, q=True, ex=True):
                    ucmds(cmds.text, hl=True, l=thumb, ann=desc, bgc=(0,0,0))
                    ucmds(cmds.popupMenu, p=parent)
                    ucmds(cmds.menuItem, l="Load this version.", c=s.load)
                    ucmds(cmds.menuItem, l="Revert back to this version.", c=s.revert)
            except KeyError:
                # No index file...
                pass

    def load(s, *_):
        """ Load version """
        root = tempfile.mkdtemp()
        try:
            scene = os.path.join(root, s.index["scene"])
            with open(scene, "w") as f:
                with zipfile.ZipFile(s.archive, "r") as z:
                    f.write(z.read(s.index["scene"]))
            cmds.scriptJob(ro=True, e=("SceneOpened", lambda: (cmds.file(rename=""), shutil.rmtree(root))))
            cmds.file(scene, open=True, force=True)
        except Exception as err:
            shutil.rmtree(root)
            raise err

    def revert(s, *_):
        """ Revert back to old version! """
        print("Replacing old file!!")


class Window(object):
    def __init__(s):
        """ Load up window! """
        cmds.window(t="Versions", rtf=True)
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
                    for version in sorted(versions, reverse=True, key=lambda x: x.group(1))[:10]:
                        col = cmds.columnLayout(p=grid, adj=True)
                        Version(col, root, version)
                        # threading.Thread(
                        #     target=Version,
                        #     args=(col, root, version)).start()
