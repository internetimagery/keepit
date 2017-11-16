# coding: utf-8
# Dummy addon. Doesn't do anything, but is something to build off of.
#
# Created by Jason Dixon
# 02/05/15
import maya.cmds as cmds
import maya.mel as mel

debug = True  # Add this to override caching. So changes can be observed while testing.


def run_hook(mayaFile, todo, settings):
    """
    Run hook for whatever event is fired.
    mayaFile = path to scene.
    todo = todo metadata (optional).
    settings = get() and set() settings. !!Beware setting the settings in hooks other than ones denoted with "settings" ie "settings.archive"!!
    """
    pass


def hooks():
    return {
        "settings.archive": run_hook,  # Populate the settings menu with archive options
        "todo.complete": run_hook,  # Fired upon completion of a todo
        "todo.delete": run_hook,  # Todo has been deleted (trash can button)
        "todo.create": run_hook,  # A New Todo has been created
        "todo.edit": run_hook,  # An existing Todo has had its name changed
        "app.changeSection": run_hook,  # A section has been opened or closed
        "app.buildList": run_hook,  # The main todo list is populating with todos
        "app.start": run_hook,  # The script has been invoked (opened / run)
        "app.end": run_hook  # The window has been closed.
        }
