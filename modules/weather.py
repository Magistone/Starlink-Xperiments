import requests
import time
import modules.grpc as dish

### Helper functions
def print_http_error(code:int, what:str, message:str = ""):
    print(f'HTTP code {code} - {what}. {message}')

### Globals
last_modified = 'Mon, 29 Apr 2024 12:32:47 GMT' #random date used for initial call, then for local caching
lattitude = 0
longtittude = 0

def collect_weather_data(user_agent) -> int:
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
                return data
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

def setup(setup):
    global lattitude, longtittude
    loc = dish.location_data()
    lattitude = round(loc['latitude'], 4)
    longtittude = round(loc['longitude'], 4)


def collect(config):
    weather = collect_weather_data(config['user_agent'])
    return weather