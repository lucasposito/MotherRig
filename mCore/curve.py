import maya.cmds as cmds

color_value = {'grey': 3, 'blue': 6, 'red': 13, 'yellow': 17, 'lightBlue': 18, 'rose': 20, 'green': 28}


def color(value):
    object_list = cmds.listRelatives(cmds.ls(sl=True, l=True), s=True, f=True)
    if not object_list:
        return
    for each in object_list:
        cmds.setAttr('{}.overrideEnabled'.format(each), 1)
        cmds.setAttr('{}.overrideColor'.format(each), value)
    cmds.select(cl=True)


def rgb_color(r=0, g=0, b=1):
    value = (r, g, b)
    rgb = ('R', 'G', 'B')
    object_list = cmds.listRelatives(cmds.ls(sl=True, l=True), s=True, f=True)
    for each in object_list:
        cmds.setAttr('{}.overrideRGBColors'.format(each), 1)
        for a, b in zip(rgb, value):
            cmds.setAttr('{}.overrideColor{}'.format(each, a), b)
    cmds.select(cl=True)


def size(value=1.1):
    selected = cmds.ls(sl=True)
    for each in selected:
        shapes = cmds.listRelatives(each, s=True, f=True)
        curve_pivot = cmds.xform(each, q=True, ws=True, piv=True)
        del (curve_pivot[2:-1])
        for crv in shapes:
            cmds.scale(value, value, value, '{}.cv[*]'.format(crv), r=True, p=curve_pivot)


def lock_hide_attr(obj, attr_array, lock, hide):
    for a in attr_array:
        cmds.setAttr(obj + '.' + a, k=hide, l=lock)


def normalize_size(factor=0.8):
    objects = [a for a in cmds.ls(sl=True) if cmds.listRelatives(a, s=True, f=True, type='nurbsCurve')]
    for child in cmds.listRelatives(cmds.ls(sl=True), ad=True, f=True, type='nurbsCurve'):
        if not cmds.listRelatives(child, s=True, f=True):
            continue
        objects.append(child)
    cmds.select(objects, r=True)


def gimbal(name='gimbal_ctr'):
    vertex_position = [(0, 7, 0), (1, 5, 0), (-1, 5, 0), (0, 7, 0), (0, 5, 1), (0, 5, -1), (0, 7, 0),
                       (0, -7, 0), (1, -5, 0), (-1, -5, 0), (0, -7, 0), (0, -5, 1), (0, -5, -1), (0, -7, 0)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13]

    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    y_shape = cmds.listRelatives(curve_object, s=True)[0]
    y_shape = cmds.rename(y_shape, '{}_YShape'.format(curve_object))
    cmds.setAttr('{}.overrideEnabled'.format(y_shape), 1)
    cmds.setAttr('{}.overrideColor'.format(y_shape), 14)

    z_arrow = cmds.duplicate(curve_object)[0]
    z_shape = cmds.listRelatives(z_arrow, s=True)[0]
    z_shape = cmds.rename(z_shape, '{}_ZShape'.format(curve_object))
    cmds.setAttr('{}.overrideEnabled'.format(z_shape), 1)
    cmds.setAttr('{}.overrideColor'.format(z_shape), 6)

    x_arrow = cmds.duplicate(curve_object)[0]
    x_shape = cmds.listRelatives(x_arrow, s=True)[0]
    x_shape = cmds.rename(x_shape, '{}_XShape'.format(curve_object))
    cmds.setAttr('{}.overrideEnabled'.format(x_shape), 1)
    cmds.setAttr('{}.overrideColor'.format(x_shape), 13)

    cmds.setAttr('{}.rotateX'.format(z_arrow), 90)
    cmds.setAttr('{}.rotateZ'.format(x_arrow), -90)
    cmds.makeIdentity(z_arrow, x_arrow, a=True, r=True)
    cmds.parent(z_shape, x_shape, curve_object, r=True, s=True)
    cmds.delete(z_arrow, x_arrow)
    cmds.select(curve_object, r=True)
    return curve_object


def proxy(name='proxy_ctr'):
    vertex_position = [(0, 12, 0), (0, 1, 0), (-1, 0, 0), (-12, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, 12), (0, 0, 1),
                       (0, 1, 0), (1, 0, 0), (12, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 0, -12),
                       (0, 0, -1), (0, 1, 0), (0, 0, -1), (-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, -1, 0),
                       (0, -12, 0), (0, -1, 0), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def diamond(name='diamond_ctr'):
    vertex_position = [(0, 1, 0), (-1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0),
                       (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 1, 0), (0, 0, -1),
                       (-1, 0, 0), (0, -1, 0), (0, 0, -1),
                       (1, 0, 0), (0, -1, 0), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def pyramid(name='pyramid_ctr'):
    vertex_position = [(0, 0, 0), (0, -0.7, 0.7), (0.7, -0.7, 0), (0, 0, 0), (0.7, -0.7, 0), (0, -0.7, -0.7), (0, 0, 0),
                       (0, -0.7, -0.7), (-0.7, -0.7, 0), (0, 0, 0), (-0.7, -0.7, 0), (0, -0.7, 0.7)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def cube(name='cube_ctr'):
    vertex_position = [(1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                       (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1),
                       (-1, 1, 1), (-1, -1, 1), (1, -1, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def square(name='square_ctr'):
    vertex_position = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)]
    vertex_number = [0, 1, 2, 3, 4]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def knot(name='knot_ctr'):
    vertex_position = [(0, 0, 1), (0, -0.5, 0.866), (0, -0.866, 0.5), (0, -1, 0), (0.5, -0.866, 0),
                       (0.866, -0.5, 0), (1, 0, 0), (0.866, 0, -0.5), (0.5, 0, -0.866), (0, 0, -1),
                       (0, -0.5, -0.866), (0, -0.866, -0.5), (0, -1, 0), (-0.5, -0.866, 0),
                       (-0.866, -0.5, 0), (-1, 0, 0), (-0.866, 0, 0.5), (-0.5, 0, 0.866), (0, 0, 1),
                       (0.5, 0, 0.866), (0.866, 0, 0.5), (1, 0, 0), (0.866, 0.5, 0), (0.5, 0.866, 0),
                       (0, 1, 0), (0, 0.866, -0.5), (0, 0.5, -0.866), (0, 0, -1), (-0.5, 0, -0.866),
                       (-0.866, 0, -0.5), (-1, 0, 0), (-0.866, 0.5, 0), (-0.5, 0.866, 0), (0, 1, 0),
                       (0, 0.866, 0.5), (0, 0.5, 0.866), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23,
                     24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def quad_arrow(name='quadArrow_ctr'):
    vertex_position = [(1, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (1, 0, -1),
                       (1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -1),
                       (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-1, 0, 1),
                       (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                     22, 23, 24]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def circle(name='circle_ctr'):
    curve_object = cmds.circle(n=name, r=1, nr=(0, 1, 0), ch=False)
    return curve_object[0]


def cone(name='cone_ctr'):
    vertex_position = ([(-0.5, -1, 0.866025), (0, 1, 0), (0.5, -1, 0.866025), (-0.5, -1, 0.866025),
                        (-1, -1, -1.5885e-07), (0, 1, 0), (-1, -1, -1.5885e-07), (-0.5, -1, -0.866026),
                        (0, 1, 0), (0.5, -1, -0.866025), (-0.5, -1, -0.866026), (0.5, -1, -0.866025),
                        (0, 1, 0), (1, -1, 0), (0.5, -1, -0.866025), (1, -1, 0), (0.5, -1, 0.866025)])
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def single_arrow(name="arrow_ctr"):
    vertex_position = [(0, 1.003235, 0), (0.668823, 0, 0), (0.334412, 0, 0), (0.334412, -0.167206, 0),
                       (0.334412, -0.501617, 0), (0.334412, -1.003235, 0), (-0.334412, -1.003235, 0),
                       (-0.334412, -0.501617, 0), (-0.334412, -0.167206, 0), (-0.334412, 0, 0),
                       (-0.668823, 0, 0), (0, 1.003235, 0)]

    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]
    curve_object = cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object))
    return curve_object


def line_between(obj1, obj2, name=None):
    if not name or not isinstance(name, str):
        name = obj1
    pos1 = cmds.xform(obj1, q=True, ws=True, t=True)
    pos2 = cmds.xform(obj2, q=True, ws=True, t=True)
    vertex_position = [tuple(pos1), tuple(pos2)]
    vertex_number = [0, 1]
    curve_object = cmds.curve(n='{}_IK_crv'.format(name), d=1, p=vertex_position, k=vertex_number)

    root_cluster = cmds.cluster(cmds.ls('{}.cv[0]'.format(curve_object), fl=True), n='{}_IK_root'.format(name))
    end_cluster = cmds.cluster(cmds.ls('{}.cv[1]'.format(curve_object), fl=True), n='{}_IK_end'.format(name))
    cmds.setAttr('{}Shape.visibility'.format(root_cluster[-1]), 0)
    cmds.setAttr('{}Shape.visibility'.format(end_cluster[-1]), 0)
    cmds.setAttr('{}.inheritsTransform'.format(curve_object), 0)

    cmds.parentConstraint(obj1, root_cluster)
    cmds.parentConstraint(obj2, end_cluster)
    cmds.select(curve_object, r=True)
    cmds.TemplateObject()

    group = cmds.group(root_cluster, end_cluster, curve_object, n='{}_cluster_grp'.format(name))
    return group


def replace(shape):
    selected = cmds.ls(sl=True)

    for each in selected:
        if shape == 'circle':
            curve = circle()
        elif shape == 'drop':
            return
        elif shape == 'diamond':
            curve = diamond()
        elif shape == 'knot':
            curve = knot()
        elif shape == 'square':
            curve = square()
        elif shape == 'star':
            return
        elif shape == 'quad_arrow':
            curve = quad_arrow()
        elif shape == 'cube':
            curve = cube()
        else:
            return

        each_shape = cmds.listRelatives(each, s=True, f=True)
        curve_shape = cmds.listRelatives(curve, s=True, f=True)

        null = cmds.group(em=True)
        cmds.parent(each_shape, null, r=True, s=True)
        cmds.delete(null)

        cmds.rename(curve_shape, '{}Shape'.format(each))
        cmds.parent(cmds.listRelatives(curve, s=True, f=True), each, r=True, s=True)
        cmds.delete(curve)
    cmds.select(selected, r=True)
