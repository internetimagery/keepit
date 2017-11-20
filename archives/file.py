# File archive
from __future__ import print_function
import os.path
import zipfile
import shutil
import time
import re

ARCHIVE = "archive"
WHITELIST = re.compile(r"[^ \.\-\_\w]")

def main(temp_dir, source, files, note):
    """ Archive into folder. Note in filename """
    # Create an archive folder
    archive = os.path.join(os.path.dirname(source), ARCHIVE)
    if not os.path.isdir(archive):
        os.mkdir(archive)

    # name our archive
    basename = os.path.basename(source)

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
        for src in files:
            z.write(src, os.path.basename(src))
        return "File archived to {}".format(dest)
    except Exception as err:
        raise
    finally:
        z.close()
        if err:
            shutil.move(dest, os.path.join(archive, "CORRUPT-{}".format(filename)))
