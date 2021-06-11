import maya.cmds as cmds
from random import uniform as rd
import mCore
import mParts

_NEW_RIG_ = None


class Structure(object):
    # That's a tree structure of the rig
    def __init__(self):
        self._objects_tree = mCore.Tree()
        self._shapes_tree = mCore.Tree()

        self._objects_tree.separator = '|'
        self.suffix = 'pxy'
        self.modules = {}

    def _check_selection(self):
        selected = cmds.ls(sl=True)
        if len(selected) is not 1:
            return

        if mCore.utility.manipulate_name(selected[0], 'check', self.suffix, -1) is True:
            new_name = mCore.utility.manipulate_name(selected[0], 'delete', position=-1)
            part_name = None
            for each in ['root', 'mid', 'end']:
                if mCore.utility.manipulate_name(new_name, 'check', each, -1) is True:
                    part_name = each
                    break
            if part_name:
                new_name = mCore.utility.manipulate_name(new_name, 'delete', position=-1)
            node = self._shapes_tree.find_node(new_name)
            if isinstance(node, tuple):
                node = None
            return node, part_name

    def execute(self):
        pass
        # if nothing is selected
        #     rig_root.naming(0)
        #     rig_root.add_node(module, 'Root')
        # else
        #     rig_root.naming(1)
        #     rig_root.add_node(module, selected)

    def move(self):
        # two selected elements
        pass

    def remove(self):
        # remove selected
        pass

    def generate(self):
        # until it's not generated button_proxy_mode is disabled
        # executes the skeleton mParts on each Node on scene
        pass

    def proxy_mode(self):
        # switch on and off = on is proxy mode off is skeleton mode
        # and when back to skeleton mode it updates position and hierarchy
        # of tweaked or new Nodes, not the rest
        pass

    def _prepare_node(self, name, data, position=None):
        if position is None:
            position = [1, 1, 1]
        result = self._shapes_tree.create_node(name)
        self.modules[result.name] = result
        result.capsule = mCore.CapsuleNode()
        result.capsule.short_name = name
        result.capsule.attributes = data

        if data[3] == 'Arm' or data[3] == 'Leg':
            proxy = mCore.curve.pyramid('{}_{}'.format(result.name, self.suffix))
            root = mCore.curve.proxy('{}_root_{}'.format(result.name, self.suffix))
            mid = mCore.curve.proxy('{}_mid_{}'.format(result.name, self.suffix))
            end = mCore.curve.proxy('{}_end_{}'.format(result.name, self.suffix))
            cmds.move(rd(position[0] + 5, position[0]), rd(position[1] + 10, position[1] + 5), rd(position[2], position[2]), proxy)
            cmds.move(rd(position[0] + 5, position[0]), rd(position[1], position[1]), rd(position[2], position[2]), root)
            cmds.move(rd(position[0] + 15, position[0] + 10), rd(position[1], position[1]), rd(position[2], position[2]), mid)
            cmds.move(rd(position[0] + 25, position[0] + 20), rd(position[1], position[1]), rd(position[2], position[2]), end)
            cmds.parent([root, mid, end], proxy)

            cmds.select(cl=True)
            return result

        if data[3] == 'Spine':
            proxy = mCore.curve.pyramid('{}_{}'.format(result.name, self.suffix))
            root = mCore.curve.proxy('{}_root_{}'.format(result.name, self.suffix))
            end = mCore.curve.proxy('{}_end_{}'.format(result.name, self.suffix))
            cmds.move(rd(position[0] + 5, position[0]), rd(position[1] + 10, position[1] + 5), rd(position[2], position[2]), proxy)
            cmds.move(rd(position[0], position[0]), rd(position[1] + 5, position[1]), rd(position[2], position[2]), root)
            cmds.move(rd(position[0], position[0]), rd(position[1] + 25, position[1] + 20), rd(position[2], position[2]), end)
            cmds.parent([root, end], proxy)

            cmds.select(cl=True)
            return result

    def add_module(self, data):
        char_name = data[0]
        selection = self._check_selection()
        if not selection:
            if char_name:
                shape_parent = self._shapes_tree.create_node(char_name)
                shape_parent.group_node = True
                node = self._prepare_node('{}_{}{}'.format(char_name, data[2], data[3]), data)

                object_parent = self._objects_tree.create_node('{}'.format(char_name))
                object_start = self._objects_tree.create_node('{}|{}{}_start'.format(object_parent, data[2], data[3]))
                object_end = self._objects_tree.create_node('{}|{}{}_end'.format(object_start, data[2], data[3]))

                node.capsule.start_node = object_start
                node.capsule.end_node = object_end
                return node

            node = self._prepare_node('{}{}'.format(data[2], data[3]), data)
            node.group_node = True

            object_start = self._objects_tree.create_node('{}{}_start'.format(data[2], data[3]))
            object_end = self._objects_tree.create_node('{}|{}{}_end'.format(object_start, data[2], data[3]))

            node.capsule.start_node = object_start
            node.capsule.end_node = object_end
            return node

        if selection[0]:
            selection_name = selection[0].name
            # selected needs to give start or end node
            plug_node = None
            plug_name = None
            if selection[-1] == 'end':
                plug_node = selection[0].capsule.end_node
                plug_name = 'end'
            else:
                plug_node = selection[0].capsule.start_node
                plug_name = 'root'
            parent_group = selection[0].parent
            while parent_group.group_node is False:
                parent_group = parent_group.parent

            if char_name:
                if not mCore.utility.manipulate_name(selection_name, 'find', char_name):
                    shape_parent = self._shapes_tree.create_node('{}_{}'.format(selection_name, char_name))
                    shape_parent.group_node = True
                    plug_trans = cmds.xform('{}_{}_pxy'.format(selection_name, plug_name), q=True, ws=True, piv=True)[0:3]
                    node = self._prepare_node('{}_{}{}'.format(shape_parent.name, data[2], data[3]), data, plug_trans)
                    cmds.parent('{}_pxy'.format(node.name), '{}_{}_pxy'.format(selection_name, plug_name))

                    object_parent = self._objects_tree.create_node('{}|{}'.format(plug_node.name, char_name))
                    object_start = self._objects_tree.create_node('{}|{}{}_start'.format(object_parent.name, data[2], data[3]))
                    object_end = self._objects_tree.create_node('{}|{}{}_end'.format(object_start.name, data[2], data[3]))

                    node.capsule.start_node = object_start
                    node.capsule.end_node = object_end
                    return node

                # here is the shit
                plug_trans = cmds.xform('{}_{}_pxy'.format(selection_name, plug_name), q=True, ws=True, piv=True)[0:3]
                node = self._prepare_node('{}_{}{}'.format(parent_group.name, data[2], data[3]), data, plug_trans)
                cmds.parent('{}_pxy'.format(node.name), '{}_{}_pxy'.format(selection[0].name, plug_name))
                object_start = self._objects_tree.create_node('{}|{}{}_start'.format(plug_node.name, data[2], data[3]))
                object_end = self._objects_tree.create_node('{}|{}{}_end'.format(object_start.name, data[2], data[3]))

                node.capsule.start_node = object_start
                node.capsule.end_node = object_end
                return node

            if not char_name:
                plug_trans = cmds.xform('{}_{}_pxy'.format(selection_name, plug_name), q=True, ws=True, piv=True)[0:3]
                node = self._prepare_node('{}_{}{}'.format(parent_group.name, data[2], data[3]), data, plug_trans)
                cmds.parent('{}_pxy'.format(node.name), '{}_{}_pxy'.format(selection[0].name, plug_name))
                object_start = self._objects_tree.create_node('{}|{}{}_start'.format(plug_node.name, data[2], data[3]))
                object_end = self._objects_tree.create_node('{}|{}{}_end'.format(object_start.name, data[2], data[3]))

                node.capsule.start_node = object_start
                node.capsule.end_node = object_end
                return node


def create_proxy(info, *args):
    global _NEW_RIG_
    if not isinstance(_NEW_RIG_, Structure):
        _NEW_RIG_ = Structure()

    name = info['name']
    order = info['order']
    side = ['Right', 'Center', 'Left']
    type = ['IK', 'FK', 'IKFK']
    size = ['light', 'average', 'heavy']

    side = side[info['side']]
    type = type[info['type']]
    size = size[info['size']]

    module = info['module']

    module_data = [name, order, side, module, type, size]
    _NEW_RIG_.add_module(module_data)


def create_rig(*args):
    global _NEW_RIG_
    if not isinstance(_NEW_RIG_, Structure):
        return
    for key in _NEW_RIG_.modules:
        node = _NEW_RIG_.modules[key]
        if node.capsule.attributes[3] == 'Arm':
            node.capsule.rig = mParts.Arm(['{}_root_{}'.format(node.name, _NEW_RIG_.suffix),
                                           '{}_mid_{}'.format(node.name, _NEW_RIG_.suffix),
                                           '{}_end_{}'.format(node.name, _NEW_RIG_.suffix)], node.name)
        elif node.capsule.attributes[3] == 'Leg':
            node.capsule.rig = mParts.Leg(['{}_root_{}'.format(node.name, _NEW_RIG_.suffix),
                                           '{}_mid_{}'.format(node.name, _NEW_RIG_.suffix),
                                           '{}_end_{}'.format(node.name, _NEW_RIG_.suffix)], node.name)

        if node.capsule.attributes[4] == 'IK':
            node.capsule.rig.set_ik()
