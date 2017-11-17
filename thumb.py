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

def capture(pixels, dest, name="thumb.jpg"):
    """ Capture thumbnail """
    # Validate our inputs
    if not pixels or type(pixels) != int:
        raise RuntimeError, "No valid size provided"
    # Collect information:
    out_path = os.path.join(dest, name)
    ext = os.path.splitext(name)[1].lower()
    if ext not in FMT:
        raise RuntimeError("Format not yet supported \"{}\"".format(ext))
    view = cmds.playblast(activeEditor=True) # Panel to capture from
    camera = cmds.modelEditor(view, q=True, cam=True)
    state = cmds.modelEditor(view, q=True, sts=True)
    imgFormat = cmds.getAttr("defaultRenderGlobals.imageFormat")
    selection = cmds.ls(sl=True) # Current selection
    # Capture our thumbnail
    cmds.undoInfo(state=False)
    try:
        try:
            cmds.select(cl=True) # Clear selection for pretty image
            cmds.setAttr("defaultRenderGlobals.imageFormat", FMT[ext])
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
            cmds.playblast(
                frame=cmds.currentTime(q=True), # Frame range
                os=True, # Render off screen
                fo=True, # Force override the file if it exists
                viewer=False, # Don't popup window during render
                width=pixels*2, # Width in pixels, duh
                # height=pixels*2, # Height in pixels. Who knew
                showOrnaments=False, # Hide tools, ie move tool etc
                format="image", # We just want a single image
                completeFilename=out_path.replace("\\", "/")) # Output file
        # Put everything back as we found it.
        finally:
            # Reset options
            cmds.select(selection, r=True)
            cmds.setAttr("defaultRenderGlobals.imageFormat", imgFormat)
            mel.eval("$editorName = \"%s\"" % view)
            mel.eval(state)
    finally:
        cmds.undoInfo(state=True)
    return out_path if os.path.isfile(out_path) else ""
