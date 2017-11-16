import maya.cmds as cmds
import popup

def main():
    """ Perform an archive save! """
    note = popup.Prompt()
    if note:
        pass




def embedImage():
    """
    Grab a random image and embed it in the scene.
    """
    path = os.path.join(os.path.dirname(__file__), "images")
    images = [os.path.join(path, f) for f in os.listdir(path) if f.endswith(".png")]
    if images:
        image = random.choice(images)
        ext =
        with open(image, "rb") as f:
            image = "<img src=\\\"data:image/png;base64,%s\\\">" % base64.b64encode(f.read())
        return "cmds.text(hl=True, l=\"%s\", h=100, w=100)" % image
    else:
        return "cmds.iconTextStaticLabel(image=\"envChrome.svg\", h=100, w=100)  # file.svg looks nice too..."



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
