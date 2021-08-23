import maya.cmds as cmds
from random import uniform as rd

import mCore


class Blank:
    def __init__(self, name):
        self.main = []

        self.self_inner = None
        self.self_outer = None

        self.parent_inner = None
        self.parent_outer = None

        self.connectors = {'root': []}

    def set_main(self):
        pass

    def set_ik(self):
        pass

    def set_fk(self):
        pass

    def set_ik_fk(self):
        pass
