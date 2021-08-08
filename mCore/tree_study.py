import sys

from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMayaUI as omui


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    if sys.version_info.major >= 3:
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)
    else:
        return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class RigUI(QtWidgets.QDialog):

    WINDOW_TITLE = "AutoRig Esposito"

    def __init__(self, parent=maya_main_window()):
        super(RigUI, self).__init__(parent)

        self.setWindowTitle(self.WINDOW_TITLE)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(QtCore.Qt.Tool)

        self.setMinimumWidth(300)

        self.parameter = {'name': None, 'order': None, 'side': None, 'type': None, 'module': None}
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

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        main_layout.addLayout(name_field)
        main_layout.addLayout(order_field)
        main_layout.addLayout(side_radio)
        main_layout.addLayout(type_radio)
        main_layout.addLayout(modules_layout)
        main_layout.addWidget(self.tree_widget)

    def create_connections(self):
        self.name_field.textChanged.connect(self.update_name)
        self.order_field.textChanged.connect(self.update_order)
        self.parameter['order'] = self.order_field.text()

        self.side_group.buttonClicked.connect(self.side_radio)
        self.type_group.buttonClicked.connect(self.type_radio)

        self.spine_button.clicked.connect(self.send_spine)
        self.arm_button.clicked.connect(self.send_arm)
        self.leg_button.clicked.connect(self.send_leg)

    def add_module(self, data):
        pass

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
        self.add_module(self.parameter)
        print(self.parameter)

    def send_arm(self):
        self.parameter['module'] = 'Arm'
        self.add_module(self.parameter)
        print(self.parameter)

    def send_leg(self):
        self.parameter['module'] = 'Leg'
        self.add_module(self.parameter)
        print(self.parameter)

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


# if __name__ == "__main__":
#
#     try:
#         rig_esposito.close()  # pylint: disable=E0601
#         rig_esposito.deleteLater()
#     except:
#         pass
#
#     rig_esposito = RigStructure()
#     rig_esposito.show()
