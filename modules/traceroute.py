import icmplib
import asyncio
from collections import namedtuple

traceResult = namedtuple('traceResult', ['target', 'trace'])

async def collect_traceroute_against_target(target: str):
    trace = dict()
    try:
        hops = icmplib.traceroute(target, 1, 0.005) #replace with async when available in icmplib
        for hop in hops:
            trace[str(hop.distance)] = {'address': hop.address, 'rtt_ms': hop.avg_rtt}
        return traceResult(target, trace)
    except icmplib.NameLookupError:
        return traceResult(target, None)

def setup(setup):
    pass

def collect(config):
    data = list()
    results:list[traceResult] = asyncio.run(run(config['targets']))
    for result in results:
        if result.trace:
            data_point = result.trace
            data_point['metadata'] = dict()
            data_point['metadata']['target'] = result.target
            data.append(data_point)

    return data

async def run(targets):
    tasks = list()
    results = list()
    for target in targets:
        tasks.append(asyncio.create_task(collect_traceroute_against_target(target)))
    
    for task in tasks:
        results.append(await task)
    return results