# View recent versions based on "file" archive
# TODO: This is not well structured. Should be integrated into archive directly
from __future__ import print_function
import maya.utils as utils
import maya.cmds as cmds
import threading
import functools
import tempfile
import datetime
import os.path
import archive
import zipfile
import base64
import shutil
import popup
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
    def run(s, parent, root, version):
        """ Version! """
        s.archive = os.path.join(root, version.group(0))
        with zipfile.ZipFile(s.archive, "r") as z:
            try:
                s.index = index_data = json.loads(z.read("index.json"))

                thumb = "<img width={} src='data:image/{};base64,{}'>".format(
                    WIDTH, os.path.splitext(index_data["thumb"])[1][1:], base64.b64encode(z.read(index_data["thumb"])))
                desc = "created: {}\nnote: {}".format(datetime.datetime.fromtimestamp(index_data["time"]), index_data["note"])
                if ucmds(cmds.text, parent, q=True, ex=True):
                    ucmds(cmds.text, parent, e=True, l=thumb, ann=desc, bgc=(0,0,0))
                    ucmds(cmds.popupMenu, p=parent)
                    ucmds(cmds.menuItem, l="Load this version.", c=s.load)
                    ucmds(cmds.menuItem, l="Revert back to this version.", c=s.revert)
            except KeyError as err:
                # No index file...
                ucmds(print, "ERROR:", err, s.archive)

    def load(s, *_):
        """ Load version temporarally. """
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
        # check if file is in its old location
        source = s.index["source"]
        if not os.path.isfile(source):
            if cmds.confirmDialog(t="Hold up...", m="Cannot find original file: {}\nPlesae provide a folder to recover the file in.".format(source)):
                path = cmds.fileDialog2(fileMode=3)
                if not path:
                    return
                source = os.path.join(path[0], os.path.basename(source))
            else:
                return

        if cmds.confirmDialog(t="Here we go...", m="You will lose all unsaved changes if you continue.\nAre you sure?"):
            note = "AUTOSAVE: Recovering version '{}'".format(s.index["note"])
            sup = popup.Startup(note)
            with sup:
                # we lied... we will save unsaved changes anyway!
                cmds.file(rename=source)
                cmds.file(save=True, force=True)
                archive.archive(note, source)

                # Recover file
                with zipfile.ZipFile(s.archive, "r") as z:
                    with open(source, "w") as f:
                        f.write(z.read(s.index["scene"]))

                # Load the file
                cmds.file(source, open=True, force=True)

class Window(object):
    def __init__(s):
        """ Load up window! """
        win = cmds.window(t="Versions", rtf=True)
        col = cmds.columnLayout(adj=True)
        placeholder = cmds.text(l="No versions can be found...")
        grid = cmds.gridLayout()

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
                    grid = cmds.gridLayout(p=col, cr=True, cw=WIDTH, ch=HEIGHT)
                    threads = []
                    for version in sorted(versions, reverse=True, key=lambda x: x.group(2))[:10]:
                        text = cmds.text(hl=True, l="", p=grid)
                        # Version(text, root, version)
                        threads.append(threading.Thread(
                            target=Version().run,
                            args=(text, root, version)))
                    for t in threads:
                        t.start()
        cmds.showWindow(win)
