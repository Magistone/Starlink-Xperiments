from flask import Flask, request
import multiprocessing, time

app = Flask(__name__)

@app.post("/create")
def createJob():
    params = request.get_json()
    validated = validate_params(params)
    if not validated['valid']:
        return validated['message'], 400
    
    #SPAWN PROCESS
    return "OK", 200

@app.post("/install")
def installDependencies():
    pass

@app.post("/reboot")
def reboot():
    config = create_min_config()
    config['config']['reboot'] = True
    #PASS to scheduler

@app.post("/stow")
def stow():
    config = create_min_config()
    obj = request.get_json()
    config['config']['stow_operation'] = obj.get('stow')
    config['config']['stow'] = True
    #PASS to scheduler

@app.post("/validate")
def debug():
    obj = request.get_json()
    response = validate_params(obj)
    status = 200
    if not response['valid']:
        status = 400
    return response['message'], status

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

    if stop == None and forever != True:
        valid = False
        msg += " Requires one of: stop, forever."

    if stop != None and not validate_date_format(stop):
        valid = False
        msg += " Invalid format for stop time."
    
    if start != None and not validate_date_format(start):
        valid = False
        msg += " Invalid format for start time."

    if mod == None:
        valid = False
        msg += " Requires module parameter."
    
    if per == None:
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