import maya.cmds as cmds
import mCore
import mParts


def _null(*args):
    pass


def _import_fbx(*args):
    mParts.ImportAnimation.show_ui()


def _ik_fk_switcher(*args):
    mParts.ikfkUI.show_ui()


def _mother_rig(*args):
    try:
        m_rig.close()
    except:
        pass
    m_rig = mParts.MotherUI()
    m_rig.show()


def _zero_out(*args):
    mParts.ControlUI.show_ui()


def _clean_namespaces(*args):
    mCore.utility.clean_namespaces()


def _select_joints(*args):
    cmds.select(mCore.utility.joint_hierarchy(), r=True)


def _simple_parent(*args):
    mCore.simple_parent.run()


class MotherShelf(object):
    def __init__(self):
        self.name = 'Mother'
        self.icon_path = ''

        self._clean_old_shelf()
        self.build()

    def build(self):
        self.add_button(label='Import', command=_import_fbx)
        self.add_button(label='IkFk', command=_ik_fk_switcher)
        cmds.separator(style='single', w=10)
        self.add_button(label='RIG', command=_mother_rig)
        self.add_button(label='ZERO', command=_zero_out)
        self.add_button(label='NSpace', command=_clean_namespaces)
        self.add_button(label='SEL', command=_select_joints)
        self.add_button(label='DEL', command=_simple_parent)

    def add_button(self, label, icon='commandButton.png', command=_null):
        cmds.setParent(self.name)
        if icon:
            icon = self.icon_path + icon
        cmds.shelfButton(width=37, height=37, image=icon, l=label, command=command,
                         imageOverlayLabel=label)

    def add_menu_item(self, parent, label, command=_null, icon=''):
        if icon:
            icon = self.icon_path + icon
        return cmds.menuItem(p=parent, l=label, c=command, i='')

    def _clean_old_shelf(self):
        try:
            cmds.deleteUI(self.name)
        except RuntimeError:
            pass

        cmds.shelfLayout(self.name, p='ShelfLayout')


MotherShelf()
