import maya.cmds as cmds


color_value = {'grey': 3, 'blue': 6, 'red': 13, 'yellow': 17, 'lightBlue': 18, 'rose': 20, 'green': 28}


def curve_color(value=6):
    object_list = cmds.listRelatives(cmds.ls(sl=True, l=True), s=True, f=True)
    for each in object_list:
        cmds.setAttr('{}.overrideEnabled'.format(each), 1)
        cmds.setAttr('{}.overrideColor'.format(each), value)
    cmds.select(cl=True)

    
def curve_size(value=1.1):
    selected = cmds.ls(sl=True)
    for each in selected:
        shapes = cmds.listRelatives(each, s=True, f=True)
        curve_pivot = cmds.xform(each, q=True, ws=True, piv=True)
        del (curve_pivot[2:-1])
        for crv in shapes:
            cmds.scale(value, value, value, '{}.cv[*]'.format(crv), r=True, p=curve_pivot)


def diamond(name='diamond_ctr'):
    vertex_position = [(0, 1, 0), (-1, 0.00278996, 6.18172e-08), (0, 0, 1), (0, 1, 0), (1, 0.00278996, 0),
                       (0, 0, 1), (1, 0.00278996, 0), (0, 0, -1), (0, 1, 0), (0, 0, -1),
                       (-1, 0.00278996, 6.18172e-08), (0, -1, 0), (0, 0, -1),
                       (1, 0.00278996, 0), (0, -1, 0), (0, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    return curve_object


def cube(name='cube_ctr'):
    vertex_position = [(1, 1, 1), (1, 1, -1), (-1, 1, -1), (-1, 1, 1), (1, 1, 1), (1, -1, 1), (1, -1, -1),
                       (1, 1, -1), (-1, 1, -1), (-1, -1, -1), (1, -1, -1), (-1, -1, -1), (-1, -1, 1),
                       (-1, 1, 1), (-1, -1, 1), (1, -1, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    return curve_object


def square(name='square_ctr'):
    vertex_position = [(-1, 0, -1), (1, 0, -1), (1, 0, 1), (-1, 0, 1), (-1, 0, -1)]
    vertex_number = [0, 1, 2, 3, 4]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
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
    return curve_object


def quad_arrow(name='quadArrow_ctr'):
    vertex_position = [(1, 0, 1), (3, 0, 1), (3, 0, 2), (5, 0, 0), (3, 0, -2), (3, 0, -1), (1, 0, -1),
                       (1, 0, -3), (2, 0, -3), (0, 0, -5), (-2, 0, -3), (-1, 0, -3), (-1, 0, -1),
                       (-3, 0, -1), (-3, 0, -2), (-5, 0, 0), (-3, 0, 2), (-3, 0, 1), (-1, 0, 1),
                       (-1, 0, 3), (-2, 0, 3), (0, 0, 5), (2, 0, 3), (1, 0, 3), (1, 0, 1)]
    vertex_number = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21,
                     22, 23, 24]
    curve_object = [cmds.curve(n=name, d=1, p=vertex_position, k=vertex_number)]
    return curve_object


def circle(name='circle_ctr'):
    curve_object = cmds.circle(n=name, r=1, nr=(0, 1, 0), ch=False)
    return curve_object
