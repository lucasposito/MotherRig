import maya.cmds as cmds
from random import uniform as rd

import mCore


class Single:
    def __init__(self, name, position=None, side=None):
        self.main = []
        self.name = [name]
        self.init_position = position
        self.side = side

        self.self_inner = None  # leaf node
        self.self_outer = None  # leaf node

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None  # leaf node

        self.connectors = {'root': []}  # 'root':[proxy_pxy, qt_node, joint, control]

        self.set_proxy()

    def set_main(self):
        pass

    def set_proxy(self):
        if not self.init_position:
            self.init_position = [0, 0, 0]

        proxy = mCore.curve.knot('{}_pxy'.format(self.name[0]))
        cmds.move(rd(self.init_position[0] + 5, self.init_position[0]), rd(self.init_position[1] + 10, self.init_position[1] + 5),
                  rd(self.init_position[2], self.init_position[2]), proxy)

        cmds.select(cl=True)
        self.connectors['root'].append(proxy)

    def set_ik(self):
        self.set_fk()

    def set_fk(self):
        circle = mCore.curve.quad_arrow('{}_ctr'.format(self.name[0]))
        mCore.curve.size(5)
        mCore.curve.color(3)
        group = cmds.group(circle, n='{}_hrc'.format(self.name[0]))
        self.self_inner = group
        self.self_outer = circle
        self.connectors['root'].append(circle)
        if self.init_position:
            cmds.xform(group, t=tuple(self.init_position))

    def set_ik_fk(self):
        self.set_fk()
