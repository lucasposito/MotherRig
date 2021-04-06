import maya.cmds as cmds

class LeafNode(object):
    def __init__(self):
        self.name = None  # it's the path as well character|module|side|extra
        self.child_group = []  # unique child will have counter, [node, 1]
        # for siblings with same name, eg: None <-- John <--> John02 <--> John03 --> None
        self.parent = None
        self.right = None


class CapsuleNode(object):
    def __init__(self):
        self.name_node = None
        self.start_node = None
        self.end_node = None
        self.attributes = None  # [name, order, side, module, type, size]


class Tree(object):
    def __init__(self):
        self.head = LeafNode()
        self.head.name = 'Root'
        self._separator = '_'
        self._cache = []
        # self.modules = ['Spine', 'Arm', 'Leg']
        # self.side = ['Left', 'Right']

    @property
    def separator(self):
        return self._separator

    @separator.setter
    def separator(self, item):
        if not isinstance(item, str):
            return
        self._separator = item

    def get_descendants(self, name):
        self._cache = []
        node = self.find_node(name)
        nodes = []
        for children in node.child_group:
            nodes.append(children[0])
        for each in nodes:
            self._traverse_in_order(each)
        return self._cache

    def traverse(self):
        self._cache = []
        self._traverse_in_order(self.head)

    def _traverse_in_order(self, node):
        # nodes = [node.child_group, node.right]
        nodes = []
        if len(node.child_group) is not 0:
            for children in node.child_group:
                nodes.append(children[0])
        if node.right is not None:
            nodes.append(node.right)
        if len(nodes) is not 0:
            for each in nodes:
                print('- {}'.format(each.name))
                self._cache.append(each)
                self._traverse_in_order(each)

    def move_node(self):
        pass

    def _disconnect_parent(self, node):
        # disconnect sibling as well
        previous_node = None
        while node is not None and node.right is not None:
            previous_node = node
            node = node.right
        if previous_node is not None and previous_node is not node:
            previous_node.right = None

        print('leaf node \'{}\' removed'.format(node.name))
        parent = node.parent
        index = None
        # parent.child_group.remove(node)
        for elem in parent.child_group:
            if elem[0].name in node.name:
                index = parent.child_group.index(elem)
        if parent.child_group[index][-1] is 1:
            parent.child_group.pop(index)
            return node, parent
        parent.child_group[index][-1] -= 1
        return node, parent

    def delete_node(self, name):
        # From similar names in children_group it has to capture the latest one
        # while self.right is not None
        node = self.find_node(name)

        if isinstance(node, tuple):
            print('The node \'{}\' does not exist'.format(name))
            return

        if len(node.child_group) is 0:
            parent = self._disconnect_parent(node)
            return parent

        elif len(node.child_group) is 1:
            print('node \'{}\' removed'.format(name))

    def _find_child(self, name, node):
        for elem in node.child_group:
            if elem[0].name == name:
                return elem[0]
        return None

    def find_node(self, path_list):
        if isinstance(path_list, str):
            path_list = path_list.split(self.separator)
        parent = self.head
        for item in path_list:
            list_name = path_list[0:path_list.index(item) + 1]
            name = self._list_to_string(list_name, self.separator)
            try:
                int(name[-1])
                main_child = name[0:-2]
                temp = self._find_child(main_child, parent)
                while temp is not None and temp.name != name:
                    temp = temp.right
            except ValueError:
                temp = self._find_child(name, parent)
            if temp is None:
                return name, parent  # it'll be a tuple (name, node)
            parent = temp
        return parent  # it'll be an instance of Node

    def _list_to_string(self, name, item):
        if not isinstance(name, list):
            return name
        result = [item] * (len(name) * 2 - 1)
        result[0::2] = name
        final = ''.join(result)
        return final

    def _insert_child(self, child, parent):
        # update with doubly link list for names in same list of siblings
        try:
            # checks if "name" is contained in some of the elements in child_group
            temp = [value for value in parent.child_group if value[0].name == child.name][0]
        except IndexError:
            parent.child_group.append([child, 1])
            return
        temp[-1] += 1
        new_name = '{0}{1:0>2d}'.format(child.name, temp[-1])
        child.name = new_name
        first = temp[0]
        while first.right is not None:
            first = first.right
        first.right = child
        return

    def create_node(self, name):
        # update with doubly link list for names in same list of siblings
        new_node = LeafNode()
        path = name.split(self.separator)
        if len(path) is 1:
            new_node.parent = self.head
            new_node.name = name
            self._insert_child(new_node, self.head)
            return new_node

        final_info = self.find_node(path)  # it'll be a tuple (name, node) if it's first otherwise it'll be an instance
        if not isinstance(final_info, tuple):
            final_info = (final_info.name, final_info.parent)
        new_node.parent = final_info[-1]
        new_node.name = final_info[0]
        self._insert_child(new_node, final_info[-1])
        return new_node


class Structure(object):
    # That's a tree structure of the rig
    def __init__(self):
        self._mother = Tree()
        self._naming = Tree()
        self._suffix = 'pxy'
        self.modules = {}

    def _check_selection(self):
        selected = cmds.ls(sl=True)
        if len(selected) is not 1:
            return
        if manipulate_name(selected[0], 'check', self._suffix, -1) is True:
            new_name = manipulate_name(selected[0], 'delete', position=-1)
            return new_name

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
        # executes the skeleton modules on each Node on scene
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
