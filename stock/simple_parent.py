##################################################################################
#                                                                                #
# Simple Parent v 0.1                                                            #
#                                                                                #
##################################################################################
#                                                                                #
# ^ Deleting constraints from node/parent/child.                                 #
# ^ Listing scene constraints (not implemented yet)                              #
#                                                                                #
##################################################################################
import maya.cmds as cmds

class constraint:
    def __init__(self, node, attrs):
      self.node = node
      self.type = cmds.ls(node, st=True)[1]
      self.child = cmds.listRelatives(node, p=1)[0]
      self.parent = cmds.listConnections(node+".target")[0]
      self.attrs = attrs

    def printObject(self):
        print "**********"
        print "Type: " + self.type
        print "Parent: " + self.parent
        print "Child: " + self.child
        print "Node: " + self.node
        print "Attrs: "
        print self.attrs
        print "**********"
      
def listSceneConstraints():
    parentConstraints = cmds.ls(typ="parentConstraint")
    pointConstraints = cmds.ls(typ="pointConstraint")
    orientConstraints = cmds.ls(typ="orientConstraint")
    scaleConstraints = cmds.ls(typ="scaleConstraint")
    aimConstraints = cmds.ls(typ="aimConstraint")
    
    return parentConstraints + pointConstraints + orientConstraints + scaleConstraints + aimConstraints

def getConstraint(c):
    #Check if parent is a reference
    try:
        cmds.referenceQuery(c, f=1)
        ref = True
    except:
        ref = False
    
    if not ref: 
        cTypeName = cmds.ls(c, st=True)[1].split("Constraint")[0]
        cBlendAttrName = "blend"+cTypeName[0].upper()+cTypeName[1:]    
        cBlendAttrs = []
        ref = 0
        
        #Look for blend attributes
        try:
            for a in cmds.listAttr(cmds.listRelatives(c, p=1)[0], k=True):
                if len(a.split(cBlendAttrName)) > 1:
                    cBlendAttrs.append(a)
        except:
            pass
            
        return constraint(c, cBlendAttrs)

def getSceneConstraints():      
    constraints = listSceneConstraints()
    constraintObjects = []
    
    for c in constraints:
        constraintObjects.append(getConstraint(c))
            
    return constraintObjects
            
def deleteConstraint(c):
    obj = getConstraint(c)
    cmds.delete(c)
    
    obj.printObject()

    print "Deleting "+c
    
    for attr in obj.attrs:  
        try:
            if(cmds.objExists(obj.child+"."+attr)):
                print "Deleting "+obj.child+"."+attr
                cmds.deleteAttr(obj.child+"."+attr)
        except:
            pass

def deleteNodeConstraints(node):
    #If constraint is selected
    if len(cmds.ls(node, st=True)[1].split("Constraint")) == 2:
        if getConstraint(node):
            deleteConstraint(node)
            
    else:
        #If constraint-child is selected
        try:
            children = cmds.listRelatives(node, c=1)
            for c in children:
                if len(cmds.ls(c, st=True)[1].split("Constraint")) == 2:
                    if getConstraint(c):
                        deleteConstraint(c)
        except:
            pass
            
        #If constraint-parent is selected
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
                if getConstraint(c):
                    deleteConstraint(c)
            except:
                pass
            
def run():
    sel = cmds.ls(sl=1)
    
    for s in sel:
        deleteNodeConstraints(s)
        
    '''
    constraints = getSceneConstraints()
    
    for c in constraints:
        c.printObject()
    '''
