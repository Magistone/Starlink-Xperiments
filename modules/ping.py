import icmplib
import asyncio
from collections import namedtuple

pingResult = namedtuple('pingResult', ['target', 'ping'])

async def collect_ping_against_target(target: str):
    data = dict()
    try:
        host = await icmplib.async_ping(target, count=1, interval=0.005)
        data['rtt_ms'] = host.avg_rtt
        if target != host.address:
            data['address'] = host.address
        return pingResult(target, data)
    except icmplib.NameLookupError:
        return pingResult(target, None)

def setup(setup: dict | None):
    if isinstance(setup, dict):
        print(setup.get('test'))
    pass

def collect(config):
    data = list()
    results:list[pingResult] = asyncio.run(run(config['targets']))

    for result in results:
        if result.ping:
            data_point = result.ping
            data_point['metadata'] = dict()
            data_point['metadata']['target'] = result.target
            data.append(data_point)

    return data

async def run(targets):
    results = list()
    tasks = list()
    for target in targets:
        tasks.append(asyncio.create_task(collect_ping_against_target(target)))
    
    for task in tasks:
        results.append(await task)
    return results