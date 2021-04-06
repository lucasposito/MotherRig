from maya import utils, cmds

if not cmds.about(batch=True):
    utils.executeDeferred('import mother_shelf')
