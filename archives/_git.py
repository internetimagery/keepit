


def main(*_):
    # TODO: Make this work
    # TODO: Working reference below!
    pass

# def archive(mayaFile, todo, settings):
#     if settings.get("GitArchive.active", False) and mayaFile:
#         check = Git().status(mayaFile)
#         if check[1]:
#             print "Cannot commit file: %s." % check[1]
#         else:
#             if Git().commit(mayaFile, todo["label"]) and settings.get("GitArchive.push", False):
#                 print "Pushing update"
#                 push = settings.get("GitArchive.branch", None)
#                 pushed = Git().push(mayaFile, push)
#                 print pushed[1] if pushed[1] else pushed[0]
#
#
# def hooks():
#     return {
#         "settings.archive": settings_archive,
#         "todo.complete": archive
#         }
#
#
# class Git(object):
#     """
#     Control Git
#     """
#     def __init__(s, *args, **kwargs):
#         if args or kwargs:
#             return s._git(*args, **kwargs)
#
#     def _git(s, *args, **kwargs):
#         """
#         git command line function
#         """
#         try:
#             return sub.Popen(["git"] + list(args), stdout=sub.PIPE, stderr=sub.PIPE, **kwargs).communicate()
#         except OSError as e:
#             return ("", e.__str__())
#
#     def push(s, path, dest):
#         return s._git("push", dest, cwd=os.path.dirname(path))
#
#     def commit(s, path, comment):
#         if not s._git("add", os.path.basename(path), cwd=os.path.dirname(path))[1]:
#             if not s._git("commit", "--quiet", "--message", comment, "--only", os.path.basename(path), cwd=os.path.dirname(path))[1]:
#                 print "File committed"
#                 return True
#
#     def status(s, path):
#         return s._git("status", "--porcelain", os.path.basename(path), cwd=os.path.dirname(path))
#
#     def version(s):
#         return s._git("--version")
