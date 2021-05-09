import maya.cmds as cmds
import mCore


class Control(object):
    def __init__(self):
        self._toggle = False
        self._old_object = []
        self._current_object = []
        self._suffix = ''

        self._object_father = {}
        self._object_translation = {}
        self._object_rotation = {}

        self._old_parent_index = 1
        self._parent_index = 0
        self._current_index = 0

    @property
    def object(self):
        return self._current_object

    @object.setter
    def object(self, element):
        element.sort(reverse=True)
        self._current_object = element
        self.update_position()

    def update_position(self):
        for elem in self._current_object:
            self._object_translation[elem] = cmds.xform(elem, q=True, ws=True, piv=True)[0:3]
            self._object_rotation[elem] = cmds.xform(elem, q=True, ws=True, ro=True)
            self._object_father[elem] = cmds.listRelatives(elem, p=True, f=True)

    def edit_suffix(self, name):
        # add the possibility of changing the element to add in between
        old_name = name.split('|')[-1]
        old_name = old_name.split('_')
        if len(old_name[-1]) == 3:
            del (old_name[-1])
        pre_name = '_'.join(old_name)
        return pre_name

    def find_parent_index(self, main):
        pre = main.split('|')
        comparable = pre[1:-1]
        previous_element = ''
        if len(comparable) is not 0:
            result = ['|'] * (len(comparable) * 2 - 1)
            result[0::2] = comparable
            result.insert(0, '|')
            for a in result:
                previous_element += a
        try:
            self._parent_index = self._current_object.index(previous_element)
        except ValueError:
            pass

    def update_path(self, main):
        pre = main.split('|')
        # checks if the intersected list between 'pre' and 'item' equals 'pre'
        # it means 'pre' fully fits in 'item'
        for a in self._current_object[0:self._current_index]:
            item = a.split('|')
            intersected = [value for value in pre if value in item]
            if len(intersected) is len(pre):
                temp = [value for value in item if value not in pre]
                rest_child = ''
                for c in temp:
                    rest_child += c
                    rest_child += '|'
                last_list = self._current_object[self._current_index] + rest_child
                pre_name = ''
                for b in last_list:
                    pre_name += b
                self._current_object[self._current_object.index(a)] = pre_name

        self._object_father = {}
        self._object_translation = {}
        self._object_rotation = {}

        self._old_parent_index = 1
        self._parent_index = 0
        self._current_index = 0
        self.update_position()

        cmds.select(self.object, r=True)
        last = cmds.ls(sl=True, l=True)
        self.object = last

    def zero_out(self, shape=None, suffix=None):
        self._suffix = suffix
        self._old_object = cmds.ls(sl=True, l=True)
        self._old_object.sort(reverse=True)
        self.object = cmds.ls(sl=True, l=True)
        if not isinstance(shape, list) or not isinstance(suffix, list):
            print('shape and suffix have to be inside of a list')
            return
        for sh, su in zip(shape, suffix):
            for obj in self._current_object:
                new_name = self.edit_suffix(obj)

                if sh == 'circle':
                    pre_element = mCore.curve.circle('{}_{}'.format(new_name, su))
                elif sh == 'cube':
                    pre_element = mCore.curve.cube('{}_{}'.format(new_name, su))
                elif sh == 'pyramid':
                    pre_element = mCore.curve.pyramid('{}_{}'.format(new_name, su))
                elif sh == 'diamond':
                    pre_element = mCore.curve.diamond('{}_{}'.format(new_name, su))
                elif sh == 'square':
                    pre_element = mCore.curve.square('{}_{}'.format(new_name, su))
                elif sh == 'knot':
                    pre_element = mCore.curve.knot('{}_{}'.format(new_name, su))
                elif sh == 'quad_arrow':
                    pre_element = mCore.curve.quad_arrow('{}_{}'.format(new_name, su))
                else:
                    pre_element = cmds.group(n='{}_{}'.format(new_name, su), em=True)

                cmds.xform(pre_element, t=tuple(self._object_translation[obj]))
                cmds.xform(pre_element, ro=tuple(self._object_rotation[obj]))
                try:
                    if self._object_father[obj] is not None:
                        cmds.parent(pre_element, self._object_father[obj])
                    zero_element = cmds.ls(pre_element, l=True)

                    self.find_parent_index(obj)
                    self._current_index = self._current_object.index(obj)

                    pre = obj.split('|')
                    pre = [i for i in pre if i]
                    self._current_object[self._current_index] = zero_element[0] + '|' + pre[-1] + '|'
                    cmds.parent(obj, zero_element[0])

                    if self._old_parent_index is self._current_index:
                        self._old_parent_index = self._parent_index
                    self.update_path(obj)
                except IndexError:
                    print('Suffix \'{}\' can\'t be the same'.format(su))

    def toggle_control(self):
        if len(self._suffix) == 0:
            return
        self._toggle = not self._toggle
        self._unparent_elements()
        suffix_length = (len(self._suffix) + 1) * -1
        index = 0
        for old, new in zip(self._old_object, self._current_object):
            old = list(filter(None, old.split('|')))
            new = list(filter(None, new.split('|')))
            parent_list = []
            parent_index = None
            connection_point = None
            for other in self._old_object[index:]:
                each = list(filter(None, other.split('|')))
                intersected = [value for value in old if value in each]
                if 0 < len(intersected) < len(old):
                    parent_list.append(intersected)
                    parent_index = self._old_object.index(other)
                    break

            if len(parent_list) != 0:
                parent = max(parent_list)
                short_name = parent[-1]
                difference = [value for value in old if value not in parent]
                if old[-1] in difference:
                    difference.remove(old[-1])
                if len(difference) != 0:
                    difference.insert(0, short_name)
                    connection_point = '|'.join(difference)
                else:
                    connection_point = short_name
            if parent_index is not None:
                parent = self._current_object[parent_index].split('|')[suffix_length:-1]
                parent = '|'.join(parent)
                cmds.parent(new[suffix_length], parent)
            if len(old) > 1 and len(parent_list) == 0:
                connection_point = '|'.join(old[:-1])
            if connection_point is not None:
                cmds.parent(old[-1], connection_point)
            index += 1

        cmds.select(self._old_object, r=True)

    def _unparent_elements(self):
        temp = None
        for obj in range(len(self._suffix)):
            cmds.pickWalk(d='up')
            temp = cmds.ls(sl=True, l=True)
        for each in temp:
            if cmds.listRelatives(each, p=True) is None:
                temp.remove(each)
        cmds.parent(self._current_object, temp, w=True)
        cmds.select(cl=True)
