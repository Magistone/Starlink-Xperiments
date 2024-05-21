import icmplib

def collect_traceroute_against_target(target: str):
    trace = dict()
    hops = icmplib.traceroute(target, 1, 0.005)
    for hop in hops:
        trace[hop.distance] = {'address': hop.address, 'rtt_ms': hop.avg_rtt}
    return trace

def setup(setup):
    pass

def collect(config):
    data = dict()
    for target in config['targets']:
        data[target] = collect_traceroute_against_target(target)

    return data
