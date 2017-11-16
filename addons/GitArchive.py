# coding: utf-8
# Archive options for Git
#
# Created by Jason Dixon
# 04/05/2015
import subprocess as sub
import maya.cmds as cmds
import os


# Settings menu
def settings_archive(mayaFile, todo, settings):

    def getInput():
        result = cmds.promptDialog(
            title="Optional Branch",
            message="Enter Branch Name:",
            button=["OK", "Cancel"],
            defaultButton="OK",
            cancelButton="Cancel",
            dismissString="Cancel")
        if result == "OK":
            return cmds.promptDialog(q=True, text=True)
        return ""

    version = Git().version()
    if not version[1]:
        git = settings.get("GitArchive.active", False)
        push = settings.get("GitArchive.push", False)
        branch = settings.get("GitArchive.branch", None)
        cmds.columnLayout(
            adjustableColumn=True,
            ann="Commit the Maya file into Git (if the file is located in a valid repo) upon each Todo task completion.",
            bgc=[0.5, 0.5, 0.5] if git else [0.2, 0.2, 0.2])
        cmds.checkBox(
            l="Use Git archive",
            v=git,
            cc=lambda x: settings.set("GitArchive.active", x))
        cmds.rowColumnLayout(nc=2, en=git)
        cmds.text(label=" - ")
        cmds.checkBox(
            l="Automatically PUSH changes.",
            v=push,
            cc=lambda x: settings.set("GitArchive.push", x))
        cmds.text(label=" - ")
        cmds.iconTextButton(
            en=push,
            image="createContainer.png",  # "publishNamedAttribute.png" "channelBoxHyperbolicOn.png"  "createContainer.png"
            l=branch if branch else "Enter remote branch name.",
            style="iconAndTextHorizontal",
            c=lambda: settings.set("GitArchive.branch", getInput()))
        cmds.setParent("..")
        cmds.text(
            en=git,
            l="%s found." % version[0].capitalize().replace("\n", ""))
        cmds.setParent("..")


def archive(mayaFile, todo, settings):
    if settings.get("GitArchive.active", False) and mayaFile:
        check = Git().status(mayaFile)
        if check[1]:
            print "Cannot commit file: %s." % check[1]
        else:
            if Git().commit(mayaFile, todo["label"]) and settings.get("GitArchive.push", False):
                print "Pushing update"
                push = settings.get("GitArchive.branch", None)
                pushed = Git().push(mayaFile, push)
                print pushed[1] if pushed[1] else pushed[0]


def hooks():
    return {
        "settings.archive": settings_archive,
        "todo.complete": archive
        }


class Git(object):
    """
    Control Git
    """
    def __init__(s, *args, **kwargs):
        if args or kwargs:
            return s._git(*args, **kwargs)

    def _git(s, *args, **kwargs):
        """
        git command line function
        """
        try:
            return sub.Popen(["git"] + list(args), stdout=sub.PIPE, stderr=sub.PIPE, **kwargs).communicate()
        except OSError as e:
            return ("", e.__str__())

    def push(s, path, dest):
        return s._git("push", dest, cwd=os.path.dirname(path))

    def commit(s, path, comment):
        if not s._git("add", os.path.basename(path), cwd=os.path.dirname(path))[1]:
            if not s._git("commit", "--quiet", "--message", comment, "--only", os.path.basename(path), cwd=os.path.dirname(path))[1]:
                print "File committed"
                return True

    def status(s, path):
        return s._git("status", "--porcelain", os.path.basename(path), cwd=os.path.dirname(path))

    def version(s):
        return s._git("--version")
