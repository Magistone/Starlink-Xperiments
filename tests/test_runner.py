import sys, subprocess

sys.path.append(sys.path[0][:-6]) # FUCK YOU PYTHON

import main

def test_min_config():
    obj = main.create_min_config()
    assert(isinstance(obj, dict))

    validation = main.validate_params(obj)
    assert(validation['valid'])

def test_valid_config_1():
    full_config = {
        'module': "ip", 
        'start': "FRI, 24 MAY 2024 09:51:00 GMT", 
        'stop': "FRI, 31 MAY 2024 09:51:00 GMT", 
        'period': 15, 
        'forever': True, 
        'setup': None, 
        'config': {} 
    }
    
    assert(main.validate_params(full_config)['valid'])
    

def test_valid_config_2():
    full_config = {
        'module': "ip", 
        'start': "FRI, 24 MAY 2024 09:51:00 GMT", 
        'stop': "FRI, 24 MAY 2024 09:51:00 UTC", 
        'period': 69
    }
    
    validation = main.validate_params(full_config)
    print(validation['message'])
    assert(validation['valid'])

def test_valid_config_3():
    full_config = {
        'module': "ip", 
        'stop': "THU, 23 MAY 2024 09:51:00 GMT", 
        'period': 15, 
        'forever': True
    }

    assert(main.validate_params(full_config)['valid'])

def test_invalid_config_1():
    full_config = {
        'module': "ip", 
        'start': "FRI, 24 MAY 2024 09:51:00 GMT", 
        'period': 15, 
        'forever': False
    }

    assert(not main.validate_params(full_config)['valid'])

def test_invalid_config_2():
    full_config = {
        'module': "ip", 
        'start': "FRI, 24 MAY 2024 09:51:00 GMT", 
        'period': 87, 
        'forever': False, 
    }

    assert(not main.validate_params(full_config)['valid'])

def test_valid_date_1():
    date = "FRI, 24 MAY 2024 09:51:00 GMT"
    assert(main.validate_date_format(date))

def test_valid_date_2():
    date = "THU, 24 MAY 2024 09:51:00 UTC"
    assert(main.validate_date_format(date))

def test_invalid_date_1():
    date = "THU, 24 MAY 2024, 09:51:00 GMT"
    assert(not main.validate_date_format(date)) 

def test_invalid_date_2():
    date = "THU, MAY 24 2024 09:51:00 GMT"
    assert(not main.validate_date_format(date))

def test_valid_dependency():
    params = {'modules': ['numpy']}
    result = main.install_dependencies(params)
    assert(len(result.result) == 1)

    for m in params['modules']:
        uninstall_after_test(m)

def test_valid_dependency_2():
    params = {'modules': ['numpy>=1.26.4']}
    result = main.install_dependencies(params)
    assert(len(result.result) == 1)

    for m in params['modules']:
        uninstall_after_test(m)

def test_invalid_dependency():
    params = {'modules': ['AnUnExistingModuleaghiera']}
    result = main.install_dependencies(params)
    assert(len(result.error) == 1)

def uninstall_after_test(module: str):
    subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', module])