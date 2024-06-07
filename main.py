from flask import Flask, request
import multiprocessing, time, subprocess, sys
import scheduler
from collections import namedtuple

Result = namedtuple('Result', ['result', 'error'])

app = Flask(__name__)

@app.post("/create")
def createJob():
    params = request.get_json()
    print(params)
    validated = validate_params(params)
    if not validated['valid']:
        return validated['message'], 400
    
    process = multiprocessing.Process(target=scheduler.schedule, args=(params,))
    process.start()

    #Quickly check whether spawned job crashed
    time.sleep(1)
    if process.is_alive():
        return "OK\n", 200
    return "Error\n", 500

@app.post("/install")
def installDependencies():
    params:dict = request.get_json()
    inst, err = install_dependencies(params)    
    
    return f'Installed: {",".join(map(str, inst))}\nFailed to install: {",".join(map(str, err))}\n', 200 if len(err) == 0 else 400

@app.post("/reboot")
def reboot():
    config = create_min_config()
    config['config']['reboot'] = True

    process = multiprocessing.Process(target=scheduler.schedule,args=(config, True))
    process.start()

    return 'Accepted\n', 202

@app.post("/stow")
def stow():
    config = create_min_config()
    obj = request.get_json()
    config['config']['stow_operation'] = obj.get('stow')
    config['config']['stow'] = True

    process = multiprocessing.Process(target=scheduler.schedule,args=(config, True))
    process.start()

    return 'Accepted\n', 202

@app.post("/validate")
def debug():
    obj = request.get_json()
    response = validate_params(obj)
    status = 200
    if not response['valid']:
        status = 400
    return response['message']+'\n', status


### methods that take care of small amount of processing. Not I/O dependent - easy to test

def install_dependencies(params: dict):
    installed = list()
    err = list()
    for mod in params.get('modules'):
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', mod])
            installed.append(mod)
        except:
            err.append(mod)

    return Result(installed, err)

def validate_params(obj: dict):
    mod = obj.get('module')     #REQUIRED
    per = obj.get('period')     #REQUIRED
    start = obj.get('start')    #OPT
    stop = obj.get('stop')      #REQUIRED one of: stop, forever
    forever = obj.get('forever')#REQUIRED one of: stop, forever
    setup = obj.get('setup')    #OPT
    config = obj.get('config')  #OPT

    valid = True
    msg = "Invalid configuration."

    if not stop and forever != True:
        valid = False
        msg += " Requires one of: stop, forever."

    if stop and not validate_date_format(stop):
        valid = False
        msg += " Invalid format for stop time."
    
    if start and not validate_date_format(start):
        valid = False
        msg += " Invalid format for start time."

    if not mod:
        valid = False
        msg += " Requires module parameter."
    
    if not per:
        valid = False
        msg += " Requires period parameter."
    else:
        try:
            float(per)
        except:
            valid = False
            msg += " Period must be a float/integer."
    
    if valid:
        msg = f"CONFIGURATION VALID. Parameters received: mod={mod}, period={per}, start={start}, stop={stop}, forever={forever}, setup={setup}, config={config}"

    return {'valid': valid, 'message': msg}

def validate_date_format(date:str):
    try:
        time.strptime(date, "%a, %d %b %Y %H:%M:%S %Z")
        return True
    except:
        return False
    

def create_min_config():
    return {
        'module': 'device_util',
        'period': 69,
        'forever': True,
        'config': dict()
    }