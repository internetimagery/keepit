# Archive stuff!
from __future__ import print_function
import maya.utils as utils
import traceback
import threading
import tempfile
import os.path
import shutil
import thumb
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

def run_archive(root, src, dest, note, module, callback):
    """ Run archive and when done, return """
    res = None
    try:
        res = module.main(root, src, dest, note)
    except Exception as err:
        res = traceback.format_exc()
    finally:
        callback(res)

def archive(note, root, src):
    """ Given a list of filepaths and note, archive file """
    # Create a temporary file
    tmp_root = tempfile.mkdtemp()
    try:

        # Copy save file to safe location
        dest = [os.path.join(tmp_root, os.path.basename(a)) for a in src]
        for s, d in zip(src, dest):
            shutil.copy(s, d)

        # Create thumbnail
        pic = thumb.capture(500, tmp_root, "thumb.jpg")
        if pic:
            dest.append(pic)

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
            threading.Thread(
                target=run_archive,
                args=(root, src, dest, note, module, cleanup)
                ).start()

    except Exception as err:
        shutil.rmtree(tmp_root)
        raise err
