import maya.cmds as cmds


color_value = {'grey': 3, 'blue': 6, 'red': 13, 'yellow': 17, 'lightBlue': 18, 'rose': 20, 'green': 28}


def curve_color(value=6):
    object_list = cmds.listRelatives(cmds.ls(sl=True, l=True), s=True, f=True)
    for each in object_list:
        cmds.setAttr('{}.overrideEnabled'.format(each), 1)
        cmds.setAttr('{}.overrideColor'.format(each), value)
    cmds.select(cl=True)


def curve_rgb_color(r=0, g=0, b=1):
    value = (r, g, b)
    rgb = ('R', 'G', 'B')
    object_list = cmds.listRelatives(cmds.ls(sl=True, l=True), s=True, f=True)
    for each in object_list:
        cmds.setAttr('{}.overrideRGBColors'.format(each), 1)
        for a, b in zip(rgb, value):
            cmds.setAttr('{}.overrideColor{}'.format(each, a), b)
    cmds.select(cl=True)


def curve_size(value=1.1):
    selected = cmds.ls(sl=True)
    for each in selected:
        shapes = cmds.listRelatives(each, s=True, f=True)
        curve_pivot = cmds.xform(each, q=True, ws=True, piv=True)
        del (curve_pivot[2:-1])
        for crv in shapes:
            cmds.scale(value, value, value, '{}.cv[*]'.format(crv), r=True, p=curve_pivot)


def normalize_size(factor=0.8):
    objects = [a for a in cmds.ls(sl=True) if cmds.listRelatives(a, s=True, f=True)]
    for child in cmds.listRelatives(cmds.ls(sl=True), ad=True, f=True):
        if not cmds.listRelatives(child, s=True, f=True):
            continue
        objects.append(child)
    cmds.select(objects, r=True)


def proxy(name='proxy_ctr'):
    vertex_position = [(0, 12, 0), (0, 1, 0), (-1, 0, 0), (-12, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, 12), (0, 0, 1),
                       (0, 1, 0), (1, 0, 0), (12, 0, 0), (1, 0, 0), (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 0, -12),
                       (0, 0, -1), (0, 1, 0), (0, 0, -1), (-1, 0, 0), (0, -1, 0), (0, 0, -1), (1, 0, 0), (0, -1, 0),
                       (0, -12, 0), (0, -1, 0), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
    return curve_object


def diamond(name='diamond_ctr'):
    vertex_position = [(0, 1, 0), (-1, 0, 0), (0, 0, 1), (0, 1, 0), (1, 0, 0),
                       (0, 0, 1), (1, 0, 0), (0, 0, -1), (0, 1, 0), (0, 0, -1),
                       (-1, 0, 0), (0, -1, 0), (0, 0, -1),
                       (1, 0, 0), (0, -1, 0), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
    return curve_object


def cube(name='cube_ctr'):
    vertex_position = [(1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                       (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1),
                       (-1, 1, 1), (-1, -1, 1), (1, -1, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
    return curve_object


def square(name='square_ctr'):
    vertex_position = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)]
    vertex_number = [0, 1, 2, 3, 4]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
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
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
    return curve_object


def quad_arrow(name='quadArrow_ctr'):
    vertex_position = [(1, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (1, 0, -1),
                       (1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -1),
                       (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-1, 0, 1),
                       (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                     22, 23, 24]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    shape = cmds.listRelatives(curve_object, s=True, f=True)
    cmds.rename(shape, '{}Shape'.format(curve_object[0]))
    return curve_object


def circle(name='circle_ctr'):
    curve_object = cmds.circle(n=name, r=1, nr=(0, 1, 0), ch=False)
    return curve_object
