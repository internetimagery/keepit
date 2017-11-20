# Capture a thumbnail
from __future__ import print_function
import maya.cmds as cmds
import maya.mel as mel
import os.path

FMT = {
    ".jpg": 8,
    ".jpeg": 8,
    ".png": 32
    }

def capture(width, dest, seq):
    """ Capture thumbnail """

    # Collect information:
    out_seq = {}
    view = cmds.playblast(activeEditor=True) # Panel to capture from
    camera = cmds.modelEditor(view, q=True, cam=True)
    state = cmds.modelEditor(view, q=True, sts=True)
    imgFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
    selection = cmds.ls(sl=True) # Current selection
    start = cmds.currentTime(q=True)
    # Capture our thumbnail
    cmds.undoInfo(state=False)
    try:
        try:
            cmds.select(cl=True) # Clear selection for pretty image
            cmds.modelEditor( # Tweak nice default visuals
                view,
                e=True,
                grid=False,
                camera=camera,
                da="smoothShaded",
                allObjects=False,
                nurbsSurfaces=True,
                polymeshes=True,
                subdivSurfaces=True,
                displayTextures=True)
            for frame in seq:
                ext = os.path.splitext(seq[frame])[1].lower()
                if ext not in FMT:
                    raise RuntimeError("Format not yet supported \"{}\"".format(ext))
                cmds.setAttr("defaultRenderGlobals.imageFormat", FMT[ext])
                out_path = os.path.join(dest, seq[frame])
                cmds.playblast(
                    frame=frame, # Frame range
                    os=True, # Render off screen
                    fo=True, # Force override the file if it exists
                    viewer=False, # Don't popup window during render
                    width=width*2, # Width in pixels, duh
                    # height=pixels*2, # Height in pixels. Who knew
                    showOrnaments=False, # Hide tools, ie move tool etc
                    format="image", # We just want a single image
                    completeFilename=out_path.replace("\\", "/")) # Output file
                if os.path.isfile(out_path):
                    out_seq[frame] = out_path
        # Put everything back as we found it.
        finally:
            # Reset options
            cmds.currentTime(start)
            cmds.select(selection, r=True)
            cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
            mel.eval("$editorName = \"%s\"" % view)
            mel.eval(state)
    finally:
        cmds.undoInfo(state=True)
    return out_seq
