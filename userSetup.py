import maya.cmds as cmds

if not cmds.about(batch=True):
    cmds.evalDeferred('import mother_shelf')
    cmds.evalDeferred('import mCore')
    cmds.evalDeferred('import mParts')
