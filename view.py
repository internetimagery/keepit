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

def confirm(message):
    ok = "OK!"
    if ok == cmds.confirmDialog(t="Hold up...", m=message, button=[ok,"Nope"], defaultButton="Nope"):
        return True
    return False


class Version(object):
    def run(s, img, nt, root, version):
        """ Version! """
        s.archive = os.path.join(root, version.group(0))
        with zipfile.ZipFile(s.archive, "r") as z:
            try:
                s.index = json.loads(z.read("index.json"))

                thumb = "<img width={} src='data:image/{};base64,{}'>".format(
                    WIDTH, os.path.splitext(s.index["thumb"])[1][1:], base64.b64encode(z.read(s.index["thumb"])))
                desc = "created: {}\nnote: {}".format(datetime.datetime.fromtimestamp(s.index["time"]), s.index["note"])
                if ucmds(cmds.text, img, q=True, ex=True):
                    ucmds(cmds.text, img, e=True, l=thumb, ann=desc)
                    ucmds(cmds.text, nt, e=True, l="{}...".format(s.index["note"][:17]) if len(s.index["note"]) > 20 else s.index["note"])
                    ucmds(cmds.popupMenu, p=img)
                    ucmds(cmds.menuItem, i="fileNew.png", l="Load this version. (temporary)", c=s.load)
                    ucmds(cmds.menuItem, i="reverseOrder.png", l="Revert back to this version.", c=s.revert)
            except KeyError as err:
                # No index file...
                ucmds(print, "Missing index:", s.archive, err)

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
            if confirm("Cannot find original file: {}\nPlesae provide a folder to recover the file in.".format(source)):
                path = cmds.fileDialog2(fileMode=3)
                if not path:
                    return
                source = os.path.join(path[0], os.path.basename(source))
            else:
                return

        if confirm("You will lose all unsaved changes if you continue.\nAre you sure?"):
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
                    max_versions = 10
                    max_cols = int((max_versions ** -0.5) * max_versions + 1)
                    grid = cmds.gridLayout(p=col, cw=WIDTH, ch=HEIGHT, nc=max_cols)
                    threads = []
                    for version in sorted(versions, reverse=True, key=lambda x: x.group(2))[:10]:
                        space = cmds.columnLayout(adj=True, p=grid)
                        img = cmds.text(hl=True, l="", p=space)
                        nt = cmds.text(ww=True, l="", p=space)
                        # Version().run(cmds.columnLayout(adj=True, p=grid), root, version)
                        threads.append(threading.Thread(
                            target=Version().run,
                            args=(img, nt, root, version)))
                    for t in threads:
                        t.start()
        cmds.showWindow(win)
