# coding: utf-8
# Import AMP support
# Created by Jason Dixon
# 02/05/15
# AMP Pipeline is copywrite Animation Mentor
import am.client.bootstrap.clientVersion as version
import am.client.cmclient.manager as manager
import am.client.cmclient.config as config
import am.client.gui.utils as AMutils
import maya.utils as Mutils
import maya.cmds as cmds
import os

#debug = True


# Settings menu
def settings_archive(mayaFile, todo, settings):
    amp = settings.get("AMPArchive.active", False)
    cmds.columnLayout(
        adjustableColumn=True,
        ann="Check the file into AMP upon each Todo task completion.",
        bgc=[0.5, 0.5, 0.5] if amp else [0.2, 0.2, 0.2])
    cmds.checkBox(
        l="Use AMP archive",
        v=amp,
        cc=lambda x: settings.set("AMPArchive.active", x))
    cmds.text(
        en=amp,
        l="AMP version %s found." % version.version)
    cmds.setParent("..")


# File Archive
def archive(mayaFile, todo, settings):
    comment = todo["label"]
    amp = settings.get("AMPArchive.active", False)
    if amp and mayaFile:
        if Mutils.executeInMainThreadWithResult(lambda: AMPArchive().archive(mayaFile, comment)):
            print "Checking file into AMP."
        else:
            print "Couldn't check in file to AMP."


def hooks():
    return {
        "settings.archive": settings_archive,
        "todo.complete": archive
        }


class AMPArchive(object):
    """
    Archive using AMP
    """
    def __init__(s):
        s.config = config.Configurator()
        s.manager = manager.getShotManager(config=s.config)
        #s.root = s.manager.contentRoot

    def archive(s, path, comment):
        """
        Save off file.
        """
        if os.path.isfile(path) and s.login() and s.manager.isClientPathManaged(path):
            if s._status(path):
                s._checkIn(path, comment)
                s._checkOut(path)
                return True
            elif "Confirm" == cmds.confirmDialog(title="Hold up...", message="You need to check out the file first.\nWould you like to do that now?"):
                s._checkOut(path)
                s._checkIn(path, comment)
                s._checkOut(path)
                return True
        return False

    def _checkLogin(s):
        """
        Check login status. Return True for logged in.
        """
        return s.manager.checkSessionToken()

    def _checkIn(s, path, comment):
        """
        Check in the file to lock in changes.
        """
        if not s.manager.checkinViewItemByPath(path, comment=comment):
            s.manager.addViewItemByPath(path, comment=comment)

    def _checkOut(s, path):
        """
        Check out file for editing.
        """
        s.manager.checkoutViewItemByPath(path)

    def _revert(s, path):
        """
        Revert file back to the most recent state.
        """
        s.manager.revertViewItemByPath(path)

    def _status(s, path):
        """
        Check the locked status of a file.
        """
        return os.access(path, os.W_OK)  # True = Checked out. False = Checked in.

    def login(s):
        """
        Check if we are logged in. If not, try to log in.
        """
        def cancel():
            s.again = False
        s.again = True

        def ok():
            s.config.setDefaultServer(d.server_name)
            s.manager.login(unicode(d.username), unicode(d.password))

        for i in range(10):
            if s.again:
                if s.manager.checkSessionToken():  # Check if we are logged in.
                    print "Signed into AMP."
                    return True
                else:
                    print "Login attempt %s of 10." % str(i + 1)
                    d = AMutils.LoginDialog(
                        message_to_user="Can't archive your file to AMP.\nYou are not logged in.\nLets log in now. :)",
                        server_config=s.config)
                    d.set_click_handler("ok", ok)
                    d.set_click_handler("cancel", cancel)
                    d.draw()
                    d.exec_()
        return False
