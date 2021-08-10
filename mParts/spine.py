import maya.cmds as cmds

import mCore
from random import uniform as rd


class Spine:
    def __init__(self, proxies=None, name=None):
        self.main = []
        self.position = {}
        self.proxy_suffix = 'pxy'

        self.name = mCore.utility.chain_name('Spine', name)

        self.inner_group = None
        self.outer_group = None

        self.connectors = {'start': None, 'end': None, 'left': None, 'right': None}

        if proxies is None:
            self.set_proxy()
        else:
            self.selected = proxies
            if len(self.selected) != 4:
                raise ValueError('Please provide four proxies')
            self._set_main()

    def _orient_spine(self):
        pass

    def _get_position(self):
        spine_key = ['Hips', 'Spine', 'LeftShoulder', 'RightShoulder']
        for name, obj in zip(spine_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def _set_main(self):
        self._get_position()
        cmds.select(d=True)
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[0], mCore.universal_suffix[-1]), p=self.position['Hips']))
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[1], mCore.universal_suffix[-1]), p=self.position['Spine']))

        cmds.joint(self.main[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        cmds.setAttr('%s.jointOrient' % self.main[-1], 0, 0, 0)

        self.main.append(cmds.joint(n='{}_{}'.format(self.name[2], mCore.universal_suffix[-1]), p=self.position['LeftShoulder']))
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[-1], mCore.universal_suffix[-1]), p=self.position['RightShoulder']))
        cmds.parent(self.main[-1], self.main[1])
        cmds.select(d=True)

    def set_proxy(self):
        proxy = mCore.curve.pyramid('{}_{}'.format(self.name[0], self.proxy_suffix))
        root = mCore.curve.proxy('{}_root_{}'.format(self.name[0], self.proxy_suffix))
        end = mCore.curve.proxy('{}_end_{}'.format(self.name[0], self.proxy_suffix))

        left = mCore.curve.proxy('{}_left_{}'.format(self.name[0], self.proxy_suffix))
        right = mCore.curve.proxy('{}_right_{}'.format(self.name[0], self.proxy_suffix))

        cmds.move(rd(5, 0), rd(10, 5), rd(0, 0), proxy)
        cmds.move(rd(0, 0), rd(5, 0), rd(0, 0), root)
        cmds.move(rd(0, 0), rd(25, 20), rd(0, 0), end)
        cmds.move(rd(10, 5), rd(25, 20), rd(0, 0), left)
        cmds.move(rd(-10, -5), rd(25, 20), rd(0, 0), right)

        cmds.parent([root, end, left, right], proxy)
        self.selected = [root, end, left, right]
        cmds.select(cl=True)

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
