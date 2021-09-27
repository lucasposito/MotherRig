from mCore import utility, curve
from maya import cmds
import pymel.core as pm


class Arm(object):
    def __init__(self, objects=None, name=None, position=None):
        self.init_position = position
        self.main = []
        self.temp_chain = []

        self.next_position = [0, 0, 0]
        self.name = utility.limb_name('Arm', name)

        # self.connections = [root, mid, end] proxies

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None

        self.connectors = {'root': [], 'end': []}  # 'root':[proxy_pxy, qt_node, control]

        if objects is None:
            self.connections = cmds.ls(sl=True, l=True)
        else:
            self.connections = objects
        if len(self.connections) != 3:
            self.set_proxy()
        else:
            self.set_main()

    def set_proxy(self):
        # list [] to put root, mid, end proxies
        self.connections = []
        if not self.init_position:
            self.init_position = [0, 0, 0]

        # Proxy name convention
        pos = ['root', 'mid', 'end']

        # Main proxy(Control the other proxies)
        main_proxy_name = '{}_pxy'.format(self.name[0])
        proxy = curve.knot(main_proxy_name)
        cmds.move(self.init_position[0], self.init_position[1] + 5, self.init_position[2], proxy)

        # Create proxies with the name convention and in the correct position
        for limb in range(3):
            proxy_name = '{}_{}_pxy'.format(self.name[limb], pos[limb])
            knot = curve.knot(proxy_name)

            self.connections.append(knot)
            if limb == 0:
                self.connectors['root'].append(knot)

            if limb == 1:
                mid = knot

            if limb == 2:
                self.connectors['end'].append(knot)

            self.next_position = self.init_position
            cmds.move(self.next_position[0], self.next_position[1], self.next_position[2], knot)
            self.next_position[0] = self.next_position[0] + 5
            cmds.parent(self.connections[limb], proxy)

    def set_main(self):
        for i in range(3):
            cmds.select(self.connections[i])
            joint_temp = cmds.joint(n=self.name[i])
            self.temp_chain.append(joint_temp)

        self.main = utility.orient_limbo(self.temp_chain, self.name)

        print(self.main)
        cmds.select(self.temp_chain, r=True)
        cmds.delete(self.temp_chain)
        cmds.select(cl=True)

    def get_pole_vector_position(self, joint_1, joint_2, joint_3, multiplier=2):
        a = joint_1.getTranslation(space="world")
        b = joint_2.getTranslation(space="world")
        c = joint_3.getTranslation(space="world")

        start_to_end = c - a
        start_to_mid = b - a

        dot = start_to_mid * start_to_end

        projection = float(dot) / float(start_to_end.length())

        start_to_end_normalized = start_to_end.normal()

        projection_vector = start_to_end_normalized * projection

        arrow_vector = start_to_mid - projection_vector
        arrow_vector *= multiplier

        pole_vector_position = arrow_vector + b

        return pole_vector_position

    def _ik(self):
        ik_chain = []
        new_joint_chain = "_IK_jnt"

        ik_chain_grp = cmds.group(n=self.name[0] + "_IK_hrc", em=True)
        cmds.matchTransform(ik_chain_grp, self.main[0])
        cmds.select(ik_chain_grp)
        for i in range(3):
            new_joint_name = self.name[i] + new_joint_chain
            ik_joint = cmds.joint(n=new_joint_name, radius=1)
            cmds.matchTransform(new_joint_name, self.main[i])
            cmds.makeIdentity(new_joint_name, a=1, t=0, r=1, s=0)
            ik_chain.append(ik_joint)
            cmds.select(ik_joint)

        # Parent the new Ik joints with the Fk one
        for i in range(2):
            cmds.parentConstraint((self.name[i] + "_IK_jnt"), self.main[i], w=True, mo=False)
        cmds.ikHandle(n=self.name[2] + "_IK_hdl", sol="ikRPsolver", sj=(self.name[0] + "_IK_jnt"),
                      ee=(self.name[2]) + "_IK_jnt")
        # Creating ik Icon
        cube = curve.cube(self.name[2] + '_IK_ctr')
        cube_list = cmds.ls(cube, dag=True)

        # Parent ik control with foot/hand
        zero = cmds.group(name=self.name[2] + "_IK_hrc")
        cmds.matchTransform(zero, self.main[2], pos=True, rot=True)
        cmds.parentConstraint(cube, self.main[2], mo=True)
        cmds.parent(self.name[2] + "_IK_hdl", self.name[2] + "_IK_ctr")

        # Create pole vector
        cone = curve.cone(self.name[1] + "_IK_ctr")
        cone = cmds.ls(sl=True)

        # Create groups pole vector
        cmds.group(name=self.name[1] + "_IK_srt")
        zero_pole = cmds.ls(sl=True)

        offset_pole = cmds.group(name=self.name[1] + "_IK_hrc")

        cmds.matchTransform(offset_pole, self.main[1], pos=True, rot=True)
        cmds.select(self.main[0], self.main[1], self.main[2])

        joint_1, joint_2, joint_3 = pm.selected()

        locator = pm.spaceLocator()
        locator.setTranslation(self.get_pole_vector_position(joint_1, joint_2, joint_3), space="world")
        cmds.select(self.name[2] + "_IK_hdl")
        # cmds.poleVectorConstraint(self.name[1] + "_IK_ctr", (self.name[2] + "_IK_hdl"), w=1)

        pm.matchTransform(offset_pole, locator, pos=True)

        # This code below makes a cycle so i will wait to fix it
        cmds.aimConstraint(self.name[1] + "_IK_jnt", offset_pole, aim=(0, 1, 0), mo=False)
        cmds.aimConstraint(self.name[1] + "_IK_jnt", offset_pole, rm=True)
        cmds.parentConstraint(self.name[1] + "_IK_jnt", zero_pole, st=["x", "y", "z"], sr=["x", "z"])
        cmds.select("{}_parentConstraint1".format(zero_pole[0]))
        cmds.delete(cmds.ls(sl=True))
        cmds.select(self.name[2] + "_IK_hdl")

        cmds.poleVectorConstraint(self.name[1] + "_IK_ctr", (self.name[2] + "_IK_hdl"), w=1)
        pm.delete(locator)

        outer_group = cmds.group(offset_pole, zero, n='{}_grp'.format(self.name[0]))
        cmds.select(cl=True)

        return ik_chain[0], outer_group, cube, ik_chain_grp

    def set_ik(self):
        _ik_return = self._ik()

        self.self_inner = _ik_return[0]
        self.self_outer = _ik_return[1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(_ik_return[0])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(_ik_return[2])

    def _fk(self, radius=1):
        ctr_to_connect = None
        _cst = None
        for i in range(3):
            ctr = cmds.circle(n=self.name[i] + "_ctr", nr=(0, 1, 0), ch=False, r=radius)
            if i == 0:
                _cst = cmds.group(n='{}_cst'.format(self.name[0]))
            hrc = cmds.group(name=self.name[i] + "_hrc")
            cmds.matchTransform(hrc, self.main[i], scale=False)
            cmds.parentConstraint(ctr, self.main[i])
            if i == 0:
                ctr_to_connect = ctr
            else:
                cmds.parent(hrc, ctr_to_connect)
                ctr_to_connect = ctr
        hrc_arm = cmds.ls("{}_hrc".format(self.name[0]))
        connect_loc = cmds.group(em=True, n='{}_connect_loc'.format(self.name[0]))
        connect_hrc = cmds.group(n='{}_connect_hrc'.format(self.name[0]))
        cmds.matchTransform(connect_hrc, self.main[0])
        cmds.pointConstraint(connect_loc, _cst)
        hrc_fk = cmds.ls('{}_ctr'.format(self.name[0]))[0]
        hand_ctr = cmds.ls('{}_ctr'.format(self.name[2]))[0]
        return connect_hrc, hrc_fk, hand_ctr, hrc_arm

    def set_fk(self):
        _fk_return = self._fk()

        self.self_inner = _fk_return[0]
        self.self_outer = _fk_return[-1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(_fk_return[1])

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(_fk_return[2])

    def set_ik_fk(self):
        _fk_return = self._fk()
        _ik_return = self._ik()

        curve.single_arrow(name=self.name[0] + "_SwitchIKFK")
        switch = cmds.ls(sl=True)
        offset_switch = cmds.group(name=self.name[0] + "_SwitchIKFK_OFFSET")
        cmds.xform(self.name[0] + "_SwitchIKFK", translation=(-2, 0, 0), rotation=(180, 0, 90))
        cmds.matchTransform(offset_switch, self.main[2])
        cmds.parentConstraint(self.main[2], offset_switch, mo=False)
        cmds.select(switch)
        add_attribute = cmds.ls(sl=True)
        for i in add_attribute:
            cmds.addAttr(i, ln="IKFK", at="float", min=0, max=1, dv=0)
            cmds.setAttr(i + ".IKFK", e=True, k=True)
        cmds.select(cl=True)

        # Add Nodes to swicht constraints and visibility
        shape_arm_fk = []
        for i in range(3):
            shape_arm_fk.append(cmds.ls(self.name[i] + "_ctrShape")[0])
        reverse = cmds.shadingNode("reverse", au=True, n=self.name[0] + "_reverse")
        cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                         (self.name[0] + "_reverse.input.inputX"), f=True)
        for i in range(3):
            cmds.connectAttr((self.name[0] + "_reverse.output.outputX"),
                             "{}.visibility".format(shape_arm_fk[i]), f=True)

        cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                         (self.name[1] + "_IK_ctrShape.visibility"), f=True)
        cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                         (self.name[2] + "_IK_ctrShape.visibility"), f=True)

        for i in range(3):

            if i >= 2:
                # Switch Fk Ik

                get_constraint = \
                    cmds.listConnections(self.name[2] + "_IK_ctr", type="parentConstraint")[0]
                get_weights = cmds.parentConstraint(get_constraint, q=True, wal=True)

                cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                                 (get_constraint + "." + get_weights[1]), f=True)
                cmds.connectAttr((self.name[0] + "_reverse.output.outputX"),
                                 (get_constraint + "." + get_weights[0]), f=True)
            else:
                get_constraint = cmds.listConnections(self.main[i], type="parentConstraint")[0]

                get_weights = cmds.parentConstraint(get_constraint, q=True, wal=True)

                cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                                 (get_constraint + "." + get_weights[1]), f=True)
                cmds.connectAttr((self.name[0] + "_reverse.output.outputX"),
                                 (get_constraint + "." + get_weights[0]), f=True)

        cmds.select(cl=True)
        hand_loc = cmds.group(em=True, n='{}_IkFk_loc'.format(self.name[-1]))
        cmds.parentConstraint(_ik_return[2], hand_loc, w=1)
        cmds.parentConstraint(_fk_return[2], hand_loc, w=1)
        get_constraint = cmds.listConnections('{}_IkFk_loc'.format(self.name[-1]), type="parentConstraint")[0]
        get_weights = cmds.parentConstraint(get_constraint, q=True, wal=True)
        cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                         (get_constraint + "." + get_weights[0]), f=True)
        cmds.connectAttr((self.name[0] + "_reverse.output.outputX"),
                         (get_constraint + "." + get_weights[1]), f=True)

        arm_loc = cmds.group(em=True, n='{}_IkFk_loc'.format(self.name[0]))
        cmds.parentConstraint(_ik_return[0], arm_loc, w=1)
        cmds.parentConstraint(_fk_return[1], arm_loc, w=1)
        get_constraint = cmds.listConnections('{}_IkFk_loc'.format(self.name[0]), type="parentConstraint")[0]
        get_weights = cmds.parentConstraint(get_constraint, q=True, wal=True)
        cmds.connectAttr((self.name[0] + "_SwitchIKFK.IKFK"),
                         (get_constraint + "." + get_weights[0]), f=True)
        cmds.connectAttr((self.name[0] + "_reverse.output.outputX"),
                         (get_constraint + "." + get_weights[1]), f=True)

        cmds.parent(_fk_return[-1], hand_loc, arm_loc, offset_switch, _ik_return[1])
        cmds.parent(_fk_return[0], _ik_return[-1])

        self.self_inner = _ik_return[-1]
        self.self_outer = _ik_return[1]

        self.connectors['root'].append(self.main[0])
        self.connectors['root'].append(arm_loc)

        self.connectors['end'].append(self.main[-1])
        self.connectors['end'].append(hand_loc)

        print(self.connectors)
