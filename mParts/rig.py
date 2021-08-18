import sys
from mCore import Tree, utility
from . import Spine, Arm, Leg

from PySide2 import QtCore
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.api.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class RigUI(QtWidgets.QDialog):

    WINDOW_TITLE = "AutoRig Esposito"
    ui_instance = None

    @classmethod
    def show_ui(cls):
        if not cls.ui_instance:
            cls.ui_instance = RigUI()

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()
        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(RigUI, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumWidth(300)

        self.parameter = {'name': None, 'order': None, 'side': '', 'type': None, 'module': None}
        self._modules = {}
        self.rig_modules = []
        self.mods = {'Spine': [Spine], 'Arm': [Arm], 'Leg': [Leg]}
        self._objects_tree = Tree()
        self._shapes_tree = Tree()
        self._objects_tree.separator = '|'

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.name_field = QtWidgets.QLineEdit()

        # order field
        self.order_field = QtWidgets.QLineEdit('xyz')
        self.order_field.setMaximumWidth(30)

        # side radio
        self.side_R_radio = QtWidgets.QRadioButton('RIGHT')
        self.side_M_radio = QtWidgets.QRadioButton('CENTER')
        self.side_L_radio = QtWidgets.QRadioButton('LEFT')
        self.side_L_radio.setChecked(True)
        self.side_group = QtWidgets.QButtonGroup()
        self.side_group.addButton(self.side_R_radio, 0)
        self.side_group.addButton(self.side_M_radio, 1)
        self.side_group.addButton(self.side_L_radio, 2)
        self.parameter['side'] = 'Left'

        # type radio
        self.type_ik_radio = QtWidgets.QRadioButton('IK')
        self.type_fk_radio = QtWidgets.QRadioButton('FK')
        self.type_fk_radio.setChecked(True)
        self.type_ikfk_radio = QtWidgets.QRadioButton('IK/FK')
        self.type_group = QtWidgets.QButtonGroup()
        self.type_group.addButton(self.type_ik_radio, 0)
        self.type_group.addButton(self.type_fk_radio, 1)
        self.type_group.addButton(self.type_ikfk_radio, 2)
        self.parameter['type'] = 'FK'

        # spine button
        self.spine_button = QtWidgets.QPushButton('SPINE')
        self.spine_button.setMinimumHeight(40)

        # arm button
        self.arm_button = QtWidgets.QPushButton('ARM')
        self.arm_button.setMinimumHeight(40)

        # leg button
        self.leg_button = QtWidgets.QPushButton('LEG')
        self.leg_button.setMinimumHeight(40)

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setHeaderHidden(True)

        # generate button
        self.generate_button = QtWidgets.QPushButton('GENERATE')

    def create_layout(self):
        name_field = QtWidgets.QFormLayout()
        name_field.addRow('Name:', self.name_field)

        order_field = QtWidgets.QFormLayout()
        order_field.addRow('Rotation Order:', self.order_field)

        side_radio = QtWidgets.QHBoxLayout()
        side_radio.addWidget(self.side_R_radio)
        side_radio.addWidget(self.side_M_radio)
        side_radio.addWidget(self.side_L_radio)

        type_radio = QtWidgets.QHBoxLayout()
        type_radio.addWidget(self.type_ik_radio)
        type_radio.addWidget(self.type_fk_radio)
        type_radio.addWidget(self.type_ikfk_radio)

        modules_layout = QtWidgets.QHBoxLayout()
        modules_layout.addWidget(self.spine_button)
        modules_layout.addWidget(self.arm_button)
        modules_layout.addWidget(self.leg_button)

        tree_layout = QtWidgets.QVBoxLayout()
        tree_layout.addWidget(self.tree_widget)

        generate_layout = QtWidgets.QVBoxLayout()
        generate_layout.addWidget(self.generate_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        main_layout.addLayout(name_field)
        main_layout.addLayout(order_field)
        main_layout.addLayout(side_radio)
        main_layout.addLayout(type_radio)
        main_layout.addLayout(modules_layout)
        main_layout.addWidget(self.tree_widget)
        main_layout.addLayout(generate_layout)

    def create_connections(self):
        self.name_field.textChanged.connect(self.update_name)
        self.order_field.textChanged.connect(self.update_order)
        self.parameter['order'] = self.order_field.text()

        self.side_group.buttonClicked.connect(self.side_radio)
        self.type_group.buttonClicked.connect(self.type_radio)

        self.spine_button.clicked.connect(self.send_spine)
        self.arm_button.clicked.connect(self.send_arm)
        self.leg_button.clicked.connect(self.send_leg)

        self.generate_button.clicked.connect(self.generate_rig)

    def generate_rig(self):
        for node in self.rig_modules:
            node.module.set_main()
            if node.attributes[0] == 'IK':
                node.module.set_ik()
                continue
            if node.attributes[0] == 'FK':
                node.module.set_fk()
                continue

    def check_selection(self):
        selected = om.MGlobal.getActiveSelectionList()
        if selected.length() != 1:
            return True
        obj = cmds.ls(sl=True)[0]
        if obj in self._modules:
            part = utility.manipulate_name(obj, 'query', position=-2)
            return self._modules[obj], part

    def create_module(self, name, module, option):
        if module == 'Spine':
            spine = self.mods['Spine'][option](name=name)
            return spine
        if module == 'Arm':
            arm = self.mods['Arm'][option](name=name)
            return arm
        if module == 'Leg':
            leg = self.mods['Leg'][option](name=name)
            return leg

    def _insert_parent_leaf(self, name, module, selected=None):
        parent = self._shapes_tree.create_node(name)
        parent.attributes.append(self.parameter['name'])
        parent.group_node = True
        short_name = parent.name.split('_')[-1]
        qt_parent = QtWidgets.QTreeWidgetItem([short_name])
        parent.qt_node = qt_parent
        if selected:
            selected[0].module.connectors[selected[-1]][-1].addChild(qt_parent)
        else:
            self.tree_widget.addTopLevelItem(qt_parent)

        child = self._shapes_tree.create_node('{}_{}'.format(parent.name, module))
        qt_child = QtWidgets.QTreeWidgetItem(['{} -> {}'.format(module, self.parameter['type'])])
        child.qt_node = qt_child
        for value in self.parameter.values():
            child.attributes.append(value)
        qt_parent.addChild(qt_child)

        mod_object = self.create_module(child.name, self.parameter['module'], 0)
        if mod_object:
            self.rig_modules.append(child)
            if selected:
                cmds.parent('{}_pxy'.format(mod_object.name[0]), selected[0].module.connectors[selected[-1]][0])
            child.module = mod_object
            for plug in mod_object.connectors:
                self._modules[mod_object.connectors[plug][0]] = child
                qt_plug = QtWidgets.QTreeWidgetItem([plug])
                mod_object.connectors[plug].append(qt_plug)
                qt_child.addChild(qt_plug)

    def _insert_child_leaf(self, name, selected=None):
        parent = self._shapes_tree.create_node(name)
        short_name = parent.name.split('_')[-1]
        qt_parent = QtWidgets.QTreeWidgetItem(['{} -> {}'.format(short_name, self.parameter['type'])])
        parent.qt_node = qt_parent
        if selected:
            selected[0].module.connectors[selected[-1]][-1].addChild(qt_parent)
        else:
            self.tree_widget.addTopLevelItem(qt_parent)
        for value in self.parameter.values():
            parent.attributes.append(value)

        mod_object = self.create_module(parent.name, self.parameter['module'], 0)
        if mod_object:
            self.rig_modules.append(parent)
            if selected:
                cmds.parent('{}_pxy'.format(mod_object.name[0]), selected[0].module.connectors[selected[-1]][0])
            parent.module = mod_object
            for plug in mod_object.connectors:
                self._modules[mod_object.connectors[plug][0]] = parent
                qt_plug = QtWidgets.QTreeWidgetItem([plug])
                mod_object.connectors[plug].append(qt_plug)
                qt_parent.addChild(qt_plug)

    def add_module(self):
        module = '{}{}'.format(self.parameter['side'], self.parameter['module'])
        if self.parameter['side'] == 'Center':
            module = self.parameter['module']
        selected = self.check_selection()
        if not selected:
            return

        if len(self._modules) == 0 or not selected:
            if self.parameter['name']:
                self._insert_parent_leaf(self.parameter['name'], module)
                return
            self._insert_child_leaf(module)
            return

        parent_group = selected[0].parent
        while parent_group.group_node is False:
            parent_group = parent_group.parent

        if self.parameter['name']:
            if parent_group.attributes:
                if parent_group.attributes[0] == self.parameter['name']:
                    self._insert_child_leaf('{}_{}'.format(parent_group.name, module), selected)
                    return
                self._insert_parent_leaf('{}_{}'.format(selected[0].name, self.parameter['name']), module, selected)
                return
            self._insert_parent_leaf('{}_{}'.format(selected[0].name, self.parameter['name']), module, selected)
            return
        self._insert_child_leaf('{}_{}'.format(parent_group.name, module), selected)
        return

    def update_name(self, data):
        self.parameter['name'] = data
        if data == '':
            self.parameter['name'] = None

    def update_order(self, data):
        self.parameter['order'] = data

    def side_radio(self, option):
        temp = ['Right', 'Center', 'Left']
        side = temp[self.side_group.id(option)]
        self.parameter['side'] = side

    def type_radio(self, option):
        temp = ['IK', 'FK', 'IKFK']
        side = temp[self.type_group.id(option)]
        self.parameter['type'] = side

    def send_spine(self):
        self.parameter['module'] = 'Spine'
        self.add_module()

    def send_arm(self):
        self.parameter['module'] = 'Arm'
        self.add_module()

    def send_leg(self):
        self.parameter['module'] = 'Leg'
        self.add_module()

    def refresh_tree_widget(self):
        self.tree_widget.clear()

        top_level_object_names = cmds.ls(assemblies=True)
        for name in top_level_object_names:
            item = self.create_item(name)
            self.tree_widget.addTopLevelItem(item)

    def create_item(self, name):
        item = QtWidgets.QTreeWidgetItem([name])
        self.add_children(item)

        return item

    def add_children(self, item):
        children = cmds.listRelatives(item.text(0), children=True)
        if children:
            for child in children:
                child_item = self.create_item(child)
                item.addChild(child_item)
