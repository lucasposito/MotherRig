import maya.cmds as cmds


def manipulate_name(full_name, action=None, name=None, position=None, separator='_'):
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
        elif position < -1:
            position += 1
        name_list.insert(position, name)
        new_name = separator.join(name_list)
        return new_name

    if action == 'add':
        if position is -1:
            name_list.append(name)
            new_name = separator.join(name_list)
            return new_name
        elif position < -1:
            position += 1
        name_list.insert(position, name)
        new_name = separator.join(name_list)
        return new_name

    if action == 'check':
        if name_list[position] == name:
            return True


def check_selection(suffix='pxy'):
    selected = cmds.ls(sl=True)
    if len(selected) is not 1:
        return
    if manipulate_name(selected[0], 'check', suffix, -1) is True:
        new_name = manipulate_name(selected[0], 'delete', position=-1)
        return new_name
