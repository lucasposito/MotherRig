from PySide2 import QtWidgets
from PySide2 import QtCore
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

import mCore


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class MotherUI(QtWidgets.QDialog):
    ui_instance = None

    @classmethod
    def show_ui(cls):
        if not cls.ui_instance:
            cls.ui_instance = MotherUI()

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()
        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(MotherUI, self).__init__(parent)
        self.width = 280
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setFixedSize(self.width + 10, 500)
        self.setWindowTitle('Mother Rig')
        self.parameter = {'name': None, 'order': None, 'side': None, 'type': None, 'size': None, 'module': None}
        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # name field
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
        self.parameter['side'] = 2

        # type radio
        self.type_ik_radio = QtWidgets.QRadioButton('IK')
        self.type_fk_radio = QtWidgets.QRadioButton('FK')
        self.type_fk_radio.setChecked(True)
        self.type_ikfk_radio = QtWidgets.QRadioButton('IK/FK')
        self.type_group = QtWidgets.QButtonGroup()
        self.type_group.addButton(self.type_ik_radio, 0)
        self.type_group.addButton(self.type_fk_radio, 1)
        self.type_group.addButton(self.type_ikfk_radio, 2)
        self.parameter['type'] = 1

        # size slider
        self.size_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.size_slider.setMinimum(0)
        self.size_slider.setMaximum(2)

        # spine button
        self.spine_button = QtWidgets.QPushButton('SPINE')
        self.spine_button.setMinimumHeight(40)

        # arm button
        self.arm_button = QtWidgets.QPushButton('ARM')
        self.arm_button.setMinimumHeight(40)

        # leg button
        self.leg_button = QtWidgets.QPushButton('LEG')
        self.leg_button.setMinimumHeight(40)

        # connect button
        self.connect_button = QtWidgets.QPushButton('CONNECT')
        self.connect_button.setMinimumHeight(40)

        # remove button
        self.remove_button = QtWidgets.QPushButton('REMOVE')
        self.remove_button.setMinimumHeight(40)

        # change button
        self.change_button = QtWidgets.QPushButton('CHANGE NAME')
        self.change_button.setMinimumHeight(40)

        # generate button
        self.generate_button = QtWidgets.QPushButton('GENERATE')
        self.generate_button.setMinimumHeight(40)

        # proxy button
        self.proxy_button = QtWidgets.QPushButton('PROXY MODE')
        self.proxy_button.setMinimumHeight(40)

    def create_layouts(self):
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

        slider = QtWidgets.QHBoxLayout()
        slider.addWidget(self.size_slider)

        modules_layout = QtWidgets.QHBoxLayout()
        modules_layout.addWidget(self.spine_button)
        modules_layout.addWidget(self.arm_button)
        modules_layout.addWidget(self.leg_button)

        edit_layout = QtWidgets.QVBoxLayout()
        edit_layout.addWidget(self.connect_button)
        edit_layout.addWidget(self.remove_button)
        edit_layout.addWidget(self.change_button)

        execute_layout = QtWidgets.QVBoxLayout()
        execute_layout.addWidget(self.generate_button)
        execute_layout.addWidget(self.proxy_button)

        # Main Layout ------
        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(name_field)
        main_layout.addLayout(order_field)
        main_layout.addLayout(side_radio)
        main_layout.addLayout(type_radio)
        main_layout.addLayout(slider)
        main_layout.addLayout(modules_layout)
        main_layout.addLayout(edit_layout)
        main_layout.addLayout(execute_layout)

    def create_connections(self):
        self.name_field.textChanged.connect(self.update_name)
        self.order_field.textChanged.connect(self.update_order)
        self.parameter['order'] = self.order_field.text()
        self.side_group.buttonClicked.connect(self.side_radio)
        self.type_group.buttonClicked.connect(self.type_radio)
        self.size_slider.valueChanged.connect(self.update_size)
        self.parameter['size'] = self.size_slider.value()
        self.spine_button.clicked.connect(self.send_spine)
        self.arm_button.clicked.connect(self.send_arm)
        self.leg_button.clicked.connect(self.send_leg)
        self.generate_button.clicked.connect(self.generate_rig)

    def update_name(self, data):
        self.parameter['name'] = data
        if data == '':
            self.parameter['name'] = None

    def update_order(self, data):
        self.parameter['order'] = data

    def side_radio(self, option):
        self.parameter['side'] = self.side_group.id(option)

    def type_radio(self, option):
        self.parameter['type'] = self.type_group.id(option)

    def update_size(self, data):
        self.parameter['size'] = data

    def send_spine(self):
        self.parameter['module'] = 'Spine'
        mCore.rig.create_proxy(self.parameter)

    def send_arm(self):
        self.parameter['module'] = 'Arm'
        mCore.rig.create_proxy(self.parameter)

    def send_leg(self):
        self.parameter['module'] = 'Leg'
        mCore.rig.create_proxy(self.parameter)

    def generate_rig(self):
        mCore.rig.create_rig()
