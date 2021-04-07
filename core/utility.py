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
        try:
            result = name_list.index(name)
            return result
        except ValueError:
            return


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
        
        
def check_selection(suffix='pxy'):
    selected = cmds.ls(sl=True)
    if len(selected) is not 1:
        return
    if manipulate_name(selected[0], 'check', suffix, -1) is True:
        new_name = manipulate_name(selected[0], 'delete', position=-1)
        return new_name
