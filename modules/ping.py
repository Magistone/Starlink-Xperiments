import icmplib

def collect_ping_against_target(target: str):
    icmplib.ping(target, count=1)

def setup():
    pass

def collect(config):
    #parse config
    #for all targets in config
    data = collect_ping_against_target("T A R G E T")
    return data