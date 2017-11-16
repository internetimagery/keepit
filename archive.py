# Archive stuff!
from __future__ import print_function
import maya.utils as utils
import threading
import os.path
import imp
import os

def safe_print(*args, **kwargs):
    """ Print out messages in a threadsafe manner """
    SEM.acquire()
    utils.executeDeferred(print, *args, **kwargs)
    SEM.release()

SEM = threading.BoundedSemaphore(1)
ROOT = os.path.join(os.path.dirname(__file__), "archives")
ARCHIVERS = []
for path in os.listdir(ROOT):
    name, ext = os.path.splitext(path)
    if ext == ".py":
        module = imp.load_source(name, os.path.join(ROOT, path))
        # Inject safe printing
        module.print = safe_print
        ARCHIVERS.append(module)

def archive(path, note):
    """ Given a filepath and note, archive file """
    pass
