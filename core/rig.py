import maya.cmds as cmds
from random import uniform as rd
import core


_NEW_RIG_ = None


class Structure(object):
    # That's a tree structure of the rig
    def __init__(self):
        self._mother = core.Tree()
        self._naming = core.Tree()
        self._suffix = 'pxy'
        self.modules = {}

    def _check_selection(self):
        selected = cmds.ls(sl=True)
        if len(selected) is not 1:
            return
        if core.utility.manipulate_name(selected[0], 'check', self._suffix, -1) is True:
            new_name = core.utility.manipulate_name(selected[0], 'delete', position=-1)
            node = self._naming.find_node(new_name)
            if isinstance(node, tuple):
                node = None
            return node

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
        # executes the skeleton parts on each Node on scene
        pass

    def proxy_mode(self):
        # switch on and off = on is proxy mode off is skeleton mode
        # and when back to skeleton mode it updates position and hierarchy
        # of tweaked or new Nodes, not the rest
        pass

    def _find_last_parent(self, name):
        list_name = name.split('_')

    def add_module(self, data):
        # cmds.move(rd(10, -10), rd(10, -10), rd(10, -10))
        char_name = data[0]
        selection = self._check_selection()
        if not selection:
            if char_name:
                parent_result = self._naming.create_node(char_name)
                cmds.group(n='{}_{}'.format(parent_result.name, self._suffix), em=True)
                name_result = self._naming.create_node('{}_{}{}'.format(parent_result.name, data[2], data[3]))
                cmds.spaceLocator(n=('{}_{}'.format(name_result.name, self._suffix)))
                cmds.select(cl=True)
                return

            name_result = self._naming.create_node('{}{}'.format(data[2], data[3]))
            cmds.spaceLocator(n=('{}_{}'.format(name_result.name, self._suffix)))
            cmds.select(cl=True)
            return
        if selection:
            if char_name:
                if not core.utility.manipulate_name(selection.name, 'find', char_name):
                    parent_result = self._naming.create_node('{}_{}'.format(selection.name, char_name))
                    cmds.group(n='{}_{}'.format(parent_result.name, self._suffix), em=True)
                    name_result = self._naming.create_node('{}_{}{}'.format(parent_result.name, data[2], data[3]))
                    cmds.spaceLocator(n=('{}_{}'.format(name_result.name, self._suffix)))
                    cmds.select(cl=True)
                    return

                name_result = self._naming.create_node('{}_{}{}'.format(selection.name, data[2], data[3]))
                cmds.spaceLocator(n=('{}_{}'.format(name_result.name, self._suffix)))
                cmds.select(cl=True)
                return

            if not char_name:
                name_result = self._naming.create_node('{}_{}{}'.format(selection.name, data[2], data[3]))
                cmds.spaceLocator(n=('{}_{}'.format(name_result.name, self._suffix)))
                cmds.select(cl=True)
                return

        # print(name_result.name)
        # John and LeftArm

        # store it in the dictionary, complete name node and attributes
        # then create both hierarchy nodes and store it in dictionary

        # first create first layer node John, then second layer, John_Left, then third layer, John_LeftArm
        # After getting the generated name, use it to save on dict and create the hierarchy tree

        # these two pieces will have to be connected (it'll be stored in a variable)
        # this variable has to have a name connected to the module named after the generated name
        # where I can access it later by its new name


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
