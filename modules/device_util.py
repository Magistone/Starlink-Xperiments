import modules.grpc as dish

def setup(setup):
    pass

def collect(config):
    if config.get('reboot'):
        dish.reboot()
    if config.get('stow'):
        dish.set_stow_state(not config.get('stow_operation'))

    return None
