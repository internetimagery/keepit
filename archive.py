# Archive stuff!
from __future__ import print_function, division
import maya.utils as utils
import maya.cmds as cmds
import traceback
import threading
import tempfile
import datetime
import os.path
import shutil
import thumb
import json
import imp
import os

def safe_func(func):
    """ Call function in threadsafe manner """
    def run(*args, **kwargs):
        SEM.acquire()
        try:
            return utils.executeInMainThreadWithResult(func, *args, **kwargs)
        finally:
            SEM.release()
    return run

SEM = threading.BoundedSemaphore(1)
ROOT = os.path.join(os.path.dirname(__file__), "archives")
ARCHIVERS = []
for path in os.listdir(ROOT):
    name, ext = os.path.splitext(path)
    if ext == ".py" and name[0] != "_":
        module = imp.load_source(name, os.path.join(ROOT, path))
        # Inject safe functions
        module.print = safe_func(print)
        try:
            module.cmds = safe_func(module.cmds)
        except AttributeError:
            pass
        ARCHIVERS.append(module)

def run_archive(root, src, files, note, module, callback):
    """ Run archive and when done, return """
    res = None
    try:
        res = module.main(root, src, files, note)
    except Exception as err:
        res = traceback.format_exc()
    finally:
        callback(res)

def archive(note, src):
    """ Given a list of filepaths and note, archive file in a neat package. """
    root = os.path.dirname(src)
    # Create a temporary file
    tmp_root = tempfile.mkdtemp()
    try:
        files = []

        # Copy save file to safe location
        dest_name = os.path.basename(src)
        dest = os.path.join(tmp_root, dest_name)
        shutil.copy(src, dest)
        files.append(dest)

        # Create thumbnails
        timeline_range = cmds.playbackOptions(q=True, min=True), cmds.playbackOptions(q=True, max=True)
        num_thumbs = 10
        frame_scale = (timeline_range[1] - timeline_range[0]) / num_thumbs
        thumb_name = "thumb_{0:0>2}.jpg"
        start = cmds.currentTime(q=True)
        thumb_seq = []
        for i in range(num_thumbs + 1):
            frame = i * frame_scale + timeline_range[0]
            cmds.currentTime(frame)
            tn = thumb_name.format(i)
            thumb_path = thumb.capture(500, tmp_root, tn)
            if thumb_path:
                thumb_seq.append(tn)
                files.append(thumb_path)

        # Index file!
        index_name = "index.json"
        index_data = {
            "time": datetime.datetime.now().isoformat(),
            "note": note,
            "scene": dest_name,
            "source": src,
            "thumb": thumb_seq[0] if thumb_seq else "",
            "thumb_seq": thumb_seq}
        index_path = os.path.join(tmp_root, index_name)
        with open(index_path, "w") as f:
            json.dump(index_data, f, indent=4)
        files.append(index_path)

        # Run when all archivers are complete
        results = []
        def cleanup(res):
            results.append(res)
            if len(results) == len(ARCHIVERS):
                shutil.rmtree(tmp_root)
                p = safe_func(print)
                for res in results:
                    p(res)

        # Run archivers!
        for module in ARCHIVERS:
            run_archive(tmp_root, src, files, note, module, cleanup)
            # threading.Thread(
            #     target=run_archive,
            #     args=(tmp_root, src, files, note, module, cleanup)
            #     ).start()

    except Exception as err:
        shutil.rmtree(tmp_root)
        raise err
