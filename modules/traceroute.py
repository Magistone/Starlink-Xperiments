import icmplib

def collect_traceroute_against_target(target: str):
    icmplib.traceroute(target, 1)

def setup():
    pass

def collect(config):
    #parse config
    #for each target
    data = collect_traceroute_against_target("T A R G E T")
    
    return data