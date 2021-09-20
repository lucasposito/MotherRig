import maya.cmds as cmds
from random import uniform as rd

import mCore


class Arm:
    def __init__(self, objects=None, name=None, position=None):
        self._toggle = False
        self.main = []
        self.init_position = position
        self.position = {}
        self.name = mCore.utility.limb_name('Arm', name)

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
        cmds.xform(cmds.spaceLocator(p=self.position['ForeArm']), cp=True)
        locator = cmds.ls(sl=True, l=True)
        cmds.select(d=True)
        first = cmds.joint(n='{}_{}'.format(self.name[0], mCore.universal_suffix[-1]), p=self.position['Arm'])
        second = cmds.joint(n='{}_{}'.format(self.name[1], mCore.universal_suffix[-1]), p=self.position['ForeArm'])
        third = cmds.joint(n='{}_{}'.format(self.name[2], mCore.universal_suffix[-1]), p=self.position['Hand'])
        self.main.append(first)
        self.main.append('{}|{}'.format(first, second))
        self.main.append('{}|{}|{}'.format(first, second, third))
        cmds.joint(self.main[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        self._orient(locator)

    def _orient(self, locator):
        wrist = self.position['Hand']
        for a in self.main:
            cmds.setAttr(a + '.jointOrient', 0, 0, 0)
        cmds.setAttr('{}.preferredAngleX'.format(self.main[1]), 90)
        ik_handle = cmds.ikHandle(sj=self.main[0], ee=self.main[-1])
        cmds.move(wrist[0], wrist[1], wrist[-1], a=True)
        cmds.poleVectorConstraint(locator, ik_handle[0])
        cmds.delete(locator)
        for b in self.main:
            cmds.makeIdentity(b, a=True, t=1, r=1, s=1, n=0)
        cmds.delete()
        cmds.setAttr('{}.preferredAngleX'.format(self.main[1]), 0)

    def set_proxy(self):
        if not self.init_position:
            self.init_position = [0, 0, 0]
        proxy = mCore.curve.pyramid('{}_pxy'.format(self.name[0]))
        root = mCore.curve.proxy('{}_root_pxy'.format(self.name[0]))
        mid = mCore.curve.proxy('{}_mid_pxy'.format(self.name[1]))
        end = mCore.curve.proxy('{}_end_pxy'.format(self.name[2]))
        cmds.move(rd(self.init_position[0] + 5, self.init_position[0]), rd(self.init_position[1] + 10, self.init_position[1] + 5),
                  rd(self.init_position[2], self.init_position[2]), proxy)
        cmds.move(rd(self.init_position[0] + 5, self.init_position[0]), rd(self.init_position[1], self.init_position[1]), rd(self.init_position[2], self.init_position[2]),
                  root)
        cmds.move(rd(self.init_position[0] + 15, self.init_position[0] + 10), rd(self.init_position[1], self.init_position[1]),
                  rd(self.init_position[2], self.init_position[2]), mid)
        cmds.move(rd(self.init_position[0] + 25, self.init_position[0] + 20), rd(self.init_position[1], self.init_position[1]),
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
        self._orient(locator)
        if self._toggle:
            self.toggle_orient()
            self._toggle = True

    def toggle_orient(self):
        self._toggle = not self._toggle
        cmds.parent(self.main[1], self.main[-1], w=True)
        for a in self.main:
            cmds.setAttr('{}.rotateX'.format(a), 180)
        cmds.parent(self.main[-1], self.main[1])
        cmds.parent(self.main[1], self.main[0])
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

    def set_ik(self):
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
        hand_ctr = list(ctr.group)[0]

        ctr.zero_out(['null', 'null', 'diamond'], ['hrc', 'srt', 'ctr'], [ik_chain[1]])
        ctr.toggle_control()
        pole_ctr = list(ctr.group)[0]

        ctr.zero_out(['null'], ['hrc'], [ik_chain[0]])
        ik_chain = list(ctr.new_object)
        temp = cmds.listRelatives(ik_chain, ad=True, f=True)
        temp.sort()
        ik_chain.extend(temp)

        srt_group = list(filter(None, pole_ctr.split('|')[:-1]))
        pole_position = self._pole_vector()
        cmds.move(pole_position.x, pole_position.y, pole_position.z, '|'.join(srt_group), ws=True)

        for copy, main in zip(ik_chain[:-1], self.main[:-1]):
            cmds.parentConstraint(copy, main)
        cmds.parentConstraint(hand_ctr, self.main[-1])

        pre_ik_handle = cmds.ikHandle(sj=ik_chain[0], ee=ik_chain[-1])
        ik_handle = cmds.rename(pre_ik_handle[0], '{}_hdl'.format(self.name[-1]))
        cmds.poleVectorConstraint(pole_ctr, ik_handle)
        cmds.parent(ik_handle, hand_ctr)

        hrc_pole_group = list(filter(None, pole_ctr.split('|')))[0]
        hrc_hand_group = list(filter(None, hand_ctr.split('|')))[0]
        outer_group = cmds.group(hrc_pole_group, hrc_hand_group, n='{}_grp'.format(self.name[0]))
        cmds.select(cl=True)

        self.self_inner = list(filter(None, ik_chain[0].split('|')))[0]
        self.self_outer = outer_group

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(ik_chain[0])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(hand_ctr)

    def set_fk(self):
        ctr = mCore.Control()
        ctr.zero_out(['null', 'circle'], ['hrc', 'ctr'], self.main)
        ctr.toggle_control()
        ctr.constraint()

        loc = cmds.group(em=True, n='{}_connect_loc'.format(self.name[0]))
        loc_group = cmds.group(loc, n='{}_connect_hrc'.format(self.name[0]))
        cmds.xform(loc_group, t=self.position['Arm'])

        parent_group = cmds.listRelatives(ctr.group[-1], p=True)[0]
        grp = cmds.group(em=True, r=True, p=parent_group, n='{}_cst'.format(self.name[0]))
        cmds.parent(ctr.group[-1], grp)
        cmds.pointConstraint(loc, grp)

        self.self_inner = loc_group
        self.self_outer = parent_group

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(cmds.listRelatives(grp, f=True)[0])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(ctr.group[0].split('|')[-1])

    def set_ik_fk(self):
        pass

    def _remove_controls(self):
        pass
