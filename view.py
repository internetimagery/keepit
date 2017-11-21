# View recent versions based on "file" archive
# TODO: This is not well structured. Should be integrated into archive directly
from __future__ import print_function
import maya.utils as utils
import maya.cmds as cmds
import threading
import functools
import itertools
import tempfile
import datetime
import os.path
import archive
import zipfile
import base64
import shutil
import popup
import time
import json
import os
import re

WIDTH = HEIGHT = 160

SEM = threading.BoundedSemaphore(1)

class tcmds(object):
    def __getattr__(s, func):
        def run(*args, **kwargs):
            SEM.acquire()
            try:
                return utils.executeInMainThreadWithResult(getattr(cmds, func), *args, **kwargs)
            finally:
                SEM.release()
        return run
tcmds = tcmds()

def confirm(message):
    ok = "OK!"
    if ok == cmds.confirmDialog(t="Hold up...", m=message, button=[ok,"Nope"], defaultButton="Nope"):
        return True
    return False

def img_tag(name, height, data):
    ext = os.path.splitext(name)[-1][1:]
    return "<img height={} src='data:image/{};base64,{}'>".format(
        height, ext, base64.b64encode(data))

class Version(object):
    def run(s, img, nt, root, version, anim):
        """ Version! """
        s.archive = os.path.join(root, version.group(0))
        with zipfile.ZipFile(s.archive, "r") as z:
            try:
                s.index = json.loads(z.read("index.json"))

                seq_images = [img_tag(a, HEIGHT-30, z.read(a)) for a in s.index.get("thumb_seq", [])]
                if seq_images:
                    seq = itertools.cycle(seq_images)
                    anim.anims[img] = seq

                created = datetime.datetime.strptime(s.index["time"], "%Y%m%d%H%M%S")
                desc = "created: {}\nnote: {}".format(created.strftime("%I:%M%p %a %d/%m/%Y"), s.index["note"])
                if tcmds.text(img, q=True, ex=True):
                    tcmds.text(img, e=True, l=img_tag(s.index.get("thumb", ""), HEIGHT-30, z.read(s.index["thumb"])), ann=desc)
                    tcmds.text(nt, e=True, l="{}...".format(s.index["note"][:17]) if len(s.index["note"]) > 20 else s.index["note"])
                    tcmds.popupMenu(p=img)
                    tcmds.menuItem(i="fileNew.png", l="Load this version. (temporary)", c=s.load)
                    tcmds.menuItem(i="reverseOrder.png", l="Revert back to this version.", c=s.revert)
            except KeyError as err:
                # No index file...
                utils.executeDeferred(print, "Missing index:", s.archive, err)

    def load(s, *_):
        """ Load version temporarally. """
        root = tempfile.mkdtemp()
        try:
            scene = os.path.join(root, s.index["scene"])
            with open(scene, "w") as f:
                with zipfile.ZipFile(s.archive, "r") as z:
                    f.write(z.read(s.index["scene"]))
            cmds.scriptJob(ro=True, e=("SceneOpened", lambda: (cmds.file(rename=""), cmds.file(rts=True), shutil.rmtree(root))))
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

class Animation(object):
    def __init__(s, window):
        s.window = window
        s.fps = 0.8
        s.sem = threading.BoundedSemaphore(1)
        s.playing = True
        s.anims = {}
        threading.Thread(target=s.loop).start()

    def loop(s):
        try:
            while s.playing:
                s.sem.acquire()
                utils.executeDeferred(cmds.scriptJob, ro=True, e=("idle", s.update))
                time.sleep(s.fps)
        except Exception as err:
            utils.executeDeferred(print, "Loop error:", err)

    def update(s):
        """ Update all frames """
        try:
            if cmds.window(s.window, q=True, ex=True):
                for gui, frame in s.anims.items():
                    if cmds.text(gui, q=True, ex=True):
                        cmds.text(gui, e=True, l=next(frame))
            else:
                print("Animation stopped")
                s.playing = False
        except Exception as err:
            print("update error:", err)
        finally:
            s.sem.release()


class Window(object):
    def __init__(s):
        """ Load up window! """
        threads = []
        win = cmds.window(t="Versions", rtf=True)
        col = cmds.columnLayout(adj=True)
        placeholder = cmds.text(l="No versions can be found...")
        anim = Animation(win)

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
                    for version in sorted(versions, reverse=True, key=lambda x: x.group(2))[:10]:
                        space = cmds.columnLayout(adj=True, p=grid)
                        img = cmds.text(hl=True, l="", p=space)
                        nt = cmds.text(ww=True, l="", p=space)
                        # Version().run(img, nt, root, version, anim)
                        threads.append(threading.Thread(
                            target=Version().run,
                            args=(img, nt, root, version, anim)))
        cmds.showWindow(win)
        for t in threads:
            t.start()
