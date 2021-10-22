import maya.cmds as cmds
from random import uniform as rd

import mCore


class Arm:
    def __init__(self, objects=None, name=None, position=None, orient=None, side=None):
        self._toggle = False
        self.main = []
        self.init_position = position
        self.init_orient = orient
        self.position = {}
        self.name = mCore.utility.limb_name('Arm', name)
        self.side = side

        self.color = {'Left': 6, 'Right': 13, 'Center': 17}

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None

        self.connectors = {'root': [], 'end': []}  # 'root':[proxy_pxy, qt_node, joint, control]

        if objects is None:
            self.selected = cmds.ls(sl=True, l=True)
        else:
            self.selected = objects
        if len(self.selected) != 3:
            self.set_proxy()
        else:
            self.set_main()

    def _get_position(self):
        arm_key = ['Arm', 'ForeArm', 'Hand']
        for name, obj in zip(arm_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def set_main(self):
        self._get_position()
        self.main = mCore.utility.orient_limbo(self.selected, self.name)
        if self.side == 'Right':
            self.toggle_orient()

    def set_proxy(self):
        multiplier = 1
        if not self.init_position:
            self.init_position = [0, 0, 0]
        if self.side == 'Right':
            multiplier *= -1
        proxy = mCore.curve.pyramid('{}_pxy'.format(self.name[0]))
        root = mCore.curve.proxy('{}_root_pxy'.format(self.name[0]))
        mid = mCore.curve.proxy('{}_mid_pxy'.format(self.name[1]))
        end = mCore.curve.proxy('{}_end_pxy'.format(self.name[2]))
        cmds.move(rd(self.init_position[0] + (5 * multiplier), self.init_position[0]), rd(self.init_position[1] + 10, self.init_position[1] + 5),
                  rd(self.init_position[2], self.init_position[2]), proxy)
        cmds.move(rd(self.init_position[0] + (5 * multiplier), self.init_position[0]), rd(self.init_position[1], self.init_position[1]), rd(self.init_position[2], self.init_position[2]),
                  root)
        cmds.move(rd(self.init_position[0] + (15 * multiplier), self.init_position[0] + (10 * multiplier)), rd(self.init_position[1], self.init_position[1]),
                  rd(self.init_position[2], self.init_position[2]), mid)
        cmds.move(rd(self.init_position[0] + (25 * multiplier), self.init_position[0] + (20 * multiplier)), rd(self.init_position[1], self.init_position[1]),
                  rd(self.init_position[2], self.init_position[2]), end)
        cmds.parent([root, mid, end], proxy)
        cmds.select(cl=True)
        self.selected = [root, mid, end]
        self.connectors['root'].append(root)
        self.connectors['end'].append(end)

    def reset_proxy(self):
        self.selected = cmds.ls(sl=True, l=True)
        cmds.select(cl=True)
        if len(self.selected) is not 3:
            raise ValueError('Please select three objects')

    def reset_main(self):
        arm_key = ['Arm', 'ForeArm', 'Hand']
        count = 0
        try:
            for a in self.selected:
                self.position[arm_key[count]] = cmds.xform(a, q=True, ws=True, t=True)
                count += 1
        except ValueError:
            raise ValueError('Proxy is missing, please reset it')

        cmds.xform(cmds.spaceLocator(p=self.position['ForeArm']), cp=True)
        locator = cmds.ls(sl=True, l=True)
        cmds.select(d=True)

        cmds.parent(self.main[1], self.main[-1], w=True)
        count = 0
        for a in self.main:
            cmds.xform(a, ws=True, t=self.position[arm_key[count]])
            count += 1
        cmds.parent(self.main[-1], self.main[1])
        cmds.parent(self.main[1], self.main[0])

        cmds.joint(self.main[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        # self._orient(locator)
        if self._toggle:
            self.toggle_orient()
            self._toggle = True

    def toggle_orient(self):
        self._toggle = not self._toggle
        temp = []
        for each in self.main:
            temp.append(each.split('|')[-1])
        cmds.parent(temp[1], temp[-1], w=True)
        for a in temp:
            cmds.setAttr('{}.rotateX'.format(a), 180)
        cmds.parent(temp[-1], temp[1])
        cmds.parent(temp[1], temp[0])
        for b in self.main:
            cmds.makeIdentity(b, a=True, t=1, r=1, s=1, n=0)
        cmds.select(cl=True)

    def access(self, element):
        return

    def _pole_vector(self):
        point_a = mCore.utility.create_vector(self.position['Arm'])
        point_b = mCore.utility.create_vector(self.position['ForeArm'])
        point_c = mCore.utility.create_vector(self.position['Hand'])

        vector_ab = point_b - point_a
        vector_ac = point_c - point_a
        ac_normal = vector_ac.normalize()

        proj_length = vector_ab * ac_normal
        proj_vector = (ac_normal * proj_length) + point_a

        vector_pb = point_b - proj_vector
        pb_normal = vector_pb.normalize()
        pole_position = point_b + (pb_normal * vector_ab.length())
        return pole_position

    def _ik(self):
        arm_copy = cmds.listRelatives(cmds.duplicate(self.main[0])[0], ad=True, f=True)
        arm_copy.append(list(filter(None, arm_copy[0].split('|')))[0])
        self.name.sort(reverse=True)
        ik_chain = None
        for jnt, new in zip(arm_copy, self.name):
            ik_chain = cmds.listRelatives(cmds.rename(jnt, '{}_IK'.format(new)), ad=True, f=True)
        self.name.sort()
        ik_chain.append(list(filter(None, ik_chain[0].split('|')))[0])
        ik_chain.sort()

        ctr = mCore.Control()
        ctr.zero_out(['null', 'cube'], ['hrc', 'ctr'], [ik_chain[-1]])
        ctr.toggle_control()
        mCore.curve.color(self.color[self.side])
        hand_ctr = list(ctr.group)[0]

        ctr.zero_out(['null', 'null', 'diamond'], ['hrc', 'srt', 'ctr'], [ik_chain[1]])
        ctr.toggle_control()
        mCore.curve.color(self.color[self.side])
        pole_ctr = list(ctr.group)[0]

        ctr.zero_out(['null'], ['hrc'], [ik_chain[0]])
        ik_chain = list(ctr.new_object)
        temp = cmds.listRelatives(ik_chain, ad=True, f=True)
        temp.sort()
        ik_chain.extend(temp)

        srt_group = list(filter(None, pole_ctr.split('|')[:-1]))
        pole_position = self._pole_vector()
        cmds.move(pole_position.x, pole_position.y, pole_position.z, '|'.join(srt_group), ws=True)

        cluster = mCore.curve.line_between(self.main[1], pole_ctr, self.name[1])

        for copy, main in zip(ik_chain[:-1], self.main[:-1]):
            cmds.parentConstraint(copy, main)
        cmds.parentConstraint(hand_ctr, self.main[-1])

        pre_ik_handle = cmds.ikHandle(sj=ik_chain[0], ee=ik_chain[-1])
        ik_handle = cmds.rename(pre_ik_handle[0], '{}_hdl'.format(self.name[-1]))
        cmds.poleVectorConstraint(pole_ctr, ik_handle)
        cmds.parent(ik_handle, hand_ctr)

        hrc_pole_group = list(filter(None, pole_ctr.split('|')))[0]
        hrc_hand_group = list(filter(None, hand_ctr.split('|')))[0]
        outer_group = cmds.group(hrc_pole_group, hrc_hand_group, cluster, n='{}_grp'.format(self.name[0]))
        cmds.select(cl=True)
        cmds.setAttr('{}.visibility'.format(ik_chain[1]), 0)
        return list(filter(None, ik_chain[0].split('|')))[0], outer_group, ik_chain[0], hand_ctr

    def _fk(self):
        ctr = mCore.Control()
        ctr.zero_out(['null', 'circle'], ['hrc', 'ctr'], self.main)
        ctr.toggle_control()
        mCore.curve.color(self.color[self.side])
        ctr.constraint()

        loc = cmds.group(em=True, n='{}_connect_loc'.format(self.name[0]))
        loc_group = cmds.group(loc, n='{}_connect_hrc'.format(self.name[0]))
        cmds.xform(loc_group, t=self.position['Arm'])

        parent_group = cmds.listRelatives(ctr.group[-1], p=True)[0]
        grp = cmds.group(em=True, r=True, p=parent_group, n='{}_cst'.format(self.name[0]))
        cmds.parent(ctr.group[-1], grp)
        cmds.pointConstraint(loc, grp)

        final_ctr = cmds.listRelatives(grp, f=True)[0]
        if final_ctr[0] == '|':
            final_ctr = final_ctr[1:]
        return loc_group, parent_group, final_ctr, ctr.group[0].split('|')[-1]

    def set_ik(self):
        ik_elements = self._ik()

        self.self_inner = ik_elements[0]
        self.self_outer = ik_elements[1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(ik_elements[2])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(ik_elements[-1])

    def set_fk(self):
        fk_elements = self._fk()

        self.self_inner = fk_elements[0]
        self.self_outer = fk_elements[1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(fk_elements[2])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(fk_elements[-1])

    def set_ik_fk(self):
        ik_elements = self._ik()
        fk_elements = self._fk()

        # root locator, end locator both constraint to ik and fk, it'll go to outer group
        hand_loc = cmds.group(em=True, n='{}_IkFk_loc'.format(self.name[-1]))
        cmds.parentConstraint(ik_elements[-1], hand_loc, w=1)
        cmds.parentConstraint(fk_elements[-1], hand_loc, w=1)

        arm_loc = cmds.group(em=True, n='{}_IkFk_loc'.format(self.name[0]))
        switcher = mCore.curve.knot(name='{}_SwitchIKFK'.format(self.name[0]))
        mCore.curve.color(17)

        direction = 10
        if self.side == 'Right':
            direction *= -1
        cmds.move(0, direction, 0, '{}.cv[*]'.format(cmds.listRelatives(switcher, s=True, f=True)[0]), r=True, os=True, wd=True)
        cmds.addAttr(switcher, ln='IkFk', at='float', dv=0, min=0, max=1, k=True)

        cmds.parentConstraint(ik_elements[2], arm_loc, w=1)
        cmds.parentConstraint(fk_elements[2], arm_loc, w=1)
        cmds.parentConstraint(hand_loc, switcher, w=1)

        constraints = cmds.listRelatives(self.main, arm_loc, hand_loc, f=True, type='parentConstraint')
        remap = cmds.createNode('remapValue', n='{}_remapValue'.format(switcher))
        cmds.setAttr('{}.outputMin'.format(remap), 1)
        cmds.setAttr('{}.outputMax'.format(remap), 0)
        cmds.connectAttr('{}.IkFk'.format(switcher), '{}.inputValue'.format(remap))

        for each in constraints:
            cmds.connectAttr('{}.IkFk'.format(switcher), '{}.{}'.format(each, cmds.listAttr(each, ud=True)[0]))
            cmds.connectAttr('{}.outValue'.format(remap), '{}.{}'.format(each, cmds.listAttr(each, ud=True)[1]))

        cmds.parent(fk_elements[1], hand_loc, arm_loc, switcher, ik_elements[1])
        cmds.parent(fk_elements[0], ik_elements[0])
        mCore.curve.lock_hide_attr(switcher, ['tx', 'ty', 'tz', 'rx', 'ry', 'rz', 'sx', 'sy', 'sz', 'visibility'], 0, 0)

        # visibility = [line, pole vector, ik jnt, hand ctr, fk ctr]
        # cmds.connectAttr('{}.IkFk'.format(switcher), '{}.visibility'.format(ik_elements[0]))
        # cmds.connectAttr('{}.IkFk'.format(switcher), '{}.visibility'.format(ik_elements[-1]))
        #
        # cmds.connectAttr('{}.outValue'.format(remap), '{}.visibility'.format(fk_elements[0]))
        # cmds.connectAttr('{}.outValue'.format(remap), '{}.visibility'.format(fk_elements[-1]))

        self.self_inner = ik_elements[0]
        self.self_outer = ik_elements[1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(arm_loc)

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(hand_loc)

    def _remove_controls(self):
        pass
