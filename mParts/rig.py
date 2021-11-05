import sys

import mCore.utility
from mCore import LeafNode, Tree, utility, universal_suffix
from . import Spine, Arm, Leg, Blank, Hand, Foot, QuadArm, QuadLeg, Single
# modules = map(__import__, mother_modules)
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
        return wrapInstance(int(main_window_ptr), QtWidgets.QWidget)


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
        self._proxies = []
        self._toggle = False
        self._qt_items = {}
        self.rig_modules = []
        self.mods = {'Spine': [Spine], 'Arm': [Arm], 'Leg': [Leg], 'Blank': [Blank], 'Hand': [Hand], 'Foot': [Foot],
                     'QuadArm': [QuadArm], 'QuadLeg': [QuadLeg], 'Single': [Single]}
        self.qt_tree = QtWidgets.QTreeWidget()
        self._shapes_tree = Tree()

        self._rig_root = LeafNode()
        self._rig_root.module = Blank('Rig')

        self.create_widgets()
        self.create_layout()
        self.create_connections()

    def create_widgets(self):
        self.name_field = QtWidgets.QLineEdit()

        # order field
        # self.order_field = QtWidgets.QLineEdit('xyz')
        # self.order_field.setMaximumWidth(30)

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

        # arm button
        self.arm_button = QtWidgets.QPushButton('ARM')
        self.arm_button.setMinimumHeight(40)

        # spine button
        self.spine_button = QtWidgets.QPushButton('SPINE')
        self.spine_button.setMinimumHeight(40)

        # leg button
        self.leg_button = QtWidgets.QPushButton('LEG')
        self.leg_button.setMinimumHeight(40)

        self.hand_minus_button = QtWidgets.QPushButton('-')
        self.hand_minus_button.setMinimumHeight(40)
        self.hand_minus_button.setMaximumWidth(20)

        self.hand_button = QtWidgets.QPushButton('HAND')
        self.hand_button.setMinimumHeight(40)

        self.hand_plus_button = QtWidgets.QPushButton('+')
        self.hand_plus_button.setMinimumHeight(40)
        self.hand_plus_button.setMaximumWidth(20)

        self.foot_minus_button = QtWidgets.QPushButton('-')
        self.foot_minus_button.setMinimumHeight(40)
        self.foot_minus_button.setMaximumWidth(20)

        self.foot_button = QtWidgets.QPushButton('FOOT')
        self.foot_button.setMinimumHeight(40)

        self.foot_plus_button = QtWidgets.QPushButton('+')
        self.foot_plus_button.setMinimumHeight(40)
        self.foot_plus_button.setMaximumWidth(20)

        self.quad_arm_button = QtWidgets.QPushButton('QUAD ARM')
        self.quad_arm_button.setMinimumHeight(40)

        self.single_button = QtWidgets.QPushButton('SINGLE')
        self.single_button.setMinimumHeight(40)

        self.quad_leg_button = QtWidgets.QPushButton('QUAD LEG')
        self.quad_leg_button.setMinimumHeight(40)

        self.qt_tree.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)
        self.qt_tree.setHeaderHidden(True)

        # delete button
        self.delete_button = QtWidgets.QPushButton('DELETE')

        # generate button
        self.generate_button = QtWidgets.QPushButton('GENERATE')
        self.generate_button.setMinimumHeight(40)

    def create_layout(self):
        name_field = QtWidgets.QFormLayout()
        name_field.addRow('Name:', self.name_field)

        # order_field = QtWidgets.QFormLayout()
        # order_field.addRow('Rotation Order:', self.order_field)

        side_radio = QtWidgets.QHBoxLayout()
        side_radio.addWidget(self.side_R_radio)
        side_radio.addWidget(self.side_M_radio)
        side_radio.addWidget(self.side_L_radio)

        type_radio = QtWidgets.QHBoxLayout()
        type_radio.addWidget(self.type_ik_radio)
        type_radio.addWidget(self.type_fk_radio)
        type_radio.addWidget(self.type_ikfk_radio)

        modules_layout = QtWidgets.QHBoxLayout()
        modules_layout.addWidget(self.arm_button)
        modules_layout.addWidget(self.spine_button)
        modules_layout.addWidget(self.leg_button)

        modules02_layout = QtWidgets.QHBoxLayout()
        modules02_layout.addWidget(self.hand_minus_button)
        modules02_layout.addWidget(self.hand_button)
        modules02_layout.addWidget(self.hand_plus_button)
        modules02_layout.addWidget(self.single_button)
        modules02_layout.addWidget(self.foot_minus_button)
        modules02_layout.addWidget(self.foot_button)
        modules02_layout.addWidget(self.foot_plus_button)

        modules03_layout = QtWidgets.QHBoxLayout()
        modules03_layout.addWidget(self.quad_arm_button)
        modules03_layout.addWidget(self.quad_leg_button)

        tree_layout = QtWidgets.QVBoxLayout()
        tree_layout.addWidget(self.qt_tree)

        buttons_layout = QtWidgets.QVBoxLayout()
        buttons_layout.addWidget(self.delete_button)
        buttons_layout.addWidget(self.generate_button)

        main_layout = QtWidgets.QVBoxLayout(self)
        main_layout.setContentsMargins(2, 2, 2, 2)
        main_layout.setSpacing(2)

        main_layout.addLayout(name_field)
        # main_layout.addLayout(order_field)
        main_layout.addLayout(side_radio)
        main_layout.addLayout(type_radio)
        main_layout.addLayout(modules_layout)
        main_layout.addLayout(modules02_layout)
        main_layout.addLayout(modules03_layout)
        main_layout.addWidget(self.qt_tree)
        main_layout.addLayout(buttons_layout)

    def create_connections(self):
        self.name_field.textChanged.connect(self.update_name)
        # self.order_field.textChanged.connect(self.update_order)
        # self.parameter['order'] = self.order_field.text()

        self.side_group.buttonClicked.connect(self.side_radio)
        self.type_group.buttonClicked.connect(self.type_radio)

        self.qt_tree.itemSelectionChanged.connect(self.select_items)

        self.spine_button.clicked.connect(self.send_spine)
        self.arm_button.clicked.connect(self.send_arm)
        self.leg_button.clicked.connect(self.send_leg)

        self.hand_minus_button.clicked.connect(self.minus_hand)
        self.hand_button.clicked.connect(self.send_hand)
        self.hand_plus_button.clicked.connect(self.plus_hand)

        self.foot_minus_button.clicked.connect(self.minus_foot)
        self.foot_button.clicked.connect(self.send_foot)
        self.foot_plus_button.clicked.connect(self.plus_foot)

        self.quad_arm_button.clicked.connect(self.send_quad_arm)
        self.quad_leg_button.clicked.connect(self.send_quad_leg)

        self.single_button.clicked.connect(self.send_single)

        self.delete_button.clicked.connect(self.delete)
        self.generate_button.clicked.connect(self._traverse)

    def select_items(self):
        items = self.qt_tree.selectedItems()
        for item in items:
            if item not in self._qt_items:
                if item.parent() in self._qt_items:
                    cmds.select(self._qt_items[item.parent()].module.connectors[item.text(0)][0], r=True)
                    return

    def delete(self):
        if self._toggle:
            return
        item = self.qt_tree.selectedItems()[0]

        if item in self._qt_items:
            if isinstance(self._qt_items[item].module, Blank):
                return

            start_node = item
            if item.parent() in self._qt_items:
                if self._qt_items[item.parent()] and item.parent().childCount() == 1:
                    start_node = item.parent()

            cache = []

            def recursive(node):
                for a in range(node.childCount()):
                    cache.append(node.child(a))
                    recursive(node.child(a))

            for b in range(start_node.childCount()):
                recursive(start_node.child(b))

            if start_node in self._qt_items:
                self._shapes_tree.delete_node(self._qt_items[start_node].name)

            if not start_node.parent():
                self.qt_tree.takeTopLevelItem(self.qt_tree.indexOfTopLevelItem(start_node))
            else:
                start_node.parent().takeChildren()

            proxy = '{}_pxy'.format(self._qt_items[item].module.name[0])
            cmds.select(proxy, r=True)
            cmds.delete()
            if proxy in self._proxies:
                self._proxies.remove(proxy)

    def orient_tip(self, leaf):
        if len(leaf.child_group) == 0:
            return
        for each in leaf.child_group:
            cache = [each[0]]
            first = each[0].right
            while first:
                cache.append(first)
                first = first.right
            for nod in cache:
                if isinstance(nod.module, Hand) or isinstance(nod.module, Foot):
                    if len(nod.module.fingers_name) > 2:
                        temp_group = cmds.group(em=True)
                        parent = nod.module.parent_inner
                        root = cmds.xform(parent[0].module.connectors[parent[-1]][0], q=True, ws=True, t=True)
                        left = cmds.xform('{}_pxy'.format(nod.module.fingers_name[2][0]), q=True, ws=True, t=True)
                        right = cmds.xform('{}_pxy'.format(nod.module.fingers_name[1][0]), q=True, ws=True, t=True)
                        mCore.utility.triad_orient(temp_group, root, left, right)
                        parent[0].module.init_orient = cmds.xform(temp_group, q=True, ws=True, ro=True)
                        cmds.delete(temp_group)
                    break

    def generate_rig(self, element):
        if element in self._qt_items:
            node = self._qt_items[element]
            self.orient_tip(node)
            # detect if arm or leg have
            node.module.set_main()
            # in python 2 the order of the attributes changes
            if node.attributes[-2] == 'IK':
                node.module.set_ik()
            elif node.attributes[-2] == 'FK':
                if isinstance(node.module, Blank) and node.module.parent_inner:
                    node.module.init_position = cmds.xform(
                        node.module.init_position.module.connectors['root'][0], q=True,
                        ws=True, t=True)
                node.module.set_fk()
            elif node.attributes[-2] == 'IKFK':
                node.module.set_ik_fk()
            else:
                return

            if node.module.self_inner and node.module.parent_inner:
                cmds.parent(node.module.self_inner,
                            node.module.parent_inner[0].module.connectors[node.module.parent_inner[-1]][-1])
            if node.module.self_outer and node.module.parent_outer:
                if node.module.parent_outer.module:
                    cmds.parent(node.module.self_outer, node.module.parent_outer.module.connectors['root'][-1])

            if len(node.module.main) != 0:
                parent = node.module.parent_inner
                if parent:
                    if len(parent[0].module.main) != 0:
                        cmds.parent(node.module.connectors['root'][-2], parent[0].module.connectors[parent[-1]][-2])
                        return
                    if parent[0].group_node:
                        group_parent = parent[0].module.parent_inner
                        if group_parent:
                            cmds.parent(node.module.connectors['root'][-2],
                                        group_parent[0].module.connectors[parent[0].module.parent_inner[-1]][-2])
                        return
                    if node.group_node:
                        cmds.parent(node.module.connectors['root'][-2],
                                    node.module.parent_outer.module.connectors['root'][-2])

    def _traverse(self, node=None):
        if not node:
            for pxy in self._proxies:
                cmds.setAttr('{}.visibility'.format(pxy), 0)
            if self._toggle:
                return
            self._toggle = not self._toggle
            cmds.select(cl=True)
            self._rig_root.module.connectors['root'].append(cmds.joint(n='Root_{}'.format(universal_suffix[-1])))
            self._rig_root.module.set_fk()
            cmds.parentConstraint(self._rig_root.module.connectors['root'][-1],
                                  self._rig_root.module.connectors['root'][-2])

            for first in range(self.qt_tree.topLevelItemCount()):
                qt_item = self.qt_tree.topLevelItem(first)
                self.generate_rig(qt_item)
                self._traverse(qt_item)
            return
        for child in range(node.childCount()):
            qt_child = node.child(child)
            self.generate_rig(qt_child)
            self._traverse(qt_child)
        cmds.select(cl=True)

    def check_selection(self):
        selected = om.MGlobal.getActiveSelectionList()
        if selected.length() != 1:
            return True
        obj = cmds.ls(sl=True)[0]
        if obj in self._modules:
            part = utility.manipulate_name(obj, 'query', position=-2)
            return self._modules[obj], part

    def create_module(self, name, module, option):
        if cmds.ls(sl=True):
            pos = cmds.xform(cmds.ls(sl=True), q=True, ws=True, t=True)
        else:
            pos = [0, 0, 0]
        if module == 'Spine':
            spine = self.mods['Spine'][option](name=name, position=pos)
            return spine
        if module == 'Arm':
            arm = self.mods['Arm'][option](name=name, position=pos, side=self.parameter['side'])
            return arm
        if module == 'Leg':
            leg = self.mods['Leg'][option](name=name, position=pos, side=self.parameter['side'])
            return leg
        if module == 'Hand':
            hand = self.mods['Hand'][option](name=name, position=pos)
            return hand
        if module == 'Foot':
            foot = self.mods['Foot'][option](name=name, position=pos)
            return foot
        if module == 'QuadArm':
            quad_arm = self.mods['QuadArm'][option](name=name, position=pos)
            return quad_arm
        if module == 'QuadLeg':
            quad_leg = self.mods['QuadLeg'][option](name=name, position=pos)
            return quad_leg
        if module == 'Single':
            single = self.mods['Single'][option](name=name, position=pos, side=self.parameter['side'])
            return single

    def _insert_parent_leaf(self, name, module, selected=None):
        parent = self._shapes_tree.create_node(name)
        parent.attributes.append('FK')
        parent.attributes.append(self.parameter['name'])
        parent.group_node = True
        short_name = parent.name.split('_')[-1]

        qt_parent = QtWidgets.QTreeWidgetItem([short_name])
        parent.qt_node = qt_parent

        parent.module = Blank(parent.name)
        self._qt_items[qt_parent] = parent

        if selected:
            parent.module.parent_inner = selected
            selected[0].module.connectors[selected[-1]][-1].addChild(qt_parent)
        else:

            parent.module.parent_inner = (self._rig_root, 'root')
            parent.module.parent_outer = parent.module.self_outer
            self.qt_tree.addTopLevelItem(qt_parent)

        child = self._shapes_tree.create_node('{}_{}'.format(parent.name, module))
        qt_child = QtWidgets.QTreeWidgetItem(['{} -> {}'.format(module, self.parameter['type'])])
        parent.module.init_position = child
        child.qt_node = qt_child
        self._qt_items[qt_child] = child
        for value in self.parameter.values():
            child.attributes.append(value)
        qt_parent.addChild(qt_child)

        mod_object = self.create_module(child.name, self.parameter['module'], 0)
        mod_object.side = self.parameter['side']
        if mod_object:
            mod_object.parent_outer = parent
            self.rig_modules.append(child)
            if selected:
                cmds.parent('{}_pxy'.format(mod_object.name[0]), selected[0].module.connectors[selected[-1]][0])
            else:
                self._proxies.append('{}_pxy'.format(mod_object.name[0]))
            mod_object.parent_inner = (parent, 'root')
            child.module = mod_object
            for plug in mod_object.connectors:
                self._modules[mod_object.connectors[plug][0]] = child
                qt_plug = QtWidgets.QTreeWidgetItem([plug])
                mod_object.connectors[plug].append(qt_plug)
                qt_child.addChild(qt_plug)
        self.qt_tree.expandAll()

    def _insert_child_leaf(self, name, selected=None):
        group = None
        str_name = name
        if not isinstance(name, str):
            group = name[0]
            str_name = '{}_{}'.format(name[0].name, name[-1])

        parent = self._shapes_tree.create_node(str_name)
        short_name = parent.name.split('_')[-1]
        qt_parent = QtWidgets.QTreeWidgetItem(['{} -> {}'.format(short_name, self.parameter['type'])])
        parent.qt_node = qt_parent
        self._qt_items[qt_parent] = parent
        if selected:
            selected[0].module.connectors[selected[-1]][-1].addChild(qt_parent)
        else:
            self.qt_tree.addTopLevelItem(qt_parent)

        for value in self.parameter.values():
            parent.attributes.append(value)

        mod_object = self.create_module(parent.name, self.parameter['module'], 0)
        mod_object.side = self.parameter['side']
        if mod_object:
            self.rig_modules.append(parent)
            mod_object.parent_outer = group
            if selected:
                cmds.parent('{}_pxy'.format(mod_object.name[0]), selected[0].module.connectors[selected[-1]][0])
                mod_object.parent_inner = selected
            else:
                self._proxies.append('{}_pxy'.format(mod_object.name[0]))
                mod_object.parent_inner = (self._rig_root, 'root')
            parent.module = mod_object
            for plug in mod_object.connectors:
                self._modules[mod_object.connectors[plug][0]] = parent
                qt_plug = QtWidgets.QTreeWidgetItem([plug])
                mod_object.connectors[plug].append(qt_plug)
                qt_parent.addChild(qt_plug)
        self.qt_tree.expandAll()

    def add_module(self):
        if self._toggle:
            return
        module = '{}{}'.format(self.parameter['side'], self.parameter['module'])
        if self.parameter['side'] == 'Center':
            module = self.parameter['module']
        selected = self.check_selection()
        if not selected:
            return

        if len(self._modules) == 0 or selected is True:
            if self.parameter['name']:
                self._insert_parent_leaf(self.parameter['name'], module)
                return
            self._insert_parent_leaf(module, module)
            # self._insert_child_leaf(module, nameless=True)
            return

        parent_group = selected[0]
        if parent_group.parent.name != 'Root':
            parent_group = selected[0].parent
        while parent_group.group_node is False:
            parent_group = parent_group.parent

        if self.parameter['name']:
            if parent_group.attributes:
                if parent_group.attributes[-1] == self.parameter['name']:
                    self._insert_child_leaf([parent_group, module], selected)
                    return
                self._insert_parent_leaf('{}_{}'.format(selected[0].name, self.parameter['name']), module, selected)
                return
            self._insert_parent_leaf('{}_{}'.format(selected[0].name, self.parameter['name']), module, selected)
            return
        self._insert_child_leaf([parent_group, module], selected)
        return

    def update_name(self, data):
        self.parameter['name'] = data
        if data == '':
            self.parameter['name'] = None

    # def update_order(self, data):
    #     self.parameter['order'] = data

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

    def minus_hand(self):
        if self._toggle:
            return
        selected = self.check_selection()
        if not isinstance(selected[0].module, Hand):
            return
        selected[0].module.set_proxy(False)

    def send_hand(self):
        self.parameter['module'] = 'Hand'
        self.add_module()

    def plus_hand(self):
        if self._toggle:
            return
        selected = self.check_selection()
        if not isinstance(selected[0].module, Hand):
            return
        selected[0].module.set_proxy()

    def minus_foot(self):
        if self._toggle:
            return
        selected = self.check_selection()
        if not isinstance(selected[0].module, Foot):
            return
        selected[0].module.set_proxy(False)

    def send_foot(self):
        self.parameter['module'] = 'Foot'
        self.add_module()

    def plus_foot(self):
        if self._toggle:
            return
        selected = self.check_selection()
        if not isinstance(selected[0].module, Foot):
            return
        selected[0].module.set_proxy()

    def send_quad_arm(self):
        self.parameter['module'] = 'QuadArm'
        self.add_module()

    def send_quad_leg(self):
        self.parameter['module'] = 'QuadLeg'
        self.add_module()

    def send_single(self):
        self.parameter['module'] = 'Single'
        self.add_module()

    def refresh_tree_widget(self):
        self.qt_tree.clear()

        top_level_object_names = cmds.ls(assemblies=True)
        for name in top_level_object_names:
            item = self.create_item(name)
            self.qt_tree.addTopLevelItem(item)

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
