import requests
import socket
import requests.packages.urllib3.util.connection as urllib3_cn # type: ignore

#Force IP layer utils
original = urllib3_cn.allowed_gai_family

def force_v6():
    return socket.AF_INET6

def force_v4():
    return socket.AF_INET

def reset_forced_version():
    urllib3_cn.allowed_gai_family = original

#Required by spec
def setup(setup):
    pass

#Required by spec
def collect(config):
    data = dict()
    try:
        data['v4'] = collect_public_ipv4()
    except requests.exceptions.ConnectionError:
        data['v4'] = "Unreachable"
    try:
        data['v6'] = collect_public_ipv6()
    except requests.exceptions.ConnectionError:
        data['v6'] = "Unreachable"
    reset_forced_version()
    return data

#Any helper/module functions doing work
def collect_public_ipv4():
    urllib3_cn.allowed_gai_family = force_v4
    response = requests.get('https://ifconfig.me')
    return response.text

def collect_public_ipv6():
    urllib3_cn.allowed_gai_family = force_v6
    response = requests.get('https://ifconfig.me')
    return response.text