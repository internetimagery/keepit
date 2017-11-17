# File archive
from __future__ import print_function
import os.path
import zipfile
import shutil
import time
import re

ARCHIVE = "archive"
EXT = (".ma", ".mb")
WHITELIST = re.compile(r"[^ \.\-\_\w]")

def main(root, source, copy, note):
    """ Archive into folder. Note in filename """
    # Create an archive folder
    archive = os.path.join(root, ARCHIVE)
    if not os.path.isdir(archive):
        os.mkdir(archive)

    # Grab a file to use as the base name for archive
    for basename in copy:
        if os.path.splitext(basename)[-1] in EXT:
            break

    # Create a file name for archive
    name = os.path.splitext(os.path.basename(basename))[0]
    stamp = int(time.time() * 100)
    while True:
        filename = WHITELIST.sub("_", "{}_{}_{}".format(name, stamp, note)) + ".zip"
        dest = os.path.join(archive, filename)
        if not os.path.isfile(dest):
            break
        stamp += 1

    # Create our archive!
    z = zipfile.ZipFile(dest, "w")
    err = None
    try:
        for src in copy:
            z.write(src, os.path.basename(src))
        return "File archived to {}".format(dest)
    except Exception as err:
        raise
    finally:
        z.close()
        if err:
            shutil.move(dest, os.path.join(archive, "CORRUPT-{}".format(filename)))
