import maya.cmds as cmds

import core.utility as utility

from core.ik_fk_switcher import ikfkUI
from core.import_fbx_anim import ImportAnimation
from core.simple_parent import run
import core.rig_ui as rig_ui


def _null(*args):
    pass


def _import_fbx(*args):
    ImportAnimation.show_ui()


def _ik_fk_switcher(*args):
    ikfkUI.show_ui()


def _gwent_autorig(*args):
    # GwentUI.show_ui()
    reload(rig_ui)
    try:
        gwent_ui.close()
    except:
        pass
    gwent_ui = rig_ui.GwentUI()
    gwent_ui.show()


def _clean_namespaces(*args):
    utility.clean_namespaces()


def _simple_parent(*args):
    run()


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
        self.add_button(label='RIG', command=_gwent_autorig)
        self.add_button(label='NSpace', command=_clean_namespaces)
        self.add_button(label='Del', command=_simple_parent)

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
