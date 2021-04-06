import maya.cmds as cmds


class Arm:
    def __init__(self):
        self.main_arm = []
        self._toggle = False
        self.position = {}
        self.selected = cmds.ls(sl=True, l=True)
        cmds.select(cl=True)
        if len(self.selected) is not 3:
            raise ValueError('Please select three objects')
        self._get_position()
        self._set_limbo()

    def _get_position(self):
        arm_key = ['Arm', 'ForeArm', 'Hand']
        x = 0
        for a in self.selected:
            self.position[arm_key[x]] = cmds.xform(a, q=True, ws=True, t=True)
            x += 1

    def _set_limbo(self):
        cmds.xform(cmds.spaceLocator(p=self.position['ForeArm']), cp=True)
        locator = cmds.ls(sl=True, l=True)
        cmds.select(d=True)
        # name = generate_chainName(Arm)
        self.main_arm.insert(0, cmds.joint(p=self.position['Arm']))
        self.main_arm.insert(1, cmds.joint(p=self.position['ForeArm']))
        self.main_arm.insert(2, cmds.joint(p=self.position['Hand']))
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
        x = 0
        try:
            for a in self.selected:
                self.position[arm_key[x]] = cmds.xform(a, q=True, ws=True, t=True)
                x += 1
        except ValueError:
            raise ValueError('Proxy is missing, please reset it')

        cmds.xform(cmds.spaceLocator(p=self.position['ForeArm']), cp=True)
        locator = cmds.ls(sl=True, l=True)
        cmds.select(d=True)

        cmds.parent(self.main_arm[1], self.main_arm[-1], w=True)
        x = 0
        for a in self.main_arm:
            cmds.xform(a, ws=True, t=self.position[arm_key[x]])
            x += 1
        cmds.parent(self.main_arm[-1], self.main_arm[1])
        cmds.parent(self.main_arm[1], self.main_arm[0])

        cmds.joint(self.main_arm[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)
        self._orient(locator)
        if self._toggle is True:
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
