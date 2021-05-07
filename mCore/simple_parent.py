import maya.cmds as cmds


class Constraint:
    def __init__(self, node, attrs):
        self.node = node
        self.type = cmds.ls(node, st=True)[1]
        self.child = cmds.listRelatives(node, p=1)[0]
        self.parent = cmds.listConnections(node + ".target")[0]
        self.attrs = attrs

    def print_object(self):
        print("**********")
        print("Type: " + self.type)
        print("Parent: " + self.parent)
        print("Child: " + self.child)
        print("Node: " + self.node)
        print("Attrs: ")
        print(self.attrs)
        print("**********")


def list_scene_constraints():
    parent_constraints = cmds.ls(typ="parentConstraint")
    point_constraints = cmds.ls(typ="pointConstraint")
    orient_constraints = cmds.ls(typ="orientConstraint")
    scale_constraints = cmds.ls(typ="scaleConstraint")
    aim_constraints = cmds.ls(typ="aimConstraint")

    return parent_constraints + point_constraints + orient_constraints + scale_constraints + aim_constraints


def get_constraint(c):
    # Check if parent is a reference
    try:
        cmds.referenceQuery(c, f=1)
        ref = True
    except:
        ref = False

    if not ref:
        c_type_name = cmds.ls(c, st=True)[1].split("Constraint")[0]
        c_blend_attr_name = "blend" + c_type_name[0].upper() + c_type_name[1:]
        c_blend_attrs = []
        ref = 0

        # Look for blend attributes
        try:
            for a in cmds.listAttr(cmds.listRelatives(c, p=1)[0], k=True):
                if len(a.split(c_blend_attr_name)) > 1:
                    c_blend_attrs.append(a)
        except:
            pass

        return Constraint(c, c_blend_attrs)


def get_scene_constraints():
    constraints = list_scene_constraints()
    constraint_objects = []

    for c in constraints:
        constraint_objects.append(get_constraint(c))

    return constraint_objects


def delete_constraint(c):
    obj = get_constraint(c)
    cmds.delete(c)

    obj.print_object()

    print("Deleting " + c)

    for attr in obj.attrs:
        try:
            if cmds.objExists(obj.child + "." + attr):
                print("Deleting " + obj.child + "." + attr)
                cmds.deleteAttr(obj.child + "." + attr)
        except:
            pass


def delete_node_constraints(node):
    # If constraint is selected
    if len(cmds.ls(node, st=True)[1].split("Constraint")) == 2:
        if get_constraint(node):
            delete_constraint(node)

    else:
        # If constraint-child is selected
        try:
            children = cmds.listRelatives(node, c=1)
            for c in children:
                if len(cmds.ls(c, st=True)[1].split("Constraint")) == 2:
                    if get_constraint(c):
                        delete_constraint(c)
        except:
            pass

        # If constraint-parent is selected
        pc = []
        ptc = []
        oc = []
        sc = []
        ac = []

        try:
            if len(cmds.listConnections(node, t="parentConstraint")) > 0:
                pc = cmds.listConnections(node, t="parentConstraint")
        except:
            pass

        try:
            if len(cmds.listConnections(node, t="pointConstraint")) > 0:
                ptc = cmds.listConnections(node, t="pointConstraint")
        except:
            pass

        try:
            if len(cmds.listConnections(node, t="orientConstraint")) > 0:
                oc = cmds.listConnections(node, t="orientConstraint")
        except:
            pass

        try:
            if len(cmds.listConnections(node, t="scaleConstraint")) > 0:
                sc = cmds.listConnections(node, t="scaleConstraint")
        except:
            pass

        try:
            if len(cmds.listConnections(node, t="aimConstraint")) > 0:
                ac = cmds.listConnections(node, t="aimConstraint")
        except:
            pass

        constraints = pc + ptc + oc + sc + ac

        for c in constraints:
            try:
                if get_constraint(c):
                    delete_constraint(c)
            except:
                pass


def run():
    sel = cmds.ls(sl=1)

    for s in sel:
        delete_node_constraints(s)

    '''
    constraints = get_scene_constraints()
    
    for c in constraints:
        c.printObject()
    '''
