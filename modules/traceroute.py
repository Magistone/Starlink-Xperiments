import icmplib
import asyncio

async def collect_traceroute_against_target(target: str):
    trace = dict()
    hops = icmplib.traceroute(target, 1, 0.005)
    for hop in hops:
        trace[hop.distance] = {'address': hop.address, 'rtt_ms': hop.avg_rtt}
    return (target, trace)

def setup(setup):
    pass

def collect(config):
    data = dict()
    results = asyncio.run(run(config['targets']))
    for result in results:
        data[result[0]] = result[1]

    return data

async def run(targets):
    tasks = list()
    results = list()
    for target in targets:
        tasks.append(asyncio.create_task(collect_traceroute_against_target(target)))
    
    for task in tasks:
        results.append(await task)
    return results