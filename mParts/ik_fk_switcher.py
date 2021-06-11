import maya.cmds as cmds
import maya.OpenMayaUI as omui
from PySide2 import QtWidgets
from PySide2 import QtCore
from shiboken2 import wrapInstance


'''
Author: Lucas Esposito

if you need to clear all mParts run the following code on python script editor:

ikfkUI.dialog_instance.ik_fk._modules = []
ikfkUI.dialog_instance.ik_fk._content = {}

'''


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class IKFK(object):
    def __init__(self):
        # Look inside namespaces
        # Working by selection too
        # Name order: Character _ Side + Limb _ Suffix
        self.suffix = 'ctr'
        self.separator = ':'
        self.ik_suffix = 'IK'  # that's for the IK Skeleton, it'll replace ctr suffix
        self.limbs = ['Leg', 'Arm']
        self.side = ['Left', 'Right']

        self.leg_module = ['Foot', 'Leg', 'UpLeg', 'Foot_IK', 'Leg_IK']
        self.arm_module = ['Hand', 'ForeArm', 'Arm', 'Hand_IK', 'ForeArm_IK']

        self.start_frame = None
        self.end_frame = None

        self._modules = []
        self._content = {}
        # mParts = ['John_LeftLeg', 'John_RightLeg', 'John_LeftArm', 'John_RightArm']
        # content = {'John_LeftLeg':['John_LeftFoot', 'John_LeftLeg', 'John_LeftFoot_IK',
        # 'John_LeftKnee_pole'], 'John_RightLeg':['John_RightFoot', 'John_RightLeg', 'John_RightFoot_IK',
        # 'John_RightKnee_pole'], 'John_LeftArm', 'John_RightArm'}

    @property
    def characters(self):
        return self._modules

    @characters.setter
    def characters(self, char):
        for sid in self.side:
            for limb in self.limbs:
                pre_mod = '{0}{1}{2}'.format(char, self.separator, sid)
                fk_control = '{0}{1}{2}{3}'.format(char, self.separator, sid, limb)
                mod_index = self.limbs.index(limb)
                if mod_index is 0:
                    ik_control = '{0}{1}{2}{3}'.format(char, self.separator, sid, self.leg_module[3])
                    temp = self.leg_module
                else:
                    ik_control = '{0}{1}{2}{3}'.format(char, self.separator, sid, self.arm_module[3])
                    temp = self.arm_module
                if cmds.objExists('{0}_{1}'.format(fk_control, self.suffix)) and cmds.objExists('{0}_{1}'.format(ik_control, self.suffix)) and fk_control not in self._modules:
                    self._modules.append(fk_control)
                    mod_element = [pre_mod + a for a in temp]
                    self._content[fk_control] = mod_element

    def check_selection(self):
        selection = cmds.ls(sl=True)
        modules = []
        name = None
        if len(selection) == 0:
            return self._modules
        for each in selection:
            try:
                cache = each.split(self.separator)
                name = '{0}_{1}'.format(cache[0], cache[1])
            except ValueError:
                cache = each.split('_')
                name = cache[0]
            if name in self._modules:
                modules.append(name)
                return modules
        print(modules)
        return self._modules

    def match_tip(self, position, rotation, main_object, fk=False):
        if fk is True:
            driver = 3
            driven = 0
        elif fk is False:
            driver = 0
            driven = 3

        temp_group = cmds.group(em=True)
        cmds.move(position[0], position[1], position[2], temp_group)
        cmds.xform(temp_group, ro=tuple(rotation))
        cmds.parent(temp_group, '{0}_{1}'.format(self._content[main_object][driver], self.suffix))
        cmds.move(10, temp_group, z=True, ls=True)
        temp_aim = cmds.aimConstraint(temp_group, '{0}_{1}'.format(self._content[main_object][driven], self.suffix), w=True, aim=[0, 0, 1], u=[0, 1, 0],
                                      wut='objectrotation', wu=[0, 1, 0], wuo=temp_group)

        if cmds.keyframe('{0}_{1}'.format(self._content[main_object][driven], self.suffix), query=True, at='rotate', vc=True) is not None:
            cmds.setKeyframe('{0}_{1}'.format(self._content[main_object][driven], self.suffix), hi='none', at='rotate', s=False)

        cmds.delete(temp_aim)
        cmds.delete(temp_group)

    def match_ik_to_fk(self):
        self.check_selection()
        for mod in self._modules:
            try:
                # Query FK position
                tip = cmds.xform('{0}_{1}'.format(self._content[mod][0], self.suffix), q=True, ws=True, piv=True)[0:3]
                tip_rotation = cmds.xform('{0}_{1}'.format(self._content[mod][0], self.suffix), q=True, ws=True, ro=True)
                mid = cmds.xform('{0}_{1}'.format(self._content[mod][1], self.suffix), q=True, ws=True, piv=True)[0:3]

                # Move IK to FK
                cmds.move(tip[0], tip[1], tip[2], '{0}_{1}'.format(self._content[mod][3], self.suffix))
                cmds.move(mid[0], mid[1], mid[2], '{0}_{1}'.format(self._content[mod][4], self.suffix))
                self.match_tip(tip, tip_rotation, mod)
            except ValueError:
                print('Module {} has failed'.format(mod))

    def bake_ik_to_fk(self):
        playback_start = self.start_frame
        playback_end = self.end_frame
        timeline = range(int(playback_start), int(playback_end))
        controllers = []
        try:
            for a in self._content:
                controllers.append('{0}_{1}'.format(self._content[a][3], self.suffix))
                controllers.append('{0}_{1}'.format(self._content[a][4], self.suffix))
            for frame in timeline:
                cmds.currentTime(frame, edit=True)

                cmds.cutKey(controllers, time=(frame, frame), option="keys")
                self.match_ik_to_fk()
                cmds.setKeyframe(controllers, hi='none', at=['translate', 'rotate'], s=False, t=frame)
            cmds.delete(controllers, sc=True)
        except ValueError:
            print('Make sure the names of the mParts are correct')
        except KeyboardInterrupt:
            pass

    def match_fk_to_ik(self):
        for mod in self._modules:
            try:
                # Query IK rotation
                root_rot = cmds.getAttr('{0}_{1}.rotate'.format(self._content[mod][2], self.ik_suffix))[0]
                mid_rot = cmds.getAttr('{0}_{1}.rotate'.format(self._content[mod][1], self.ik_suffix))[0]

                tip = cmds.xform('{0}_{1}'.format(self._content[mod][3], self.suffix), q=True, ws=True, piv=True)[0:3]
                tip_rot = cmds.xform('{0}_{1}'.format(self._content[mod][3], self.suffix), q=True, ws=True, ro=True)

                # Rotate FK to IK
                cmds.setAttr('{0}_{1}.rotate'.format(self._content[mod][2], self.suffix), root_rot[0], root_rot[1], root_rot[2])
                cmds.setAttr('{0}_{1}.rotate'.format(self._content[mod][1], self.suffix), mid_rot[0], mid_rot[1], mid_rot[2])
                self.match_tip(tip, tip_rot, mod, fk=True)
            except ValueError:
                print('Module {} has failed'.format(mod))

    def bake_fk_to_ik(self):
        playback_start = self.start_frame
        playback_end = self.end_frame
        timeline = range(int(playback_start), int(playback_end))
        controllers = []
        try:
            for a in self._content:

                controllers.append('{0}_{1}'.format(self._content[a][0], self.suffix))
                controllers.append('{0}_{1}'.format(self._content[a][1], self.suffix))
                controllers.append('{0}_{1}'.format(self._content[a][2], self.suffix))
            for frame in timeline:
                cmds.currentTime(frame, edit=True)
                cmds.cutKey(controllers, time=(frame, frame), option="keys")

                self.match_fk_to_ik()
                cmds.setKeyframe(controllers, hi='none', at=['translate', 'rotate'], s=False, t=frame)
            cmds.delete(controllers, sc=True)
        except ValueError:
            print('Make sure the names of the mParts are correct')


class ikfkUI(QtWidgets.QDialog):

    ui_instance = None

    @classmethod
    def show_ui(cls):
        if not cls.ui_instance:
            cls.ui_instance = ikfkUI()

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()
        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(ikfkUI, self).__init__(parent)

        self.setWindowTitle("IK FK Switcher")
        self.ik_fk = IKFK()
        self.width = 280
        self.setFixedSize(self.width + 10, 180)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.width)

        self.start_frame = int(cmds.playbackOptions(q=True, minTime=True))
        self.ik_fk.start_frame = self.start_frame
        self.end_frame = int(cmds.playbackOptions(q=True, maxTime=True))
        self.ik_fk.end_frame = self.end_frame

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # name field
        self.name_field = QtWidgets.QLineEdit()
        self.name_field.setMinimumWidth(140)

        self.separator_field = QtWidgets.QLineEdit(':')
        self.separator_field.setMaxLength(1)
        self.separator_field.setMaximumWidth(20)

        self.add_char_button = QtWidgets.QPushButton('ADD')
        self.add_char_button.setMaximumWidth(35)
        self.add_char_button.setMinimumHeight(30)

        self.start_frame_field = QtWidgets.QLineEdit(str(self.start_frame))
        self.start_frame_field.setMaximumWidth(60)

        self.end_frame_field = QtWidgets.QLineEdit(str(self.end_frame))
        self.end_frame_field.setMaximumWidth(60)

        # generate button
        self.match_ikfk_button = QtWidgets.QPushButton('SNAP IK TO FK')
        self.match_ikfk_button.setMinimumWidth((self.width - 20) / 2)
        self.match_ikfk_button.setMinimumHeight(40)

        self.match_fkik_button = QtWidgets.QPushButton('SNAP FK TO IK')
        self.match_fkik_button.setMinimumWidth((self.width - 20) / 2)
        self.match_fkik_button.setMinimumHeight(40)

        self.bake_ikfk_button = QtWidgets.QPushButton('IK FOLLOWS FK')
        self.bake_ikfk_button.setMinimumWidth((self.width - 20) / 2)
        self.bake_ikfk_button.setMinimumHeight(40)

        self.bake_fkik_button = QtWidgets.QPushButton('FK FOLLOWS IK')
        self.bake_fkik_button.setMinimumWidth((self.width - 20) / 2)
        self.bake_fkik_button.setMinimumHeight(40)

    def create_layouts(self):
        name_field = QtWidgets.QFormLayout()
        name_field.addRow('Character:', self.name_field)
        separator_field = QtWidgets.QFormLayout()
        separator_field.addRow(self.separator_field)
        add_button_layout = QtWidgets.QHBoxLayout()
        add_button_layout.addWidget(self.add_char_button)

        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.addWidget(self.start_frame_field)
        frame_layout.addWidget(self.end_frame_field)

        match_layout = QtWidgets.QHBoxLayout()
        match_layout.addStretch()
        match_layout.addWidget(self.match_ikfk_button)
        match_layout.addWidget(self.match_fkik_button)

        bake_layout = QtWidgets.QHBoxLayout()
        bake_layout.addStretch()
        bake_layout.addWidget(self.bake_ikfk_button)
        bake_layout.addWidget(self.bake_fkik_button)

        header_layout = QtWidgets.QHBoxLayout()
        header_layout.addLayout(name_field)
        header_layout.addLayout(separator_field)
        header_layout.addLayout(add_button_layout)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(header_layout)
        main_layout.addLayout(frame_layout)
        main_layout.addLayout(match_layout)
        main_layout.addLayout(bake_layout)

    def create_connections(self):
        self.name_field.returnPressed.connect(self.add_character)
        self.separator_field.returnPressed.connect(self.add_character)
        self.add_char_button.clicked.connect(self.add_character)

        self.start_frame_field.textChanged.connect(self.set_start_frame)
        self.end_frame_field.textChanged.connect(self.set_end_frame)

        self.match_ikfk_button.clicked.connect(self.ik_fk.match_ik_to_fk)
        self.match_fkik_button.clicked.connect(self.ik_fk.match_fk_to_ik)
        self.bake_ikfk_button.clicked.connect(self.ik_fk.bake_ik_to_fk)
        self.bake_fkik_button.clicked.connect(self.ik_fk.bake_fk_to_ik)

    def set_start_frame(self):
        self.ik_fk.start_frame = int(self.start_frame_field.text())

    def set_end_frame(self):
        self.ik_fk.end_frame = int(self.end_frame_field.text())

    def add_character(self):
        name = self.name_field.text()
        sep = self.separator_field.text()
        self.ik_fk.separator = sep
        self.ik_fk.characters = name
        print('\n\n--------Detected mParts:--------\n')
        for mod in self.ik_fk.characters:
            print(mod)
        print('\n---------------------------------\n')
