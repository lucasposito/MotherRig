import maya.OpenMayaUI as omui
import mParts
import re
from PySide2 import QtWidgets
from PySide2 import QtCore
from shiboken2 import wrapInstance


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QWidget)


class ControlUI(QtWidgets.QDialog):

    ui_instance = None

    @classmethod
    def show_ui(cls):
        if not cls.ui_instance:
            cls.ui_instance = ControlUI()

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()
        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()

    def __init__(self, parent=maya_main_window()):
        super(ControlUI, self).__init__(parent)

        self.setWindowTitle("Zero Out Control")
        self.control = mParts.Control()
        self.width = 280
        self.setFixedSize(self.width + 10, 180)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.width)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        self.shape_field = QtWidgets.QLineEdit()
        self.shape_field.setMinimumWidth(140)

        self.suffix_field = QtWidgets.QLineEdit()
        self.suffix_field.setMinimumWidth(140)

        # generate button
        self.zero_out_button = QtWidgets.QPushButton('ZERO OUT')
        self.zero_out_button.setMinimumWidth(self.width - 20)
        self.zero_out_button.setMinimumHeight(40)

    def create_layouts(self):
        shape_layout = QtWidgets.QFormLayout()
        shape_layout.addRow('SHAPE', self.shape_field)

        suffix_layout = QtWidgets.QFormLayout()
        suffix_layout.addRow('SUFFIX', self.suffix_field)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(self.zero_out_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(shape_layout)
        main_layout.addLayout(suffix_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.zero_out_button.clicked.connect(self._zero_out)

    def _zero_out(self):
        pre_shape = self.shape_field.text()
        shape = re.split(', |,', pre_shape)

        pre_suffix = self.suffix_field.text()
        suffix = re.split(', |,', pre_suffix)

        self.control.zero_out(shape, suffix)
