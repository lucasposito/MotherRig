from tree import Structure


_NEW_RIG_ = None


def create_proxy(info, *args):
    global _NEW_RIG_
    if not isinstance(_NEW_RIG_, Structure):
        _NEW_RIG_ = Structure()

    name = info['name']
    order = info['order']
    side = ['Right', 'Center', 'Left']
    type = ['IK', 'FK', 'IKFK']
    size = ['light', 'average', 'heavy']

    side = side[info['side']]
    type = type[info['type']]
    size = size[info['size']]

    module = info['module']

    module_data = [name, order, side, module, type, size]
    _NEW_RIG_.add_module(module_data)
