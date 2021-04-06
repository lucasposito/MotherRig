import maya.cmds as cmds
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
            node = self._naming.find_node([new_name])
            return node

        # if nothing is selected it creates on root
        # if something is selected, this is the parent

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
        # QLineEdit empty means None
        # None doesn't add name, it adds just module's name like "LeftArm"
        # If name in QLineEdit is the same as closest parent's name,
        # like it's typed John and John is there already, then
        # QLineEdit becomes None

        # def create_node(parent, name):
        #     if parent is not None:
        #         final_name = '{}_{}'.format(parent, name)
        #         return final_name
        #     final_name = name
        #     return final_name
        selection = self._check_selection()
        char_name = data[0]
        name_result = None

        new_layers_to_add = 1
        consider_parent = False
        if not selection and not char_name:
            consider_parent = True
            char_name = '{}{}'.format(data[2], data[3])
            name_result = self._naming.create_node(char_name)
            print(name_result.name)
        elif not selection and char_name:
            new_layers_to_add = 2
            pre_step = data[0]
            char_name = '{}_{}{}'.format(data[0], data[2], data[3])
            self._naming.create_node(pre_step)
            name_result = self._naming.create_node(char_name)
            print(name_result.name)
        elif selection and not char_name:
            consider_parent = True
            char_name = '{}_{}{}'.format(selection, data[2], data[3])
            name_result = self._naming.create_node(char_name)
        elif selection == char_name:
            # if last parent == char_name
            consider_parent = True
            pass
        elif selection != char_name:
            # if last parent != char_name
            consider_parent = True
            new_layers_to_add = 2
            pass

        #
        # elif selection != char_name:
        #     consider_parent = True
        #     pre_step = '{}_{}'.format(selection, data[0])
        #     char_name = '{}_{}{}'.format(pre_step, data[2], data[3])
        #     self._naming.create_node(pre_step)
        #     name_result = self._naming.create_node(char_name)
        #
        # else:
        #     pre_step = data[0]
        #     char_name = '{}_{}{}'.format(pre_step, data[2], data[3])
        #     self._naming.create_node(pre_step)
        #     name_result = self._naming.create_node(char_name)

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
