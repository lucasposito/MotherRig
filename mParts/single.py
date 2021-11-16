import maya.cmds as cmds
from random import uniform as rd

import mCore


class Single:
    def __init__(self, name, position=None, side=None):
        self.main = []
        self.name = [name]
        self.init_position = position
        self.position = None
        self.side = side

        self.color = {'Left': 6, 'Right': 13, 'Center': 17}

        self.self_inner = None  # leaf node
        self.self_outer = None  # leaf node

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None  # leaf node

        self.connectors = {'root': []}  # 'root':[proxy_pxy, qt_node, joint, control]

        self.set_proxy()

    def set_main(self):
        self.position = cmds.xform(self.connectors['root'][0], q=True, ws=True, piv=True)[0:3]
        rot = cmds.xform(self.connectors['root'][0], q=True, ws=True, ro=True)
        joint = cmds.joint(n='{}_{}'.format(self.name[0], mCore.universal_suffix[-1]), p=self.position)
        cmds.xform(joint, ro=tuple(rot), ws=True)
        cmds.makeIdentity(joint, a=True, r=True)
        if self.side == 'Right':
            cmds.setAttr('{}.rotateX'.format(joint), 180)
            cmds.makeIdentity(joint, a=True, r=True)
        self.main.append(joint)
        self.connectors['root'].append(joint)

    def set_proxy(self):
        if not self.init_position:
            self.init_position = [0, 0, 0]

        proxy = mCore.curve.gimbal('{}_pxy'.format(self.name[0]))
        cmds.move(rd(self.init_position[0] + 2, self.init_position[0]), rd(self.init_position[1] + 2, self.init_position[1]),
                  rd(self.init_position[2], self.init_position[2]), proxy)

        cmds.select(cl=True)
        self.connectors['root'].append(proxy)

    def set_ik(self):
        self.set_fk()

    def set_fk(self):
        ctr = mCore.Control()

        ctr.zero_out(['null', 'diamond'], ['hrc', 'ctr'], [self.main[0]])
        ctr.toggle_control()
        group = cmds.listRelatives(ctr.group[0], p=True)[0]
        if self.side == 'Right':
            cmds.setAttr('{}.scale'.format(group), -1, -1, -1)
        ctr.constraint()
        mCore.curve.color(self.color[self.side])

        self.self_inner = group
        final_ctr = ctr.group[0]
        if final_ctr[0] == '|':
            final_ctr = final_ctr[1:]
        self.connectors['root'].append(final_ctr)

    def set_ik_fk(self):
        self.set_fk()
