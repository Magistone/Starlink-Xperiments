import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import scheduler
import time
import re

full_config = {
    'module': "ip", #REQUIRED
    'start': "Tue, 68 HH:MM:SS Z", #OPTIONAL
    'stop': "Wed, 69 HH:MM:SS Z", #REQUIRED one of: stop, forever
    'period': 15, #REQUIRED
    'forever': True, #REQUIRED one of: stop, forever
    'setup': None, #REQUIRED, Setup data for module (can be null/none/empty)
    'config': {} #REQUIRED, Runtime data for collection (can be null/none/empty)
}

def test_delay():
    target_time = time.gmtime(time.time() + 5)
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    scheduler.delay(time_str)
    curr_time = time.gmtime(time.time())
    assert(curr_time >= target_time)

def test_create():
    mod = scheduler.create('ip', None)
    data = mod.collect(None)
    for key in data.keys():
        assert(key in ['v4', 'v6'])

def test_create_non_existent():
    try:
        mod = scheduler.create('non_existent', None)
        assert(False)
    except:
        pass

def test_time_past_true():
    resp = scheduler.is_time_past_deadline("Sun, 06 Nov 1994 08:49:37 GMT")
    assert(resp)

def test_time_past_false():
    target_time = time.gmtime(time.time() + 100)
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    resp = scheduler.is_time_past_deadline(time_str)
    assert(not resp)

def test_full_module_no_config(capsys):
    target_time = time.gmtime(time.time() + 12)
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    config = dict()
    config['module'] = 'space_weather'
    config['stop'] = end_time
    config['forever'] = False
    config['period'] = 5
    config['start'] = None

    scheduler.schedule(config)
    output = capsys.readouterr()
    finds = re.findall(r"{'R': '[0-5]', 'S': '[0-5]', 'G': '[0-5]'}", output.out)
    assert(len(finds) >= 2)

def test_full_module_with_config(capsys):
    target_time = time.gmtime(time.time() + 14)
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    config = dict()
    config['module'] = 'ping'
    config['stop'] = end_time
    config['forever'] = False
    config['period'] = 5
    config['start'] = None
    config['config'] = {'targets': ['1.1.1.1', '8.8.8.8']}

    scheduler.schedule(config)
    output = capsys.readouterr()
    finds_8 = re.findall(r"'8\.8\.8\.8': {'rtt_ms': [\d\.]+}", output.out)
    finds_1 = re.findall(r"'1\.1\.1\.1': {'rtt_ms': [\d\.]+}", output.out)
    assert(len(finds_8) >= 2)
    assert(len(finds_1) >= 2)