import maya.cmds as cmds
import mCore


class Control(object):
    def __init__(self):
        self._toggle = True
        self._toggle_parent = True
        self._toggle_point = True
        self._toggle_orient = True
        self._toggle_scale = True
        self.old_object = []
        self.new_object = []
        self.group = []
        self.suffix = []

    def _edit_suffix(self, name):
        # add the possibility of changing the element to add in between
        old_name = name.split('|')[-1]
        old_name = old_name.split('_')
        if old_name[-1] in mCore.universal_suffix:
            del (old_name[-1])
        pre_name = '_'.join(old_name)
        return pre_name

    def zero_out(self, shape=None, suffix=None, objects=None):
        self._toggle_parent = True
        self._toggle_point = True
        self._toggle_orient = True
        self._toggle_scale = True
        self.suffix = suffix

        if objects is None:
            self.old_object = cmds.ls(sl=True, l=True)
        else:
            if not isinstance(shape, list) or not isinstance(suffix, list) or not isinstance(objects, list):
                print('shape, suffix and objects have to be within a list')
                return
            self.old_object = objects

        self.old_object.sort(reverse=True)
        self.new_object = list(self.old_object)

        for sh, su in zip(shape, suffix):
            index = 0
            for obj in self.new_object:
                new_name = self._edit_suffix(obj)
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

                obj_translation = cmds.xform(obj, q=True, ws=True, piv=True)[0:3]
                obj_rotation = cmds.xform(obj, q=True, ws=True, ro=True)

                cmds.xform(pre_element, t=tuple(obj_translation))
                cmds.xform(pre_element, ro=tuple(obj_rotation))

                current = list(filter(None, obj.split('|')))
                temp = current[:-1]
                if len(temp) != 0:
                    cmds.parent(pre_element, '|'.join(temp))
                grp_temp = temp + [pre_element]

                cmds.parent(obj, '|'.join(grp_temp))
                temp.extend(['{}_{}'.format(self._edit_suffix(current[-1]), su), current[-1]])
                new = '|'.join(temp)

                self.new_object[index] = new
                for child in self.new_object[:index]:
                    previous = list(filter(None, child.split('|')))
                    intersected = [value for value in current if value in previous]
                    if len(intersected) != len(current):
                        continue
                    prev_index = self.new_object.index(child)
                    sec_temp = temp + [value for value in previous if value not in current]
                    new_child = '|'.join(sec_temp)
                    self.new_object[prev_index] = new_child

                index += 1
        cmds.select(self.new_object, r=True)

    def toggle_control(self):
        self.group = []
        if len(self.suffix) == 0:
            return
        suffix_length = (len(self.suffix) + 1) * -1
        group_suffix = suffix_length + 1
        pre_group = []
        index = 0
        for new in self.new_object:
            new = list(filter(None, new.split('|')))
            object_parent = []
            group_parent = None
            connection_point = None
            for other in self.new_object[index:]:
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
            for item in self.new_object[:index]:
                each = list(filter(None, item.split('|')))
                if [value for value in new[suffix_length:-1] if value in each]:
                    a = self.new_object.index(item)
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
            self.group.append(each)

        cmds.select(self.old_object, self.group, r=True)
        self._toggle = not self._toggle

    def constraint(self, type='parent'):
        if len(self.group) == 0:
            return

        if type == 'parent':
            for grp, obj in zip(self.group, self.old_object):
                if self._toggle_parent:
                    cmds.parentConstraint(grp, obj)
                    continue
                cmds.parentConstraint(grp, obj, rm=True)
            self._toggle_parent = not self._toggle_parent
            return

        if type == 'point':
            for grp, obj in zip(self.group, self.old_object):
                if self._toggle_point:
                    cmds.pointConstraint(grp, obj)
                    continue
                cmds.pointConstraint(grp, obj, rm=True)
            self._toggle_point = not self._toggle_point
            return

        if type == 'orient':
            for grp, obj in zip(self.group, self.old_object):
                if self._toggle_orient:
                    cmds.orientConstraint(grp, obj)
                    continue
                cmds.orientConstraint(grp, obj, rm=True)
            self._toggle_orient = not self._toggle_orient
            return

        if type == 'scale':
            for grp, obj in zip(self.group, self.old_object):
                if self._toggle_scale:
                    cmds.scaleConstraint(grp, obj)
                    continue
                cmds.scaleConstraint(grp, obj, rm=True)
            self._toggle_scale = not self._toggle_scale
