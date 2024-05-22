import importlib
import time


def write_data(data):
    #MongoDB writer
    print(data)

def delay(start_time: str | None):
    #delay starting scheduled tasks
    if start_time == None:
        return
    
    time_struct = time.strptime(start_time, "%a, %d %b %Y %H:%M:%S %Z") #RFC7231, "Sun, 06 Nov 1994 08:49:37 GMT"
    target_timestamp = round(time.mktime(time_struct))
    current_timestamp = round(time.mktime(time.gmtime())) # DO NOT GET TIME with time.time() - it's wrong value
    diff = target_timestamp - current_timestamp
    if diff <= 0:
        return
    time.sleep(diff)

def create(module: str, setup: dict | None):
    mod = importlib.import_module('modules.' + module)
    mod.setup(setup)
    return mod

def run(mod, task_config: dict):
    task_stop_time = task_config.get('stop')
    forever = task_config.get('forever')
    while((not is_time_past_deadline(task_stop_time)) or forever):
        start_time = time.time_ns()
        data = mod.collect(task_config.get('config'))
        write_data(data)
        stop_time = time.time_ns()
        time_diff = (stop_time - start_time)/1e9

        sleep_time = task_config['period'] - time_diff
        if sleep_time <= 0:
            continue
        time.sleep(sleep_time) # => starts spaced by 'period'

def schedule(config: dict):
    delay(config.get('start'))
    mod = create(config['module'], config.get('setup'))
    run(mod, config)

def is_time_past_deadline(deadline: str):
    time_struct = time.strptime(deadline, "%a, %d %b %Y %H:%M:%S %Z") #RFC7231, "Sun, 06 Nov 1994 08:49:37 GMT"
    target_timestamp = round(time.mktime(time_struct))
    current_timestamp = round(time.mktime(time.gmtime())) # DO NOT GET TIME with time.time() - it's wrong value
    diff = target_timestamp - current_timestamp
    return diff < 0