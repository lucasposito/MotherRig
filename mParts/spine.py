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

        self.spine_size = 2
        self.name = mCore.utility.chain_name('Spine', name)
        self.side = None

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None

        self.connectors = {'root': [], 'end': [], 'left': [],
                           'right': []}  # 'root':[proxy_pxy, qt_node, joint, control]

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

        vertical_vector = (create_vector(self.position['Neck']) - create_vector(self.position['Hips'])).normal()
        horizontal_vector = (create_vector(self.position['LeftShoulder']) - create_vector(
            self.position['RightShoulder'])).normal()

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
            angle = (2 * math.pi) - angle
            quaternion_v = om.MQuaternion(angle, obj_u)

        quaternion *= quaternion_v

        transform_fn.setObject(obj_dag)
        transform_fn.setRotation(quaternion)

    def _get_position(self):
        spine_key = ['Hips', 'Neck', 'LeftShoulder', 'RightShoulder']
        for name, obj in zip(spine_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def set_main(self):
        self._get_position()
        cmds.select(cl=True)
        self.main.append(
            cmds.joint(n='{}_{}'.format(self.name[0], mCore.universal_suffix[-1]), p=self.position['Hips']))
        self._orient_spine(self.main[0])
        cmds.makeIdentity(r=True, a=True)

        self.main.append(
            cmds.joint(n='{}_{}'.format(self.name[2], mCore.universal_suffix[-1]), p=self.position['Neck']))

        cmds.select(self.main[0], r=True)
        distance = mCore.utility.distance_between([self.main[0], self.main[1]])
        space_between = distance / (self.spine_size + 1)
        index = 1

        for i in range(self.spine_size):
            self.main.append(cmds.joint(n='{}{}_{}'.format(self.name[1], index, mCore.universal_suffix[-1])))
            cmds.setAttr('{}.translateY'.format(cmds.ls(sl=True)[0]), space_between)
            index += 1

        self.main.append(
            cmds.joint(n='{}_{}'.format(self.name[3], mCore.universal_suffix[-1]), p=self.position['LeftShoulder']))
        cmds.select(self.main[-2], r=True)
        self.main.append(
            cmds.joint(n='{}_{}'.format(self.name[-1], mCore.universal_suffix[-1]), p=self.position['RightShoulder'],
                       o=[180, 0, 0]))

        cmds.parent(self.main[1], self.main[-3])
        cmds.select(cl=True)

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
        self.set_fk()

    def set_fk(self):
        cmds.select(self.main[:-2])
        ctr = mCore.Control()
        ctr.zero_out(['null', 'circle'], ['hrc', 'ctr'], cmds.ls(sl=True, l=True))
        ctr.toggle_control()
        mCore.curve.size(2)
        mCore.curve.color(17)

        cmds.parentConstraint(ctr.group[0], self.main[1])
        neck = ctr.group[0]
        del [ctr.group[0], ctr.old_object[0]]
        new = []
        index = 0
        for each in ctr.group:
            curve = mCore.curve.circle(name='{}IK_ctr'.format(each.split('|')[-1][:-3]))
            mCore.curve.color(18)
            cmds.parent(curve, each)
            cmds.setAttr('{}.translate'.format(curve), 0, 0, 0)
            cmds.setAttr('{}.rotate'.format(curve), 0, 0, 0)

            cmds.parentConstraint(curve, ctr.old_object[index])
            new.append(curve)
            index += 1

        left_rotation = cmds.xform(self.main[-2], q=True, ws=True, ro=True)
        left_ctr = mCore.curve.cube('{}_ctr'.format(self.name[-2]))
        mCore.curve.color(6)
        left_hrc = cmds.group(left_ctr, r=True, n='{}_hrc'.format(self.name[-2]))
        cmds.xform(left_hrc, t=self.position['LeftShoulder'])
        cmds.xform(left_hrc, ro=tuple(left_rotation))
        cmds.parentConstraint(left_ctr, self.main[-2])

        right_rotation = cmds.xform(self.main[-1], q=True, ws=True, ro=True)
        right_ctr = mCore.curve.cube('{}_ctr'.format(self.name[-1]))
        mCore.curve.color(13)
        right_hrc = cmds.group(right_ctr, r=True, n='{}_hrc'.format(self.name[-1]))
        cmds.xform(right_hrc, t=self.position['RightShoulder'])
        cmds.xform(right_hrc, ro=tuple(right_rotation))
        cmds.setAttr('{}.scale'.format(right_hrc), -1, -1, -1)
        cmds.parentConstraint(right_ctr, self.main[-1])

        cmds.parent(left_hrc, right_hrc, new[0])
        cmds.select(cl=True)

        self.self_inner = cmds.listRelatives(ctr.group[-1], p=True)

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(new[-1])

        self.connectors['end'].append(self.main[1])
        self.connectors['end'].append(neck)

        self.connectors['left'].append(self.main[-2])
        self.connectors['left'].append(left_ctr)

        self.connectors['right'].append(self.main[-1])
        self.connectors['right'].append(right_ctr)

    def set_ik_fk(self):
        self.set_fk()

    def _remove_controls(self):
        pass
