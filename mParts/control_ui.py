import maya.OpenMayaUI as omui
import mCore
import re
import mIcon
from PySide2 import QtWidgets
from PySide2 import QtCore
from PySide2 import QtGui
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
        self.control = mCore.Control()
        self.width = 500
        self.setFixedSize(self.width + 10, 200)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)
        self.setMinimumWidth(self.width)

        self.create_widgets()
        self.create_layouts()
        self.create_connections()

    def create_widgets(self):
        # -------LEFT SIDE------- #
        self.shape_field = QtWidgets.QLineEdit()
        self.shape_field.setMinimumWidth(140)

        self.suffix_field = QtWidgets.QLineEdit()
        self.suffix_field.setMinimumWidth(140)

        # toggle button
        self.toggle_button = QtWidgets.QPushButton('TOGGLE CONTROLS')
        self.toggle_button.setMinimumHeight(20)

        # constraint buttons
        self.parent_button = QtWidgets.QPushButton('PARENT')
        self.point_button = QtWidgets.QPushButton('POINT')
        self.orient_button = QtWidgets.QPushButton('ORIENT')
        self.scale_button = QtWidgets.QPushButton('SCALE')

        # generate button
        self.zero_out_button = QtWidgets.QPushButton('ZERO OUT')
        self.zero_out_button.setMinimumHeight(40)

        # -------RIGHT SIDE------- #
        size = 40
        self.circle_button = QtWidgets.QPushButton()
        self.circle_button.setMaximumWidth(size)
        self.circle_button.setMaximumHeight(size)
        self.circle_button.setStyleSheet('background-image: url(:circle.png)')
        self.circle_button.setToolTip('circle')

        self.drop_button = QtWidgets.QPushButton()
        self.drop_button.setMaximumWidth(size)
        self.drop_button.setMaximumHeight(size)
        self.drop_button.setStyleSheet('background-image: url(:cone.png)')
        self.drop_button.setToolTip('drop')

        self.diamond_button = QtWidgets.QPushButton()
        self.diamond_button.setMaximumWidth(size)
        self.diamond_button.setMaximumHeight(size)
        self.diamond_button.setStyleSheet('background-image: url(:polyPlatonic.png)')
        self.diamond_button.setToolTip('diamond')

        self.knot_button = QtWidgets.QPushButton()
        self.knot_button.setMaximumWidth(size)
        self.knot_button.setMaximumHeight(size)
        self.knot_button.setStyleSheet('background-image: url(:sphere.png)')
        self.knot_button.setToolTip('knot')

        self.square_button = QtWidgets.QPushButton()
        self.square_button.setMaximumWidth(size)
        self.square_button.setMaximumHeight(size)
        self.square_button.setStyleSheet('background-image: url(:square.png)')
        self.square_button.setToolTip('square')

        self.star_button = QtWidgets.QPushButton()
        self.star_button.setMaximumWidth(size)
        self.star_button.setMaximumHeight(size)
        self.star_button.setStyleSheet('background-image: url(:polySuperEllipse.png)')
        self.star_button.setToolTip('star')

        self.quadarrow_button = QtWidgets.QPushButton()
        self.quadarrow_button.setMaximumWidth(size)
        self.quadarrow_button.setMaximumHeight(size)
        self.quadarrow_button.setStyleSheet('background-image: url(:move_M.png)')
        self.quadarrow_button.setToolTip('quad_arrow')

        self.cube_button = QtWidgets.QPushButton()
        self.cube_button.setMaximumWidth(size)
        self.cube_button.setMaximumHeight(size)
        self.cube_button.setStyleSheet('background-image: url(:cube.png)')
        self.cube_button.setToolTip('cube')

        self.color_1_button = QtWidgets.QPushButton()
        self.color_1_button.setStyleSheet('background-color: #2b2b2b')
        self.color_2_button = QtWidgets.QPushButton()
        self.color_2_button.setStyleSheet('background-color: #999999')
        self.color_3_button = QtWidgets.QPushButton()
        self.color_3_button.setStyleSheet('background-color: #0000ff')
        self.color_4_button = QtWidgets.QPushButton()
        self.color_4_button.setStyleSheet('background-color: #ff0000')
        self.color_5_button = QtWidgets.QPushButton()
        self.color_5_button.setStyleSheet('background-color: #ffff00')
        self.color_6_button = QtWidgets.QPushButton()
        self.color_6_button.setStyleSheet('background-color: #64dcff')
        self.color_7_button = QtWidgets.QPushButton()
        self.color_7_button.setStyleSheet('background-color: #ffb0b0')
        self.color_8_button = QtWidgets.QPushButton()
        self.color_8_button.setStyleSheet('background-color: #30a15d')

        self.scale_down_button = QtWidgets.QPushButton()
        self.scale_up_button = QtWidgets.QPushButton()

    def create_layouts(self):
        shape_layout = QtWidgets.QFormLayout()
        shape_layout.addRow('SHAPE', self.shape_field)

        suffix_layout = QtWidgets.QFormLayout()
        suffix_layout.addRow('SUFFIX', self.suffix_field)

        toggle_layout = QtWidgets.QHBoxLayout()
        toggle_layout.addWidget(self.toggle_button)

        constraint_layout = QtWidgets.QHBoxLayout()
        constraint_layout.addWidget(self.parent_button)
        constraint_layout.addWidget(self.point_button)
        constraint_layout.addWidget(self.orient_button)
        constraint_layout.addWidget(self.scale_button)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.zero_out_button)

        upper_curve_layout = QtWidgets.QHBoxLayout()
        upper_curve_layout.addWidget(self.circle_button)
        upper_curve_layout.addWidget(self.drop_button)
        upper_curve_layout.addWidget(self.diamond_button)
        upper_curve_layout.addWidget(self.knot_button)

        lower_layout = QtWidgets.QHBoxLayout()
        lower_layout.addWidget(self.square_button)
        lower_layout.addWidget(self.star_button)
        lower_layout.addWidget(self.quadarrow_button)
        lower_layout.addWidget(self.cube_button)

        color_layout = QtWidgets.QHBoxLayout()
        color_layout.addWidget(self.color_1_button)
        color_layout.addWidget(self.color_2_button)
        color_layout.addWidget(self.color_3_button)
        color_layout.addWidget(self.color_4_button)
        color_layout.addWidget(self.color_5_button)
        color_layout.addWidget(self.color_6_button)
        color_layout.addWidget(self.color_7_button)
        color_layout.addWidget(self.color_8_button)

        scale_layout = QtWidgets.QHBoxLayout()
        scale_layout.addWidget(self.scale_down_button)
        scale_layout.addWidget(self.scale_up_button)

        left_layout = QtWidgets.QVBoxLayout()
        left_layout.addLayout(shape_layout)
        left_layout.addLayout(suffix_layout)
        left_layout.addLayout(toggle_layout)
        left_layout.addLayout(constraint_layout)
        left_layout.addLayout(button_layout)

        right_layout = QtWidgets.QVBoxLayout()
        right_layout.addLayout(upper_curve_layout)
        right_layout.addLayout(lower_layout)
        right_layout.addLayout(color_layout)
        right_layout.addLayout(scale_layout)

        main_layout = QtWidgets.QHBoxLayout(self)
        main_layout.addLayout(left_layout)
        main_layout.addLayout(right_layout)

    def create_connections(self):
        self.toggle_button.clicked.connect(self._toggle)
        self.parent_button.clicked.connect(lambda: self._constraint('parent'))
        self.point_button.clicked.connect(lambda: self._constraint('point'))
        self.orient_button.clicked.connect(lambda: self._constraint('orient'))
        self.scale_button.clicked.connect(lambda: self._constraint('scale'))
        self.zero_out_button.clicked.connect(self._zero_out)

        self.circle_button.clicked.connect(lambda: self._curve_shape(0))
        self.drop_button.clicked.connect(lambda: self._curve_shape(1))
        self.diamond_button.clicked.connect(lambda: self._curve_shape(2))
        self.knot_button.clicked.connect(lambda: self._curve_shape(3))
        self.square_button.clicked.connect(lambda: self._curve_shape(4))
        self.star_button.clicked.connect(lambda: self._curve_shape(5))
        self.quadarrow_button.clicked.connect(lambda: self._curve_shape(6))
        self.cube_button.clicked.connect(lambda: self._curve_shape(7))

        self.color_1_button.clicked.connect(lambda: self._curve_color(0))
        self.color_2_button.clicked.connect(lambda: self._curve_color(3))
        self.color_3_button.clicked.connect(lambda: self._curve_color(6))
        self.color_4_button.clicked.connect(lambda: self._curve_color(13))
        self.color_5_button.clicked.connect(lambda: self._curve_color(17))
        self.color_6_button.clicked.connect(lambda: self._curve_color(18))
        self.color_7_button.clicked.connect(lambda: self._curve_color(20))
        self.color_8_button.clicked.connect(lambda: self._curve_color(28))

        self.scale_down_button.clicked.connect(lambda: self._curve_size(0.8))
        self.scale_up_button.clicked.connect(lambda: self._curve_size(1.2))

    def _curve_shape(self, shape):
        if shape == 0:
            mCore.curve.circle()
        elif shape == 1:
            print('drop')
        elif shape == 2:
            mCore.curve.diamond()
        elif shape == 3:
            mCore.curve.knot()
        elif shape == 4:
            print('square')
        elif shape == 5:
            print('star')
        elif shape == 6:
            mCore.curve.quad_arrow()
        elif shape == 7:
            mCore.curve.cube()

    def _curve_color(self, index):
        mCore.curve.curve_color(index)

    def _curve_size(self, index):
        mCore.curve.curve_size(index)

    def _toggle(self):
        self.control.toggle_control()

    def _constraint(self, data):
        self.control.constraint(data)

    def _zero_out(self):
        pre_shape = self.shape_field.text()
        shape = re.split(', |,', pre_shape)

        pre_suffix = self.suffix_field.text()
        suffix = re.split(', |,', pre_suffix)

        self.control.zero_out(shape, suffix)
