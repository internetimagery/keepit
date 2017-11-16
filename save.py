# Save scene
import maya.cmds as cmds
import maya.mel as mel

def kill(id_):
    """ Kill script job """
    if cmds.scriptJob(ex=id_):
        cmds.scriptJob(kill=id_)

def Save(func):
    """ Save scene! """
    job = cmds.scriptJob(e=('SceneSaved', func), ro=True)
    cmds.scriptJob(e=('idle', lambda: kill(job)), ro=True)
    try:
        mel.eval("checkForUnknownNodes(); FileMenu_SaveItem") # Perform save, using mayas built in save
    except Exception as err:
        kill(job)
        raise err


#
#
#         if os.path.isfile(cmds.file(q=True, sn=True)):  # Check the scene is not untitled and still exists
#             process = cmds.scriptJob(e=['SceneSaved', performArchive], ro=True)
#             try:
#                 message = """
# <div>- This Scene was last saved on <em>%(time)s</em>.</div>
# <div>- Completing the task: <code>%(todo)s</code></div>
# <div>- The file <strong>has not been modified since.</strong></div><br>
# """ % {"time": time.ctime(), "todo": tempmeta["label"]}
#                 with Popup(message):
#                     cmds.file(save=True)  # Save the scene
#             except RuntimeError:  # If scene save was canceled or failed. Reset everything
#                 if cmds.scriptJob(ex=process):
#                     cmds.scriptJob(kill=process)
#                 s.data[uid] = temp
#                 s._buidTodoTasks()
#         else:
#             performArchive()
