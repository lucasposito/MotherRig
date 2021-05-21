import maya.cmds as cmds

import mCore


class Arm:
    def __init__(self, objects=None, name=None):
        self._toggle = False
        self.main_arm = []
        self.position = {}
        self.name = name

        if objects is None:
            self.selected = cmds.ls(sl=True, l=True)
        else:
            self.selected = objects
        if len(self.selected) != 3:
            raise ValueError('Please select three objects')
        self.suffix = 'jnt'

        self._get_position()
        self._limb_name()
        self._set_limbo()

    def _limb_name(self):
        index = 0
        if self.name is None:
            self.name = self.selected[0].split('|')[-1]

        for each in reversed(self.name):
            if not each.isdigit():
                break
            index += 1

        if index != 0:
            number = self.name[-index:]
            name = self.name[:-index]
            if name[-3:] == 'Arm':
                name = name[:-3]
            root = '{}Arm{}'.format(name, number)
            mid = '{}ForeArm{}'.format(name, number)
            end = '{}Hand{}'.format(name, number)
            self.name = [root, mid, end]
            return

        if self.name[-3:] == 'Arm':
            self.name = self.name[:-3]

        root = '{}Arm'.format(self.name)
        mid = '{}ForeArm'.format(self.name)
        end = '{}Hand'.format(self.name)
        self.name = [root, mid, end]

    def _get_position(self):
        arm_key = ['Arm', 'ForeArm', 'Hand']
        for name, obj in zip(arm_key, self.selected):
            self.position[name] = cmds.xform(obj, q=True, ws=True, t=True)

    def _set_limbo(self):
        cmds.xform(cmds.spaceLocator(p=self.position['ForeArm']), cp=True)
        locator = cmds.ls(sl=True, l=True)
        cmds.select(d=True)
        self.main_arm.append(cmds.joint(n='{}_{}'.format(self.name[0], self.suffix), p=self.position['Arm']))
        self.main_arm.append(cmds.joint(n='{}_{}'.format(self.name[1], self.suffix), p=self.position['ForeArm']))
        self.main_arm.append(cmds.joint(n='{}_{}'.format(self.name[2], self.suffix), p=self.position['Hand']))
        cmds.joint(self.main_arm[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        self._orient(locator)

    def _orient(self, locator):
        wrist = self.position['Hand']
        for a in self.main_arm:
            cmds.setAttr(a + '.jointOrient', 0, 0, 0)
        cmds.setAttr('{}.preferredAngleX'.format(self.main_arm[1]), 90)
        ik_handle = cmds.ikHandle(sj=self.main_arm[0], ee=self.main_arm[-1])
        cmds.move(wrist[0], wrist[1], wrist[-1], a=True)
        cmds.poleVectorConstraint(locator, ik_handle[0])
        cmds.delete(locator)
        for b in self.main_arm:
            cmds.makeIdentity(b, a=True, t=1, r=1, s=1, n=0)
        cmds.delete()
        cmds.setAttr('{}.preferredAngleX'.format(self.main_arm[1]), 0)

    def reset_proxy(self):
        self.selected = cmds.ls(sl=True, l=True)
        cmds.select(cl=True)
        if len(self.selected) is not 3:
            raise ValueError('Please select three objects')

    def reset_limb(self):
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

        cmds.parent(self.main_arm[1], self.main_arm[-1], w=True)
        count = 0
        for a in self.main_arm:
            cmds.xform(a, ws=True, t=self.position[arm_key[count]])
            count += 1
        cmds.parent(self.main_arm[-1], self.main_arm[1])
        cmds.parent(self.main_arm[1], self.main_arm[0])

        cmds.joint(self.main_arm[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        self._orient(locator)
        if self._toggle:
            self.toggle_orient()
            self._toggle = True

    def toggle_orient(self):
        self._toggle = not self._toggle
        cmds.parent(self.main_arm[1], self.main_arm[-1], w=True)
        for a in self.main_arm:
            cmds.setAttr('{}.rotateX'.format(a), 180)
        cmds.parent(self.main_arm[-1], self.main_arm[1])
        cmds.parent(self.main_arm[1], self.main_arm[0])
        for b in self.main_arm:
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
        pole_position = point_b + (pb_normal * 20)
        return pole_position

    def set_ik(self):
        arm_copy = cmds.listRelatives(cmds.duplicate(self.main_arm[0])[0], ad=True, f=True)
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

        for copy, main in zip(ik_chain[:-1], self.main_arm[:-1]):
            cmds.parentConstraint(copy, main)
        cmds.parentConstraint(hand_ctr, self.main_arm[-1])

        pre_ik_handle = cmds.ikHandle(sj=ik_chain[0], ee=ik_chain[-1])
        ik_handle = cmds.rename(pre_ik_handle[0], '{}_hdl'.format(self.name[-1]))
        cmds.poleVectorConstraint(pole_ctr, ik_handle)
        cmds.parent(ik_handle, hand_ctr)
        cmds.select(cl=True)

    def set_fk(self):
        pass

    def set_ik_fk(self):
        pass

    def _remove_controls(self):
        pass
