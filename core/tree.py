
class LeafNode(object):
    def __init__(self):
        self.name = None  # it's the path as well character|module|side|extra
        self.child_group = []  # unique child will have counter, [node, 1]
        # for siblings with same name, eg: None <-- John <--> John02 <--> John03 --> None
        self.parent = None
        self.right = None
        self.capsule = None


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
        # self.parts = ['Spine', 'Arm', 'Leg']
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
        if len(node.child_group) != 0:
            for children in node.child_group:
                nodes.append(children[0])
        if node.right is not None:
            nodes.append(node.right)
        if len(nodes) != 0:
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
        if parent.child_group[index][-1] == 1:
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

        if len(node.child_group) == 0:
            parent = self._disconnect_parent(node)
            return parent

        elif len(node.child_group) == 1:
            print('node \'{}\' removed'.format(name))

    def _find_child(self, name, node):
        for elem in node.child_group:
            if elem[0].name == name:
                return elem[0]
        return None

    def find_node(self, path_name):
        path_name = path_name.split(self._separator)
        parent = self.head
        index = 0
        for item in path_name:
            if not path_name[index] == item:
                index += 1
                continue
            list_name = path_name[0:index + 1]
            name = self._separator.join(list_name)
            index += 1

            if name[-1].isdigit() is True:
                main_child = name[0:-2]
                temp = self._find_child(main_child, parent)
                while temp is not None and temp.name != name:
                    temp = temp.right
            else:
                temp = self._find_child(name, parent)
            if temp is None:
                return name, parent  # it'll be a tuple (name, node)
            parent = temp
        return parent  # it'll be an instance of Node

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
        if len(path) == 1:
            new_node.parent = self.head
            new_node.name = name
            self._insert_child(new_node, self.head)
            return new_node

        final_info = self.find_node(name)  # it'll be a tuple (name, node) if it's first otherwise it'll be an instance
        if not isinstance(final_info, tuple):
            final_info = (final_info.name, final_info.parent)
        new_node.parent = final_info[-1]
        new_node.name = final_info[0]
        self._insert_child(new_node, final_info[-1])
        return new_node
