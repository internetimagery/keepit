# Import modules
import sys
import os
import re

path = os.path.dirname(__file__)
sys.path.append(path)
reg = re.compile("^([^_\.]\w*?)(?:\.py)$")  # allow modules with no . or _ as first letter, and no spaces

modules = {}
for f in [reg.match(m).group(1) for m in os.listdir(path) if reg.match(m)]:
    try:
        modules[f] = __import__(f)
        if hasattr(modules[f], "debug") and modules[f].debug:
            reload(modules[f])
    except Exception as e:
        print "Did not load %s." % f, e
