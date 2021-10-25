import maya.OpenMaya as old_om
import maya.api.OpenMaya as om
import maya.cmds as cmds
import math
import fnmatch

from mCore import universal_suffix


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


def select_all_controls():
    main_namespace = None
    if cmds.ls(sl=True):
        try:
            main_reference = cmds.referenceQuery(cmds.ls(sl=True), referenceNode=True)
            main_file = cmds.referenceQuery(main_reference, filename=True)
            main_namespace = cmds.referenceQuery(main_file, ns=True)
        except RuntimeError:
            pass

    if main_namespace:
        shapes = [value for value in cmds.ls(type="nurbsCurve") if value in cmds.namespaceInfo(main_namespace, ls=True)]
    else:
        shapes = cmds.ls(type="nurbsCurve")
    curves = fnmatch.filter(cmds.listRelatives(shapes, parent=True), '*_ctr')
    curves.extend(fnmatch.filter(cmds.listRelatives(shapes, parent=True), '*IKFK'))
    curves.extend(fnmatch.filter(cmds.listRelatives(shapes, parent=True), '*_IK'))
    cmds.select(curves, r=True)


def select_all_keyed():
    cache = []
    for i in cmds.ls():
        if cmds.keyframe(i, query=True, at=['translate', 'rotate'], vc=True) is not None:
            cache.append(i)
    cmds.select(cache, r=True)


def select_non_crv():
    curves = cmds.listRelatives(cmds.ls(type="nurbsCurve"), parent=True)
    cache = []
    for i in cmds.ls():
        if cmds.keyframe(i, query=True, at=['translate', 'rotate'], vc=True) is not None:
            cache.append(i)
    not_shapes = [each for each in cache if each not in curves]
    cmds.select(not_shapes, r=True)


def freeze_joints():
    selected = cmds.ls(sl=True)
    for each in selected:
        cmds.makeIdentity(each, a=True, t=True, r=True, s=True)
        cmds.setAttr('{}.jointOrient'.format(each), 0, 0, 0)


def skin_cluster_joints():
    selected = cmds.ls(sl=True)
    cmds.select(cmds.skinCluster(selected, q=True, inf='findRelatedSkinCluster'), r=True)


def orient_limbo(objects, name):
    if len(objects) != 3:
        return
    main_limb = []
    position = {}
    limb_key = ['Root', 'Mid', 'End']
    index = 0
    for each in objects:
        position[limb_key[index]] = cmds.xform(each, q=True, ws=True, t=True)
        index += 1

    cmds.xform(cmds.spaceLocator(p=position['Mid']), cp=True)
    locator = cmds.ls(sl=True, l=True)
    cmds.select(d=True)

    first = cmds.joint(n='{}_{}'.format(name[0], universal_suffix[-1]), p=position['Root'])
    second = cmds.joint(n='{}_{}'.format(name[1], universal_suffix[-1]), p=position['Mid'])
    third = cmds.joint(n='{}_{}'.format(name[2], universal_suffix[-1]), p=position['End'])
    main_limb.append(first)
    main_limb.append('{}|{}'.format(first, second))
    main_limb.append('{}|{}|{}'.format(first, second, third))

    cmds.joint(main_limb[0], e=True, oj="yxz", sao="xup", ch=True, zso=True)

    for a in main_limb:
        cmds.setAttr(a + '.jointOrient', 0, 0, 0)
    cmds.setAttr('{}.preferredAngleX'.format(main_limb[1]), 90)
    ik_handle = cmds.ikHandle(sj=main_limb[0], ee=main_limb[-1])
    cmds.move(position['End'][0], position['End'][1], position['End'][-1], a=True)
    cmds.poleVectorConstraint(locator, ik_handle[0])
    cmds.delete(locator)
    for b in main_limb:
        cmds.makeIdentity(b, a=True, t=1, r=1, s=1, n=0)
    cmds.delete()
    cmds.setAttr('{}.preferredAngleX'.format(main_limb[1]), 0)
    return main_limb


def limb_name(limb, name=None):
    final_name = name
    selected = cmds.ls(sl=True, l=True)

    if limb == 'Arm':
        chain = ['Arm', 'ForeArm', 'Hand']
    elif limb == 'Leg':
        chain = ['UpLeg', 'Leg', 'Foot']
    else:
        return

    index = 0
    if not final_name:
        if selected:
            final_name = selected[0].split('|')[-1]
        else:
            final_name = limb

    for each in reversed(final_name):
        if not each.isdigit():
            break
        index += 1

    if index != 0:
        number = final_name[-index:]
        final_name = final_name[:-index]
        if final_name[-3:] == limb:
            final_name = final_name[:-3]
        root = '{}{}{}'.format(final_name, chain[0], number)
        mid = '{}{}{}'.format(final_name, chain[1], number)
        end = '{}{}{}'.format(final_name, chain[2], number)
        return [root, mid, end]

    if final_name[-3:] == limb:
        final_name = final_name[:-3]

    root = '{}{}'.format(final_name, chain[0])
    mid = '{}{}'.format(final_name, chain[1])
    end = '{}{}'.format(final_name, chain[2])
    return [root, mid, end]


def hand_name(limb, name=None, fingers=None):
    final_name = name + '_'
    selected = cmds.ls(sl=True, l=True)
    num_fingers = fingers

    hand_list = ['Thumb', 'Index', 'Pinky', 'Middle', 'Ring', 'Extra']
    foot_list = ['BigToe', 'SecondToe', 'PinkyToe', 'MiddleToe', 'RingToe', 'ExtraToe']

    if limb == 'Hand':
        if num_fingers > 5:
            chain = ['{}1_num{}'.format(hand_list[5], num_fingers - 4),
                     '{}2_num{}'.format(hand_list[5], num_fingers - 4),
                     '{}3_num{}'.format(hand_list[5], num_fingers - 4)]
        else:
            chain = [hand_list[num_fingers] + '1', hand_list[num_fingers] + '2', hand_list[num_fingers] + '3']
    elif limb == 'Foot':
        if num_fingers > 5:
            chain = ['{}1_num{}'.format(foot_list[5], num_fingers - 4),
                     '{}2_num{}'.format(foot_list[5], num_fingers - 4),
                     '{}3_num{}'.format(foot_list[5], num_fingers - 4)]
        else:
            chain = [foot_list[num_fingers] + '1', foot_list[num_fingers] + '2', foot_list[num_fingers] + '3']
    else:
        return

    index = 0
    if not final_name:
        if selected:
            final_name = selected[0].split('|')[-1]
        else:
            final_name = limb

    for each in reversed(final_name):
        if not each.isdigit():
            break
        index += 1

    if index != 0:
        number = final_name[-index:]
        final_name = final_name[:-index]
        if final_name[-3:] == limb:
            final_name = final_name[:-3]
        root = '{}{}{}'.format(final_name, chain[0], number)
        mid = '{}{}{}'.format(final_name, chain[1], number)
        end = '{}{}{}'.format(final_name, chain[2], number)
        return [root, mid, end]

    if final_name[-3:] == limb:
        final_name = final_name[:-3]

    root = '{}{}'.format(final_name, chain[0])
    mid = '{}{}'.format(final_name, chain[1])
    end = '{}{}'.format(final_name, chain[2])
    return [root, mid, end]


def quadruped_limb_name(limb, name=None):
    final_name = name
    selected = cmds.ls(sl=True, l=True)

    if limb == 'Arm':
        chain = ['Arm', 'ForeArm', 'Wrist', 'Hand']
    elif limb == 'Leg':
        chain = ['UpLeg', 'Leg', 'Heel', 'Foot']
    else:
        return

    index = 0
    if not final_name:
        if selected:
            final_name = selected[0].split('|')[-1]
        else:
            final_name = limb

    for each in reversed(final_name):
        if not each.isdigit():
            break
        index += 1

    if index != 0:
        number = final_name[-index:]
        final_name = final_name[:-index]
        if final_name[-3:] == limb:
            final_name = final_name[:-3]
        root = '{}{}{}'.format(final_name, chain[0], number)
        mid_first = '{}{}{}'.format(final_name, chain[1], number)
        mid = '{}{}{}'.format(final_name, chain[2], number)
        end = '{}{}{}'.format(final_name, chain[3], number)
        return [root, mid_first, mid, end]

    if final_name[-3:] == limb:
        final_name = final_name[:-3]

    root = '{}{}'.format(final_name, chain[0])
    mid_first = '{}{}'.format(final_name, chain[1])
    mid = '{}{}'.format(final_name, chain[2])
    end = '{}{}'.format(final_name, chain[3])
    return [root, mid_first, mid, end]


def chain_name(element, name=None):
    final_name = name
    selected = cmds.ls(sl=True, l=True)

    extra_clean = None

    if element == 'Spine':
        name_len = 5
        chain = ['Hips', 'Spine', 'Neck', 'LeftShoulder', 'RightShoulder']
    else:
        return

    index = 0
    if final_name is None:
        final_name = selected[0].split('|')[-1]

    for each in reversed(final_name):
        if not each.isdigit():
            break
        index += 1

    if index != 0:
        number = final_name[-index:]
        final_name = final_name[:-index]
        if final_name[-name_len:] == element:
            final_name = final_name[:-name_len]
        if extra_clean == final_name[-5:]:
            final_name = final_name[:-5]
        root = '{}{}{}'.format(final_name, chain[0], number)
        mid = '{}{}{}'.format(final_name, chain[1], number)
        end = '{}{}{}'.format(final_name, chain[2], number)
        left = '{}{}{}'.format(final_name, chain[3], number)
        right = '{}{}{}'.format(final_name, chain[-1], number)
        return [root, mid, end, left, right]

    if final_name[-name_len:] == element:
        final_name = final_name[:-name_len]
    if extra_clean == final_name[-5:]:
        final_name = final_name[:-5]

    root = '{}{}'.format(final_name, chain[0])
    mid = '{}{}'.format(final_name, chain[1])
    end = '{}{}'.format(final_name, chain[2])
    left = '{}{}'.format(final_name, chain[3])
    right = '{}{}'.format(final_name, chain[-1])
    return [root, mid, end, left, right]


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

    if action == 'query':
        return name_list[position]


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


def twist_roll(twist_target, twist_end, twist_rolls, reverse=False, axis='y'):
    if not isinstance(twist_rolls, list) or len(twist_rolls) == 0:
        return
    if reverse:
        twist_rolls.reverse()

    axis = axis.upper()
    mult_matrix = cmds.createNode('multMatrix', n=twist_target + '_multMatrix_twist')
    dec_matrix = cmds.createNode('decomposeMatrix', n=twist_target + '_decomposeMatrix_twist')
    quat = cmds.createNode('quatToEuler', n=twist_target + '_quatToEuler_twist')

    cmds.connectAttr(twist_target + '.worldMatrix', mult_matrix + '.matrixIn[0]')
    cmds.connectAttr(twist_end + '.worldInverseMatrix', mult_matrix + '.matrixIn[1]')
    cmds.connectAttr(mult_matrix + '.matrixSum', dec_matrix + '.inputMatrix')
    cmds.connectAttr(dec_matrix + '.outputQuat' + axis, quat + '.inputQuat' + axis)
    cmds.connectAttr(dec_matrix + '.outputQuatW', quat + '.inputQuatW')

    roll_amount = len(twist_rolls) + 1
    index = 1
    for i in twist_rolls:
        twist_amount = float(index) / float(roll_amount)
        mult = cmds.createNode('multiplyDivide', n='{}_{}_twistStrength'.format(i, int(twist_amount * 100)))
        cmds.setAttr(mult + '.input2X', twist_amount)
        cmds.setAttr(mult + '.input2Y', twist_amount)
        cmds.setAttr(mult + '.input2Z', twist_amount)
        cmds.connectAttr(quat + '.outputRotate', mult + '.input1')
        cmds.connectAttr(mult + '.output', i + '.rotate')
        index += 1


def negative_twist(twist_target, twist_rolls, reverse=False, axis='y'):
    if not isinstance(twist_rolls, list) or len(twist_rolls) == 0:
        return
    if reverse:
        twist_rolls.reverse()

    axis = axis.upper()
    dec_matrix = cmds.createNode('decomposeMatrix')
    quat = cmds.createNode('quatToEuler')

    cmds.connectAttr(twist_target + '.matrix', dec_matrix + '.inputMatrix')
    cmds.connectAttr(dec_matrix + '.outputQuat' + axis, quat + '.inputQuat' + axis)
    cmds.connectAttr(dec_matrix + '.outputQuatW', quat + '.inputQuatW')

    roll_amount = len(twist_rolls)
    index = 0
    for i in twist_rolls:
        twist_amount = (float(roll_amount - index) / float(roll_amount)) * -1
        mult = cmds.createNode('multiplyDivide')
        cmds.setAttr(mult + '.input2X', twist_amount)
        cmds.setAttr(mult + '.input2Y', twist_amount)
        cmds.setAttr(mult + '.input2Z', twist_amount)
        cmds.connectAttr(quat + '.outputRotate', mult + '.input1')
        cmds.connectAttr(mult + '.output', i + '.rotate')
        index += 1


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
    vector = om.MVector(pos[0], pos[1], pos[2])
    return vector


def pole_vector(pos_a, pos_b, pos_c, multiplier=1):
    point_a = create_vector(pos_a)
    point_b = create_vector(pos_b)
    point_c = create_vector(pos_c)

    vector_ab = point_b - point_a
    vector_ac = point_c - point_a
    ac_normal = vector_ac.normalize()

    proj_length = vector_ab * ac_normal
    proj_vector = (ac_normal * proj_length) + point_a

    vector_pb = point_b - proj_vector
    pb_normal = vector_pb.normalize()
    pole_position = (point_b + (pb_normal * vector_ab.length())) * multiplier
    return pole_position


def distance_between(obj=None):
    if not obj:
        selection = cmds.ls(sl=True)
    else:
        selection = obj
    if len(selection) != 2:
        return
    obj1_pos = object_position(selection[0])
    obj2_pos = object_position(selection[1])

    vector1 = create_vector(obj1_pos)
    vector2 = create_vector(obj2_pos)

    distance = vector1 - vector2
    return distance.length()


__start_index__ = {0: 0, 1: 4, 2: 8, 3: 12}


def set_matrix_row(row=0, vec=None, matrix=None):
    matrix[__start_index__[row]] = vec[0]
    matrix[__start_index__[row] + 1] = vec[1]
    matrix[__start_index__[row] + 2] = vec[2]


def get_matrix_row(row=0, in_mat=None):
    out_vec = om.MVector(in_mat[__start_index__[row]],
                         in_mat[__start_index__[row] + 1],
                         in_mat[__start_index__[row] + 2])
    return out_vec


def get_matrix(transform, mat_attr='worldMatrix[0]'):
    mat_data = cmds.getAttr(transform + '.' + mat_attr)
    mat = om.MMatrix(mat_data)
    return mat


def get_quaternion(transform):
    mat_a = get_matrix(transform)
    tm_in_mat = om.MTransformationMatrix(mat_a)
    py_quat = tm_in_mat.rotationComponents(asQuaternion=True)
    quat = om.MQuaternion(py_quat)
    return quat


def quaternion_constrain(driver, driven):
    driver_quat = get_quaternion(driver)
    driver_matrix = get_matrix(driver)
    driver_pos = get_matrix_row(3, driver_matrix)

    result_matrix = driver_quat.asMatrix()
    set_matrix_row(3, driver_pos, result_matrix)

    if cmds.listRelatives(driven, p=True):
        parent_matrix = get_matrix(cmds.listRelatives(driven, p=True, f=True)[0])
        result_matrix = result_matrix * parent_matrix.inverse()

    cmds.xform(driven, m=result_matrix)


def cardinal_orient(obj, south, north, left, right):
    def old_api_vector(pos):
        vector = old_om.MVector(pos[0], pos[1], pos[2])
        return vector

    obj_dag = old_om.MDagPath()
    sel_list = old_om.MSelectionList()
    sel_list.add(obj)
    sel_list.getDagPath(0, obj_dag)

    transform_fn = old_om.MFnTransform(obj_dag)

    vertical_axis = old_om.MVector().yAxis
    horizontal_axis = old_om.MVector().xAxis

    vertical_vector = (old_api_vector(north) - old_api_vector(south)).normal()
    horizontal_vector = (old_api_vector(left) - old_api_vector(
        right)).normal()

    obj_u = vertical_vector.normal()

    obj_v = horizontal_vector
    obj_w = (obj_u ^ obj_v).normal()

    obj_v = obj_w ^ obj_u

    quaternion_u = old_om.MQuaternion(vertical_axis, obj_u)
    quaternion = quaternion_u

    sec_axis_rotated = horizontal_axis.rotateBy(quaternion)

    angle = math.acos(sec_axis_rotated * obj_v)
    quaternion_v = old_om.MQuaternion(angle, obj_u)

    if not obj_v.isEquivalent(sec_axis_rotated.rotateBy(quaternion_v), 1.0e-5):
        angle = (2 * math.pi) - angle
        quaternion_v = old_om.MQuaternion(angle, obj_u)

    quaternion *= quaternion_v

    transform_fn.setObject(obj_dag)
    transform_fn.setRotation(quaternion)
