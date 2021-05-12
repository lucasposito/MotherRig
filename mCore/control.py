import maya.cmds as cmds
import mCore


class Control(object):
    def __init__(self):
        self._toggle = False
        self._toggle_parent = True
        self._toggle_point = True
        self._toggle_orient = True
        self._toggle_scale = True
        self._old_object = []
        self._current_object = []
        self._group = []
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
        if len(comparable) != 0:
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
        for obj in self._current_object[0:self._current_index]:
            item = obj.split('|')
            intersected = [value for value in pre if value in item]
            if len(intersected) == len(pre):
                temp = [value for value in item if value not in pre]
                rest_child = ''
                for c in temp:
                    rest_child += c
                    rest_child += '|'
                last_list = self._current_object[self._current_index] + rest_child
                pre_name = ''
                for b in last_list:
                    pre_name += b
                self._current_object[self._current_object.index(obj)] = pre_name

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
        self._group = []
        if len(self._suffix) == 0:
            return
        suffix_length = (len(self._suffix) + 1) * -1
        group_suffix = suffix_length + 1
        pre_group = []
        index = 0
        for new in self._current_object:
            new = list(filter(None, new.split('|')))
            object_parent = []
            group_parent = None
            connection_point = None
            for other in self._current_object[index:]:
                each = list(filter(None, other.split('|')))
                intersected = [value for value in new if value in each]
                if 0 < len(intersected) < len(new):
                    object_parent.append(intersected)
                    continue

            if len(object_parent) != 0:
                parent = max(object_parent)
                group_parent = '|'.join(parent[:-1])
                difference = [value for value in new if value not in parent]
                if [value for value in new[suffix_length:] if value in difference]:
                    difference = difference[:suffix_length]
                if len(difference) != 0:
                    parent.extend(difference)
                    connection_point = '|'.join(parent)
                else:
                    connection_point = '|'.join(parent)

            if len(object_parent) == 0 and len(new) > (suffix_length * -1):
                object_parent.extend(new[:suffix_length])
                connection_point = '|'.join(object_parent)
                group_parent = []

            pre_group.append(new[suffix_length:-1])
            for item in self._current_object[:index]:
                each = list(filter(None, item.split('|')))
                if [value for value in new[suffix_length:-1] if value in each]:
                    a = self._current_object.index(item)
                    pre_group[a][:0] = new[suffix_length:-1]

            group = '|'.join(new[:group_suffix])
            new = '|'.join(new)
            index += 1
            if connection_point is not None:
                cmds.parent(new, connection_point)
                if len(group_parent) == 0:
                    cmds.parent(group, w=True)
                    continue
                cmds.parent(group, group_parent)
                continue
            cmds.parent(new, w=True)

        for grp in pre_group:
            each = '|'.join(grp)
            self._group.append(each)

        cmds.select(self._old_object, self._group, r=True)
        self._toggle = not self._toggle

    def constraint(self, type='parent'):
        if len(self._group) == 0:
            return

        if type == 'parent':
            for grp, obj in zip(self._group, self._old_object):
                if self._toggle_parent:
                    cmds.parentConstraint(grp, obj)
                    continue
                cmds.parentConstraint(grp, obj, rm=True)
            self._toggle_parent = not self._toggle_parent
            return

        if type == 'point':
            for grp, obj in zip(self._group, self._old_object):
                if self._toggle_point:
                    cmds.pointConstraint(grp, obj)
                    continue
                cmds.pointConstraint(grp, obj, rm=True)
            self._toggle_point = not self._toggle_point
            return

        if type == 'orient':
            for grp, obj in zip(self._group, self._old_object):
                if self._toggle_orient:
                    cmds.orientConstraint(grp, obj)
                    continue
                cmds.orientConstraint(grp, obj, rm=True)
            self._toggle_orient = not self._toggle_orient
            return

        if type == 'scale':
            for grp, obj in zip(self._group, self._old_object):
                if self._toggle_scale:
                    cmds.scaleConstraint(grp, obj)
                    continue
                cmds.scaleConstraint(grp, obj, rm=True)
            self._toggle_scale = not self._toggle_scale
