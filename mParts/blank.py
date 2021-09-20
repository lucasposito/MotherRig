import maya.cmds as cmds
from random import uniform as rd

import mCore


class Blank:
    def __init__(self, name):
        self.main = []
        self.name = name
        self.init_position = None

        self.self_inner = None  # leaf node
        self.self_outer = None  # leaf node

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None  # leaf node

        self.connectors = {'root': []}  # 'root':[proxy_pxy, qt_node, joint, control]

    def set_main(self):
        pass

    def set_ik(self):
        pass

    def set_fk(self):
        circle = mCore.curve.quad_arrow('{}_ctr'.format(self.name))
        mCore.curve.curve_size(5)
        mCore.curve.curve_color(3)
        group = cmds.group(circle, n='{}_hrc'.format(self.name))
        self.self_inner = group
        self.self_outer = circle
        self.connectors['root'].append(circle)
        if self.init_position:
            cmds.xform(group, t=tuple(self.init_position))

    def set_ik_fk(self):
        pass
