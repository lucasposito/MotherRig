import maya.cmds as cmds
import core


class Control(object):
    def __init__(self):
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

    def zero_out(self, shape=None, suffix=None, inside=True):
        self.object = cmds.ls(sl=True, l=True)
        if not isinstance(shape, list) or not isinstance(suffix, list):
            return
        for sh, su in zip(shape, suffix):
            for obj in self._current_object:
                new_name = self.edit_suffix(obj)

                if sh == 'circle':
                    pre_element = core.curve.circle('{}_{}'.format(new_name, su))
                elif sh == 'cube':
                    pre_element = core.curve.cube('{}_{}'.format(new_name, su))
                elif sh == 'diamond':
                    pre_element = core.curve.diamond('{}_{}'.format(new_name, su))
                elif sh == 'square':
                    pre_element = core.curve.square('{}_{}'.format(new_name, su))
                elif sh == 'knot':
                    pre_element = core.curve.knot('{}_{}'.format(new_name, su))
                elif sh == 'quad_arrow':
                    pre_element = core.curve.quad_arrow('{}_{}'.format(new_name, su))
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
