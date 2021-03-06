import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui
from mCore import utility
from PySide2 import QtWidgets
from PySide2 import QtCore
from shiboken2 import wrapInstance

'''
Author: Lucas Esposito
'''


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


class IKFK(object):
    def __init__(self):
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

        self.temp_new_mods = []
        self._modules = []
        self.content = {}
        self._selection = {}
        # _modules = ['John_LeftLeg', 'John_RightLeg', 'John_LeftArm', 'John_RightArm']
        # _content = {'John_LeftLeg':['John_LeftFoot', 'John_LeftLeg', 'John_LeftFoot_IK',
        # 'John_LeftKnee_pole'], 'John_RightLeg':['John_RightFoot', 'John_RightLeg', 'John_RightFoot_IK',
        # 'John_RightKnee_pole'], 'John_LeftArm', 'John_RightArm'}

    @property
    def characters(self):
        return self._modules

    @characters.setter
    def characters(self, char):
        self.temp_new_mods = []
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
                if cmds.objExists('{0}_{1}'.format(fk_control, self.suffix)) and cmds.objExists(
                        '{0}_{1}'.format(ik_control, self.suffix)) and fk_control not in self._modules:
                    self._modules.append(fk_control)
                    mod_element = [pre_mod + a for a in temp]
                    self.temp_new_mods.append(fk_control)
                    self.content[fk_control] = mod_element
                    for obj in mod_element:
                        control = '{}_{}'.format(obj, self.suffix)
                        self._selection[control] = fk_control

    def check_selection(self):
        selection = cmds.ls(sl=True)
        selected = []
        mods = []
        for each in selection:
            if each in self._selection:
                selected.append(each)
        if len(selected) != 0:
            for each in selected:
                if self._selection[each] in mods:
                    continue
                mods.append(self._selection[each])
            return mods
        return self._modules

    def match_tip(self, main_object, fk=False):
        if not fk:
            driver = 0
            driven = 3
        else:
            driver = 3
            driven = 0

        utility.quaternion_constrain('{}_{}'.format(self.content[main_object][driver], self.suffix),
                                     '{}_{}'.format(self.content[main_object][driven], self.suffix))

    def _pole_vector(self, root, mid, end):
        point_a = om.MVector(root[0], root[1], root[2])
        point_b = om.MVector(mid[0], mid[1], mid[2])
        point_c = om.MVector(end[0], end[1], end[2])

        vector_ab = point_b - point_a
        vector_ac = point_c - point_a
        ac_normal = vector_ac.normalize()

        proj_length = vector_ab * ac_normal
        proj_vector = (ac_normal * proj_length) + point_a

        vector_pb = point_b - proj_vector
        pb_normal = vector_pb.normalize()
        pole_position = point_b + (pb_normal * vector_ab.length())
        return pole_position.x, pole_position.y, pole_position.z

    def match_ik_to_fk(self, mods=None):
        if not mods:
            mods = self.check_selection()

        for mod in mods:
            # Query FK position
            root = cmds.xform('{0}_{1}'.format(self.content[mod][2], self.suffix), q=True, ws=True, piv=True)[0:3]
            mid = cmds.xform('{0}_{1}'.format(self.content[mod][1], self.suffix), q=True, ws=True, piv=True)[0:3]
            tip = cmds.xform('{0}_{1}'.format(self.content[mod][0], self.suffix), q=True, ws=True, piv=True)[0:3]

            pole = self._pole_vector(root, mid, tip)
            # Move IK to FK
            cmds.move(pole[0], pole[1], pole[2], '{0}_{1}'.format(self.content[mod][4], self.suffix))
            self.match_tip(mod)

    def bake_ik_to_fk(self):
        if len(self._modules) == 0:
            return
        mods = self.check_selection()
        playback_start = self.start_frame
        playback_end = self.end_frame
        timeline = range(int(playback_start), int(playback_end))
        controllers = []
        for a in self.content:
            controllers.append('{0}_{1}'.format(self.content[a][3], self.suffix))
            controllers.append('{0}_{1}'.format(self.content[a][4], self.suffix))
        for frame in timeline:
            cmds.currentTime(frame, edit=True)

            cmds.cutKey(controllers, time=(frame, frame), option="keys")
            self.match_ik_to_fk(mods)
            cmds.setKeyframe(controllers, hi='none', at=['translate', 'rotate'], s=False, t=frame)
        cmds.delete(controllers, sc=True)

    def match_fk_to_ik(self, mods=None):
        if not mods:
            mods = self.check_selection()

        for mod in mods:
            utility.quaternion_constrain('{0}_{1}'.format(self.content[mod][2], self.ik_suffix),
                                         '{0}_{1}'.format(self.content[mod][2], self.suffix))
            utility.quaternion_constrain('{0}_{1}'.format(self.content[mod][1], self.ik_suffix),
                                         '{0}_{1}'.format(self.content[mod][1], self.suffix))
            self.match_tip(mod, fk=True)

    def bake_fk_to_ik(self):
        if len(self._modules) == 0:
            return
        mods = self.check_selection()
        playback_start = self.start_frame
        playback_end = self.end_frame
        timeline = range(int(playback_start), int(playback_end))
        controllers = []
        for a in self.content:
            controllers.append('{0}_{1}'.format(self.content[a][0], self.suffix))
            controllers.append('{0}_{1}'.format(self.content[a][1], self.suffix))
            controllers.append('{0}_{1}'.format(self.content[a][2], self.suffix))
        for frame in timeline:
            cmds.currentTime(frame, edit=True)
            cmds.cutKey(controllers, time=(frame, frame), option="keys")

            self.match_fk_to_ik(mods)
            cmds.setKeyframe(controllers, hi='none', at=['translate', 'rotate'], s=False, t=frame)
        cmds.delete(controllers, sc=True)


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
        self.setMinimumWidth(self.width)
        self.setMaximumWidth(self.width + 10)
        self.setMinimumHeight(self.width)

        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

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

        self.table = QtWidgets.QTableWidget()
        self.table.setColumnCount(1)
        self.table.setHorizontalHeaderLabels(['Modules Detected'])
        header_view = self.table.horizontalHeader()
        header_view.setSectionResizeMode(0, QtWidgets.QHeaderView.Stretch)

        self.custom_button = QtWidgets.QPushButton('CUSTOMIZE')
        self.custom_button.setMaximumWidth(70)
        self.clear_button = QtWidgets.QPushButton('CLEAR')
        self.clear_button.setMaximumWidth(70)

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

        extra_buttons_layout = QtWidgets.QHBoxLayout()
        extra_buttons_layout.addStretch()
        extra_buttons_layout.addWidget(self.custom_button)
        extra_buttons_layout.addWidget(self.clear_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(header_layout)
        main_layout.addWidget(self.table)
        main_layout.addLayout(extra_buttons_layout)
        main_layout.addLayout(frame_layout)
        main_layout.addLayout(match_layout)
        main_layout.addLayout(bake_layout)

    def create_connections(self):
        self.name_field.returnPressed.connect(self.add_character)
        self.separator_field.returnPressed.connect(self.add_character)
        self.add_char_button.clicked.connect(self.add_character)

        self.table.itemSelectionChanged.connect(self.select_items)

        self.clear_button.clicked.connect(self.clear_modules)

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

    def clear_modules(self):
        self.ik_fk.temp_new_mods = []
        self.ik_fk._modules = []
        self.ik_fk.content = {}
        self.ik_fk._selection = {}
        self.table.clear()
        self.table.setRowCount(0)
        self.table.setHorizontalHeaderLabels(['Modules Detected'])

    def select_items(self):
        items = self.table.selectedItems()
        names = []
        for item in items:
            names.append('{}_{}'.format(self.ik_fk.content[item.text()][0], self.ik_fk.suffix))
        cmds.select(names, r=True)

    def add_character(self):
        name = self.name_field.text()
        sep = self.separator_field.text()
        self.ik_fk.separator = sep
        self.ik_fk.characters = name

        for i in range(len(self.ik_fk.temp_new_mods)):
            self.table.insertRow(i)
            self.insert_item(i, 0, self.ik_fk.temp_new_mods[i])

    def insert_item(self, row, column, text):
        item = QtWidgets.QTableWidgetItem(text)
        self.table.setItem(row, column, item)
