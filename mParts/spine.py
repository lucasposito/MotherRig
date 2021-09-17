import maya.cmds as cmds
import maya.OpenMaya as om

import mCore
import math
from random import uniform as rd


class Spine:
    def __init__(self, proxies=None, name=None, position=None):
        self.main = []
        self.init_position = position
        self.position = {}
        self.proxy_suffix = 'pxy'

        self.name = mCore.utility.chain_name('Spine', name)

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None

        self.connectors = {'root': [], 'end': [], 'left': [], 'right': []}  # 'root':[proxy_pxy, qt_node, joint, control]

        if proxies is None:
            self.set_proxy()
        else:
            self.selected = proxies
            if len(self.selected) != 4:
                raise ValueError('Please provide four proxies')
            self.set_main()

    def _orient_spine(self, obj):
        def create_vector(pos):
            vector = om.MVector(pos[0], pos[1], pos[2])
            return vector

        obj_dag = om.MDagPath()
        sel_list = om.MSelectionList()
        sel_list.add(obj)
        sel_list.getDagPath(0, obj_dag)

        transform_fn = om.MFnTransform(obj_dag)

        vertical_axis = om.MVector().yAxis
        horizontal_axis = om.MVector().xAxis

        vertical_vector = (create_vector(self.position['Spine']) - create_vector(self.position['Hips'])).normal()
        horizontal_vector = (create_vector(self.position['LeftShoulder']) - create_vector(self.position['RightShoulder'])).normal()

        obj_u = vertical_vector.normal()

        obj_v = horizontal_vector
        obj_w = (obj_u ^ obj_v).normal()

        obj_v = obj_w ^ obj_u

        quaternion_u = om.MQuaternion(vertical_axis, obj_u)
        quaternion = quaternion_u

        sec_axis_rotated = horizontal_axis.rotateBy(quaternion)

        angle = math.acos(sec_axis_rotated * obj_v)
        quaternion_v = om.MQuaternion(angle, obj_u)

        if not obj_v.isEquivalent(sec_axis_rotated.rotateBy(quaternion_v), 1.0e-5):
            angle = (2*math.pi) - angle
            quaternion_v = om.MQuaternion(angle, obj_u)

        quaternion *= quaternion_v

        transform_fn.setObject(obj_dag)
        transform_fn.setRotation(quaternion)

    def _get_position(self):
        spine_key = ['Hips', 'Spine', 'LeftShoulder', 'RightShoulder']
        for name, obj in zip(spine_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def set_main(self):
        self._get_position()
        cmds.select(d=True)
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[0], mCore.universal_suffix[-1]), p=self.position['Hips']))
        self._orient_spine(self.main[0])
        cmds.makeIdentity(r=True, a=True)

        self.main.append(cmds.joint(n='{}_{}'.format(self.name[1], mCore.universal_suffix[-1]), p=self.position['Spine']))

        cmds.setAttr('%s.jointOrient' % self.main[-1], 0, 0, 0)
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[2], mCore.universal_suffix[-1]), p=self.position['LeftShoulder']))
        self.main.append(cmds.joint(n='{}_{}'.format(self.name[-1], mCore.universal_suffix[-1]), p=self.position['RightShoulder']))
        cmds.parent(self.main[-1], self.main[1])
        cmds.select(d=True)

    def set_proxy(self):
        if not self.init_position:
            self.init_position = [0, 0, 0]
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
        self.connectors['root'].append(root)
        self.connectors['end'].append(end)
        self.connectors['left'].append(left)
        self.connectors['right'].append(right)

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
