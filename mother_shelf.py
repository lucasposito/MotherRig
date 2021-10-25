import maya.cmds as cmds
import mCore
import mParts


def _null(*args):
    pass


def _import_fbx(*args):
    mParts.ImportAnimation.show_ui()


def _ik_fk_switcher(*args):
    mParts.ikfkUI.show_ui()


def _select_all_keyed(*args):
    mCore.utility.select_all_keyed()


def _select_all_controls(*args):
    mCore.utility.select_all_controls()


def _select_non_crv(*args):
    mCore.utility.select_non_crv()


def _mother_rig(*args):
    mParts.RigUI.show_ui()


def _zero_out(*args):
    mParts.ControlUI.show_ui()


def _clean_namespaces(*args):
    mCore.utility.clean_namespaces()


def _select_joints(*args):
    cmds.select(mCore.utility.joint_hierarchy(), r=True)


def _simple_parent(*args):
    mCore.simple_parent.run()


def _freeze_joints(*args):
    mCore.utility.freeze_joints()


def _skin_cluster_joints(*args):
    mCore.utility.skin_cluster_joints()


class MotherShelf(object):
    def __init__(self):
        self.name = 'Mother'
        self.icon_path = ''

        self._clean_old_shelf()
        self.build()

    def build(self):
        self.add_button(label='Import', command=_import_fbx)
        self.add_button(label='IkFk', command=_ik_fk_switcher)
        self.add_button(label='SelKey', command=_select_all_keyed)
        self.add_button(label='SelCtrl', command=_select_all_controls)
        self.add_button(label='notCRV', command=_select_non_crv)
        cmds.separator(style='single', w=10)

        self.add_button(label='RIG', command=_mother_rig)
        self.add_button(label='CTR', command=_zero_out)
        self.add_button(label='NSpace', command=_clean_namespaces)
        self.add_button(label='SelJnt', command=_select_joints)
        self.add_button(label='DelCst', command=_simple_parent)
        self.add_button(label='FreeJnt', command=_freeze_joints)
        self.add_button(label='SelSkn', command=_skin_cluster_joints)

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
