from PySide2 import QtCore
from PySide2 import QtGui
from PySide2 import QtWidgets
from shiboken2 import wrapInstance

import maya.cmds as cmds
import maya.OpenMaya as om
import maya.OpenMayaUI as omui


def maya_window():
    main_window = omui.MQtUtil.mainWindow()
    return wrapInstance(int(main_window), QtWidgets.QWidget)


class ImportAnimation(QtWidgets.QDialog):
    FILE_FILTER = 'Mobu (*.fbx)'
    selected_filter = 'Mobu (*.fbx)'
    ui_instance = None

    @classmethod
    def show_ui(cls):
        if not cls.ui_instance:
            cls.ui_instance = ImportAnimation()

        if cls.ui_instance.isHidden():
            cls.ui_instance.show()
        else:
            cls.ui_instance.raise_()
            cls.ui_instance.activateWindow()

    def __init__(self, parent=maya_window()):
        super(ImportAnimation, self).__init__(parent)

        self.setWindowTitle('Import FBX Animation')
        self.setFixedSize(300, 120)
        self.setWindowFlags(self.windowFlags() ^ QtCore.Qt.WindowContextHelpButtonHint)

        self.start_frame = int(cmds.playbackOptions(q=True, minTime=True))
        self.end_frame = int(cmds.playbackOptions(q=True, maxTime=True))

        self.imported_namespace = None
        self.target_namespace = None
        self.imported_hierarchy = None
        self.control_suffix = 'ctr'

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.file_path = QtWidgets.QLineEdit()
        self.import_button = QtWidgets.QPushButton()
        self.import_button.setIcon(QtGui.QIcon(':fileOpen.png'))
        self.import_button.setToolTip('Select File')

        self.message = QtWidgets.QLabel('Now select one of the target\'s controllers')

        self.start_frame_field = QtWidgets.QLineEdit(str(self.start_frame))
        self.start_frame_field.setMaximumWidth(80)
        self.end_frame_field = QtWidgets.QLineEdit(str(self.end_frame))
        self.end_frame_field.setMaximumWidth(80)

        self.open_button = QtWidgets.QPushButton('Open')
        self.cancel_button = QtWidgets.QPushButton('Cancel')

    def create_layout(self):
        file_path_layout = QtWidgets.QHBoxLayout()
        file_path_layout.addWidget(self.file_path)
        file_path_layout.addWidget(self.import_button)

        form_layout = QtWidgets.QFormLayout()
        form_layout.addRow('File:', file_path_layout)

        message_layout = QtWidgets.QHBoxLayout()
        message_layout.addWidget(self.message)

        frame_layout = QtWidgets.QHBoxLayout()
        frame_layout.addWidget(self.start_frame_field)
        frame_layout.addWidget(self.end_frame_field)

        button_layout = QtWidgets.QHBoxLayout()
        button_layout.addWidget(self.cancel_button)
        button_layout.addWidget(self.open_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.addLayout(form_layout)
        main_layout.addLayout(message_layout)
        main_layout.addLayout(frame_layout)
        main_layout.addLayout(button_layout)

    def create_connections(self):
        self.file_path.textChanged.connect(self.set_message_visibility)
        self.import_button.clicked.connect(self.show_file_dialog)
        self.message.setVisible(False)
        self.open_button.clicked.connect(self.reference_file)
        self.cancel_button.clicked.connect(self.close)

    def set_message_visibility(self):
        if self.file_path.text() == '':
            self.message.setVisible(False)
            return
        self.message.setVisible(True)

    def show_file_dialog(self):
        file_path, self.selected_filter = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File', '',
                                                                                self.FILE_FILTER, self.selected_filter)
        if file_path:
            self.file_path.setText(file_path)
        self.set_message_visibility()

    def copy_key_frames(self):
        controllers = []

        for each_joint in self.imported_hierarchy:
            try:
                cmds.parentConstraint('{0}:{1}'.format(self.imported_namespace, each_joint),
                                      '{0}:{1}_{2}'.format(self.target_namespace, each_joint, self.control_suffix))
                controllers.append('{0}:{1}_{2}'.format(self.target_namespace, each_joint, self.control_suffix))
            except ValueError:
                pass

        cmds.bakeResults(controllers, t=(self.start_frame_field.text(), self.end_frame_field.text()), dic=False, preserveOutsideKeys=True,
                         simulation=True, sr=[True, 5.0])
        cmds.delete(controllers, sc=True, cn=True)

    def reference_file(self):
        file_path = self.file_path.text()
        if not file_path:
            return

        file_info = QtCore.QFileInfo(file_path)
        if not file_info.exists():
            om.MGlobal.displayError('File does not exist: {}'.format(file_path))
            return

        selected_namespace = cmds.ls(sl=True, sns=True)
        if not len(selected_namespace) == 2:
            return

        self.target_namespace = selected_namespace[-1]

        temp = file_info.baseName()
        old_n_spaces = cmds.namespaceInfo(':', lon=True)

        cmds.file(file_path, reference=True, ignoreVersion=True, namespace=temp)

        new_n_spaces = cmds.namespaceInfo(':', lon=True)
        self.imported_namespace = list(set(new_n_spaces).difference(old_n_spaces))[0]

        temp_2 = cmds.ls(cmds.namespaceInfo(self.imported_namespace, ls=True), type='joint')
        self.imported_hierarchy = [i.split(':')[1] for i in temp_2]

        self.copy_key_frames()
        cmds.file(file_path, rr=True)
