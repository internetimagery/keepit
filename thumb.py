# Capture a thumbnail
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import os.path
import re

FMT = {
    ".jpg": 8,
    ".jpeg": 8,
    ".png": 32
    }

def capture(width, dest, seq, pref="thumb"):
    """ Capture thumbnail """

    seq = [int(a) for a in seq] # can't use floats in filenames
    result = []
    root = os.path.join(dest, pref)
    # Collect information:
    view = cmds.playblast(activeEditor=True) # Panel to capture from
    camera = cmds.modelEditor(view, q=True, cam=True)
    # state = cmds.modelEditor(view, q=True, sts=True)
    # imgFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
    selection = cmds.ls(sl=True) # Current selection
    start = cmds.currentTime(q=True)
    # Capture our thumbnail
    cmds.undoInfo(state=False)
    try:
        try:
            cmds.select(cl=True) # Clear selection for pretty image
            # cmds.modelEditor( # Tweak nice default visuals
            #     view,
            #     e=True,
            #     grid=False,
            #     camera=camera,
            #     da="smoothShaded",
            #     allObjects=False,
            #     imagePlanes=True,
            #     nurbsSurfaces=True,
            #     polymeshes=True,
            #     subdivSurfaces=True,
            #     displayTextures=True)
            output = cmds.playblast(
                frame=seq, # Frame range
                os=True, # Render off screen
                fo=True, # Force override the file if it exists
                viewer=False, # Don't popup window during render
                width=width*2, # Width in pixels, duh
                # height=pixels*2, # Height in pixels. Who knew
                showOrnaments=False, # Hide tools, ie move tool etc
                format="image", # We just want a single image
                compression="jpg",
                rawFrameNumbers=True,
                filename=root.replace("\\", "/")) # Output file)
            hash_ = re.search(r"#+", output)
            if hash_:
                hash_num = len(hash_.group(0))
                hash_path = output.replace(hash_.group(0), "{0:0>%s}" % hash_num)

                for path in (hash_path.format(a) for a in seq):
                    if os.path.isfile(path):
                        result.append(path)
        # Put everything back as we found it.
        finally:
            # Reset options
            cmds.currentTime(start)
            cmds.select(selection, r=True)
            # cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
            mel.eval("$editorName = \"%s\"" % view)
            # mel.eval(state)
    finally:
        cmds.undoInfo(state=True)
    return result
