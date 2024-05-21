import icmplib

def collect_ping_against_target(target: str):
    data = dict()
    host = icmplib.ping(target, count=3, interval=0.005)
    data['rtt_ms'] = host.avg_rtt
    if target != host.address:
        data['address'] = host.address
    return data

def setup(setup):
    pass

def collect(config):
    data = dict()
    for target in config['targets']:
        data[target] = collect_ping_against_target(target)

    return data