import requests
import time
import math
import modules.grpc as dish

### Helper functions
def print_http_error(code:int, what:str, message:str = ""):
    print(f'HTTP code {code} - {what}. {message}')

### Globals
last_modified = 'Mon, 29 Apr 2024 12:32:47 GMT' #random date used for initial call, then for local caching
lattitude = 0
longtittude = 0

def collect_weather_data(user_agent):
    global last_modified
    headers = {'user-agent': user_agent, 'if-modified-since': last_modified}

    response = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={lattitude}&lon={longtittude}", headers=headers)
    match response.status_code:
        case 200 | 203 | 304: #Success, Depracated, Not Modified
            if response.status_code == 203:
                print_http_error(response.status_code, 'In Beta or Depracated', 'Please refer to documentation and update the endpoint')
            expires = time.strptime(response.headers.get('expires'), "%a, %d %b %Y %H:%M:%S %Z")
            expires_in = time.mktime(expires) - time.mktime(time.gmtime())
            last_modified = response.headers.get('last-modified')

            #Success, parse and save data
            if response.status_code == 200 or response.status_code == 203:
                data = response.json()
                return extract_weather_data(data)
            return None
        case 400:
            print_http_error(response.status_code, "Bad Request")
        case 401:
            print_http_error(response.status_code, "Unauthorized")
        case 403:
            print_http_error(response.status_code, "Forbidden", "Did you forget to use a proper User-Agent header?")
        case 404:
            print_http_error(response.status_code, "Not Found", "Handler has no data to offer")
        case 405:
            print_http_error(response.status_code, "Method Not Allowed", "Are you sending POST requests?")
        case 422:
            print_http_error(response.status_code, "Unprocessable Entity", "The service does not offer data for specified parameters")
        case 429:
            print_http_error(response.status_code, "Too Many Requests")
        case 499:
            print_http_error(response.status_code, "Request timeout")
        case 500 | 502 | 503 | 504:
            print_http_error(response.status_code, "Remote Server Error")
        case _:
            print('The internet is broken! You receive a medal for breaking the internet')
    return None

def extract_weather_data(raw_data):
    data = {}
    data_obj = raw_data['properties']['timeseries'][0]['data']
    units = raw_data['properties']['meta']['units']
    data[f'temperature_{units['air_temperature']}'] = data_obj['instant']['details']['air_temperature']
    data[f'cloud_area_fraction_{units['cloud_area_fraction']}'] = data_obj['instant']['details']['cloud_area_fraction']
    data[f'precipitation_amount_{units['precipitation_amount']}'] = data_obj['next_1_hours']['details']['precipitation_amount']
    return data

def setup(setup):
    global lattitude, longtittude
    loc = dish.location_data()
    lattitude = round(loc['latitude'], 4)
    longtittude = round(loc['longitude'], 4)


def collect(config):
    try:
        weather = collect_weather_data(config['user_agent'])
        if weather:
            weather['metadata'] = dict()
            weather['metadata']['longtitude'] = longtittude
            weather['metadata']['latitude'] = lattitude
        return weather
    except requests.RequestException:
        return None