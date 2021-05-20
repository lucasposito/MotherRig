import maya.api.OpenMaya as om2
import maya.cmds as cmds


def clean_namespaces():
    refs = cmds.file(q=True, r=True)
    for a in refs:
        cmds.file(a, ir=True)

    n_spaces = cmds.namespaceInfo(':', lon=True, r=True)
    defa = ['UI', 'shared']
    diff = [b for b in n_spaces if b not in defa]
    diff.sort(reverse=True)

    for d in diff:
        cmds.namespace(removeNamespace=d + ":", mergeNamespaceWithRoot=True)
    print('All namespaces deleted')
    
    
def manipulate_name(full_name, action=None, name=None, position=None, separator='_'):
    if not full_name:
        return
    name_list = full_name.split(separator)

    if action == 'delete':
        del name_list[position]
        new_name = separator.join(name_list)
        return new_name

    if action == 'replace':
        del name_list[position]
        if position is -1:
            name_list.append(name)
            new_name = separator.join(name_list)
            return new_name
        if position < -1:
            position += 1
        name_list.insert(position, name)
        new_name = separator.join(name_list)
        return new_name

    if action == 'add':
        if position is -1:
            name_list.append(name)
            new_name = separator.join(name_list)
            return new_name
        if position < -1:
            position += 1
        name_list.insert(position, name)
        new_name = separator.join(name_list)
        return new_name

    if action == 'check':
        if name_list[position] == name:
            return True

    if action == 'find' and name:
        occurrence = []
        for each in name_list:
            try:
                each.index(name)
            except ValueError:
                continue
            else:
                index = name_list.index(each)
                occurrence.append(index)
        if len(occurrence) == 0:
            return
        return occurrence


def joint_hierarchy():
    def joint_type(obj):
        temp = cmds.objectType(obj)
        if temp == 'joint':
            return True
    skeleton = []
    parent = cmds.ls(sl=True, l=True)
    upper_parent = cmds.listRelatives(p=True, f=True)
    if len(parent) is not 1:
        return
    while upper_parent is not None:
        cmds.select(upper_parent, r=True)
        parent.insert(0, upper_parent[0])
        upper_parent = cmds.listRelatives(p=True, f=True)
    for main in parent:
        if joint_type(main) is True:
            skeleton.append(main)
            for each in cmds.listRelatives(main, ad=True, f=True):
                if joint_type(each) is True:
                    skeleton.append(each)
            return skeleton


def object_size(obj):
    shape = cmds.listRelatives(obj, s=True, f=True)
    min_size = cmds.getAttr('%s.boundingBoxMin' % shape[0])[0]
    max_size = cmds.getAttr('%s.boundingBoxMax' % shape[0])[0]

    width = max_size[0] - min_size[0]
    height = max_size[1] - min_size[1]
    depth = max_size[2] - min_size[2]

    return width, height, depth


def object_position(obj):
    pos = tuple(cmds.xform(obj, q=True, ws=1, piv=1)[:3])
    return pos


def create_vector(pos):
    vector = om2.MVector(pos[0], pos[1], pos[2])
    return vector


def distance_between():
    selection = cmds.ls(sl=True)
    if len(selection) != 2:
        return
    obj1_pos = object_position(selection[0])
    obj2_pos = object_position(selection[1])

    vector1 = create_vector(obj1_pos)
    vector2 = create_vector(obj2_pos)

    distance = vector1 - vector2
    return distance.length()
