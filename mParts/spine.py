import maya.cmds as cmds

import mCore


class Spine:
    def __init__(self, objects=None, name=None):
        self.main = []
        self.position = {}
        self.name = name

        self.inner_plug = None
        self.outer_plug = None

    def _get_position(self):
        arm_key = ['Arm', 'ForeArm', 'Hand']
        for name, obj in zip(arm_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def _set_main(self):
        pass

    def reset_proxy(self):
        pass

    def reset_main(self):
        pass

    def set_ik(self):
        pass

    def set_fk(self):
        pass

    def set_ik_fk(self):
        pass

    def _remove_controls(self):
        pass
