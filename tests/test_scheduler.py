import sys

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import datetime
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
    'config': {}, #REQUIRED, Runtime data for collection (can be null/none/empty)
    'tags': {}, #OPTIONAL, inject custom tags into all entries
}

def test_delay():
    target_time = time.gmtime(time.time() + 10)
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    inst = scheduler.Scheduler('delay', time_str, None, None, {}, False, True)
    inst.delay()
    curr_time = time.gmtime(time.time())
    assert(curr_time >= target_time)

def test_create():
    inst = scheduler.Scheduler('ip', None, None, None, {}, False, True)
    mod = inst.create()
    data = mod.collect(None)
    for key in data.keys():
        assert(key in ['v4', 'v6'])

def test_create_non_existent():
    inst = scheduler.Scheduler('non_existent', None, None, None, {}, False, True)
    try:
        mod = inst.create()
        assert(False)
    except:
        pass

def test_time_past_true():
    inst = scheduler.Scheduler('non_existent', None, None, None, {}, False, True)
    resp = inst.is_time_past_deadline("Sun, 06 Nov 1994 08:49:37 GMT")
    assert(resp)

def test_time_past_false():
    target_time = time.gmtime(time.time() + 100)
    time_str = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    inst = scheduler.Scheduler('non_existent', None, None, None, {}, False, True)
    resp = inst.is_time_past_deadline(time_str)
    assert(not resp)

def test_inject_metadata():
    inst = scheduler.Scheduler('delay', None, None, None, {'foo': 'bar', 'cookies': 'yummy'}, False, True)
    data = {'temp': 5, 'pressure': 'deez'}

    new_data = inst.inject_meta_data(data)

    assert(new_data['metadata']['foo'] == 'bar')
    assert(new_data['metadata']['cookies'] == 'yummy')
    assert(new_data['metadata']['job_name'] == 'delay')
    assert(isinstance(new_data['timestamp'], datetime.datetime))
    assert(new_data['temp'] == 5)
    assert(new_data['pressure'] == 'deez')

def test_full_module_no_config(capsys):
    target_time = time.gmtime(time.time() + 12)
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    config = dict()
    config['module'] = 'space_weather'
    config['stop'] = end_time
    config['forever'] = False
    config['period'] = 5
    config['start'] = None

    scheduler.schedule(config, dbg=True)
    output = capsys.readouterr()
    finds_R = re.findall(r"'R': '[0-5]'", output.out)
    finds_S = re.findall(r"'S': '[0-5]'", output.out)
    finds_G = re.findall(r"'G': '[0-5]'", output.out)
    finds_timestamp = re.findall(r"'timestamp': datetime.datetime\(.*?\)", output.out)
    finds_name = re.findall(r"'metadata': {'job_name': 'space_weather'}", output.out)
    assert(len(finds_R) == 3)
    assert(len(finds_S) == 3)
    assert(len(finds_G) == 3)
    assert(len(finds_timestamp) == 3)
    assert(len(finds_name) == 3)

def test_full_module_with_config(capsys):
    target_time = time.gmtime(time.time() + 14)
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    config = dict()
    config['module'] = 'ping'
    config['stop'] = end_time
    config['forever'] = False
    config['period'] = 5
    config['start'] = None
    config['setup'] = {'test': 'Setting up'}
    config['config'] = {'targets': ['1.1.1.1', '8.8.8.8']}

    scheduler.schedule(config, dbg=True)
    output = capsys.readouterr()
    finds_8 = re.findall(r"'target': '8\.8\.8\.8'", output.out)
    finds_1 = re.findall(r"'target': '1\.1\.1\.1'", output.out)
    finds_setup = re.findall(r"Setting up", output.out)
    assert(len(finds_8) == 3)
    assert(len(finds_1) == 3)
    assert(len(finds_setup) == 1)

def test_delayed_start(capsys):
    target_time = time.gmtime(time.time() + 12)
    end_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_time)
    target_start_time = time.gmtime(time.time() + 5)
    start_time = time.strftime("%a, %d %b %Y %H:%M:%S %Z", target_start_time)
    config = dict()
    config['module'] = 'space_weather'
    config['stop'] = end_time
    config['start'] = start_time
    config['forever'] = False
    config['period'] = 5

    scheduler.schedule(config, dbg=True)

    output = capsys.readouterr()
    finds_R = re.findall(r"'R': '[0-5]'", output.out)
    finds_S = re.findall(r"'S': '[0-5]'", output.out)
    finds_G = re.findall(r"'G': '[0-5]'", output.out)
    finds_timestamp = re.findall(r"'timestamp': datetime.datetime\(.*?\)", output.out)
    finds_name = re.findall(r"'metadata': {'job_name': 'space_weather'}", output.out)
    assert(len(finds_R) == 2)
    assert(len(finds_S) == 2)
    assert(len(finds_G) == 2)
    assert(len(finds_timestamp) == 2)
    assert(len(finds_name) == 2)