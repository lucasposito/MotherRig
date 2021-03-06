from maya import cmds
import mCore


class Hand(object):
    def __init__(self, objects=None, name=None, position=None, side=None):
        self.init_position = position
        self.main = []
        self.side = side
        self.fingers = 0
        self.temp_chain = []
        self.main_proxy_list = []
        self.tool_name = name
        self.fingers_name = []
        self.hand_proxy = None
        self.main_fingers = []

        self.name = [name]
        self.name_temp = mCore.utility.hand_name('Hand', self.tool_name, self.fingers)

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None  # (leaf node, connector)
        self.parent_outer = None

        self.connectors = {'root': [], self.name_temp[-1].split('_')[-1]: []}  # 'root':[proxy_pxy, qt_node, control]
        if objects is None:
            self.connections = cmds.ls(sl=True, l=True)
        else:
            self.connections = objects
        if len(self.connections) != 3:
            self.set_proxy()
        else:
            self.set_main()

    def set_proxy(self, add=True):
        if not add and self.fingers > 0:
            self.fingers = self.fingers - 1

        self.name_temp = mCore.utility.hand_name('Hand', self.tool_name, self.fingers)
        self.connectors[self.name_temp[-1].split('_')[-1]] = []
        self.connections = []

        if add:
            self.fingers_name.append(self.name_temp)
        length_fingers = len(self.main_proxy_list)

        # main_proxy_name = None
        if not self.init_position:
            self.init_position = [0, 0, 0]

        # Proxy name convention
        pos = ['root', 'mid', 'end']

        # Main proxy(Control the other proxies)
        if self.fingers == 0 and not self.hand_proxy:
            self.hand_proxy = mCore.curve.knot(self.tool_name + '_pxy')
            cmds.move(self.init_position[0], self.init_position[1], self.init_position[2], self.hand_proxy)
            self.connectors['root'].append(self.hand_proxy)
        if not self.main_proxy_list:
            main_proxy_name = '{}_aux_pxy'.format(self.name_temp[0])
            self.main_proxy_list.append(main_proxy_name)
            proxy = mCore.curve.pyramid(main_proxy_name)
            cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, self.init_position[2] + 2, proxy)
            self.fingers = self.fingers + 1
            self.next_position = list(self.init_position)
            cmds.parent(proxy, self.hand_proxy)

            # Create proxies with the name convention and in the correct position
            for limb in range(3):

                proxy_name = '{}_pxy'.format(self.name_temp[limb])
                knot = mCore.curve.knot(proxy_name)
                self.connections.append(knot)
                self.main_fingers.append(knot)
                if limb == 0:
                    pass
                    # self.connectors[self.name_temp[0].split('_')[-1]].append(knot)

                # if limb == 1:
                #     mid = knot

                if limb == 2:
                    self.connectors[self.name_temp[-1].split('_')[-1]].append(knot)

                if limb == 0:
                    self.next_position[0] = self.next_position[0] + 2
                cmds.move(self.next_position[0], self.next_position[1], self.next_position[2] + 2, knot)
                self.next_position[0] = self.next_position[0] + 5
                cmds.parent(self.connections[limb], proxy)
            cmds.select(self.hand_proxy)

        elif add:
            if self.fingers == 0:
                self.fingers = 1
            elif self.fingers < 3:
                main_proxy_name = '{}_aux_pxy'.format(self.name_temp[0])
                self.main_proxy_list.append(main_proxy_name)
                proxy = mCore.curve.pyramid(main_proxy_name)
                length_fingers = len(self.main_proxy_list)
                cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2), proxy)
                self.next_position = list(self.init_position)
                cmds.parent(proxy, self.hand_proxy)

                # Create proxies with the name convention and in the correct position
                for limb in range(3):
                    proxy_name = '{}_pxy'.format(self.name_temp[limb])
                    knot = mCore.curve.knot(proxy_name)
                    self.connections.append(knot)
                    self.main_fingers.append(knot)
                    if limb == 0:
                        pass
                        # self.connectors[self.name_temp[0].split('_')[-1]].append(knot)

                    # if limb == 1:
                    #     mid = knot

                    if limb == 2:
                        self.connectors[self.name_temp[-1].split('_')[-1]].append(knot)

                    if limb == 0:
                        self.next_position[0] = self.next_position[0] + 2
                    cmds.move(self.next_position[0], self.next_position[1], 4 - (length_fingers * 2), knot)

                    self.next_position[0] = self.next_position[0] + 5

                    cmds.parent(proxy_name, proxy)
                cmds.select(self.hand_proxy)
                self.fingers = self.fingers + 1

            elif self.fingers < 5:
                main_proxy_name = '{}_aux_pxy'.format(self.name_temp[0])
                self.main_proxy_list.append(main_proxy_name)
                length_fingers = len(self.main_proxy_list)
                proxy = mCore.curve.pyramid(main_proxy_name)
                cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                          proxy)
                self.next_position = list(self.init_position)
                cmds.parent(proxy, self.hand_proxy)

                # Create proxies with the name convention and in the correct position
                for limb in range(3):
                    proxy_name = '{}_pxy'.format(self.name_temp[limb])
                    knot = mCore.curve.knot(proxy_name)
                    self.connections.append(knot)
                    self.main_fingers.append(knot)
                    if limb == 0:
                        pass
                        # self.connectors[self.name_temp[0].split('_')[-1]].append(knot)

                    # if limb == 1:
                    #     mid = knot

                    if limb == 2:
                        self.connectors[self.name_temp[-1].split('_')[-1]].append(knot)

                    if limb == 0:
                        self.next_position[0] = self.next_position[0] + 2
                    cmds.move(self.next_position[0], self.next_position[1], 4 - (length_fingers * 2), knot)

                    self.next_position[0] = self.next_position[0] + 5

                    cmds.parent(proxy_name, proxy)
                if self.fingers == 3:
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 6 - (length_fingers * 2),
                              proxy)
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                              self.main_proxy_list[self.fingers - 1])
                if self.fingers == 4:
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 6 - (length_fingers * 2),
                              proxy)
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                              self.main_proxy_list[self.fingers - 2])
                cmds.select(self.hand_proxy)
                self.fingers = self.fingers + 1

            else:
                main_proxy_name = '{}_aux_pxy'.format(self.name_temp[0])
                self.main_proxy_list.append(main_proxy_name)
                length_fingers = len(self.main_proxy_list)
                proxy = mCore.curve.pyramid(main_proxy_name)
                cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                          proxy)
                self.next_position = list(self.init_position)
                cmds.parent(proxy, self.hand_proxy)

                for limb in range(3):
                    proxy_name = '{}_pxy'.format(self.name_temp[limb])
                    knot = mCore.curve.knot(proxy_name)
                    self.connections.append(knot)
                    self.main_fingers.append(knot)
                    if limb == 0:
                        pass
                        # self.connectors[self.name_temp[0].split('_')[-1]].append(knot)

                    # if limb == 1:
                    #     mid = knot

                    if limb == 2:
                        self.connectors[self.name_temp[-1].split('_')[-1]].append(knot)

                    if limb == 0:
                        self.next_position[0] = self.next_position[0] + 2
                    cmds.move(self.next_position[0], self.next_position[1], 4 - (length_fingers * 2), knot)

                    self.next_position[0] = self.next_position[0] + 5

                    cmds.parent(proxy_name, proxy)
                if self.fingers == 3:
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 6 - (length_fingers * 2),
                              proxy)
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                              self.main_proxy_list[self.fingers - 1])
                if self.fingers == 4:
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 6 - (length_fingers * 2),
                              proxy)
                    cmds.move(self.init_position[0] + 2, self.init_position[1] + 2, 4 - (length_fingers * 2),
                              self.main_proxy_list[self.fingers - 2])
                cmds.select(self.hand_proxy)
                self.fingers = self.fingers + 1
        elif not add and self.fingers > 0:
            self.name_temp = mCore.utility.hand_name('Hand', self.tool_name, self.fingers)

            self.connectors.pop(self.name_temp[-1].split('_')[-1])

            cmds.delete('{}_aux_pxy'.format(self.name_temp[0]))
            self.fingers_name.pop()
            for i in range(3):
                self.main_fingers.pop()
            self.main_proxy_list.pop()
        elif not add and self.fingers == 0:
            self.fingers = 1

    def set_main(self):

        for j in range(self.fingers):
            for i in range(3):
                connections_sum = j * 3 + i
                cmds.select(self.main_fingers[connections_sum])

                joint_temp = cmds.joint(n=(self.fingers_name[j])[i])
                self.temp_chain.append(joint_temp)

            self.main_temp = mCore.utility.orient_limbo(self.temp_chain, self.fingers_name[j])
            self.main.append(self.main_temp)
            self.temp_chain = []
            cmds.select(cl=True)

    def _fk(self, radius=1):
        ctr_to_connect = None
        hrc_fk_list = []
        finger_end_ctr_list = []
        hrc_arm_list = []
        inner_grp = cmds.group(n='{}_grp'.format(self.tool_name), em=True)
        cmds.matchTransform(inner_grp, '{}_pxy'.format(self.tool_name))
        for j in range(self.fingers):
            for i in range(3):
                ctr = cmds.circle(n=self.fingers_name[j][i] + "_ctr", nr=(0, 1, 0), ch=False, r=radius)
                hrc = cmds.group(name=self.fingers_name[j][i] + "_hrc")
                cmds.matchTransform(hrc, self.main[j][i], scale=False)
                cmds.parentConstraint(ctr, self.main[j][i])

                if i == 0:
                    ctr_to_connect = ctr
                else:
                    cmds.parent(hrc, ctr_to_connect)
                    ctr_to_connect = ctr

                if self.side == "Left":
                    cmds.select(ctr)
                    mCore.curve.color(6)
                if self.side == "Right":
                    cmds.select(ctr)
                    mCore.curve.color(13)

            hrc_arm = cmds.ls("{}_hrc".format(self.fingers_name[j][0]))
            hrc_arm_list.append(hrc_arm)
            hrc_fk = cmds.ls('{}_ctr'.format(self.fingers_name[j][0]))[0]
            hrc_fk_list.append(hrc_fk)
            finger_end_ctr = cmds.ls('{}_ctr'.format(self.fingers_name[j][2]))[0]
            finger_end_ctr_list.append(finger_end_ctr)
            cmds.parent(hrc_arm_list[j][0], inner_grp)

        return inner_grp, hrc_fk_list, finger_end_ctr_list, hrc_arm_list

    def set_fk(self):
        _fk_return = self._fk()

        self.self_inner = _fk_return[0]
        self.self_outer = None

        for i in range(self.fingers):
            self.name_temp = mCore.utility.hand_name('Hand', self.tool_name, i)
            if i == 0:
                self.connectors['root'].append([self.main[i][0]])
                self.connectors['root'].append([_fk_return[1][i]])
                self.connectors[self.name_temp[-1].split('_')[-1]].append(self.main[i][-1])
                self.connectors[self.name_temp[-1].split('_')[-1]].append(_fk_return[2][i])
            else:
                self.connectors['root'][-2].append(self.main[i][0])
                self.connectors['root'][-1].append(_fk_return[1][i])
                self.connectors[self.name_temp[-1].split('_')[-1]].append(self.main[i][-1])
                self.connectors[self.name_temp[-1].split('_')[-1]].append(_fk_return[2][i])

    def set_ik(self):
        self.set_fk()

    def set_ik_fk(self):
        self.set_fk()
