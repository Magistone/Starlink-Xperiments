import requests
import time
import yaml
import asyncio

### Initial configuration
weather_config = {}
space_weather_config = {}
with open('config.yml', 'r') as file:
    data = yaml.safe_load(file)
    weather_config = data['weather']
    space_weather_config = data['space_weather']

### Helper functions
def print_http_error(code:int, what:str, message:str = ""):
    print(f'HTTP code {code} - {what}. {message}')

### DB writers TODO
def write_weather_data(data):
    print('Writing weather data')
    pass

def write_space_weather_data(data):
    print('Writing space weather data')
    pass

### Weather data collection
last_modified = 'Mon, 29 Apr 2024 12:32:47 GMT' #random date used for initial call, then for local caching

def collect_weather_data() -> int:
    global last_modified
    headers = {'user-agent': weather_config['user_agent'], 'if-modified-since': last_modified}

    response = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={weather_config['lattitude']}&lon={weather_config['longtittude']}", headers=headers)
    match response.status_code:
        case 200 | 203 | 304: #Success, Depracated, Not Modified
            if response.status_code == 203:
                print_http_error(response.status_code, 'In Beta or Depracated', 'Please refer to documentation and update the endpoint')
            expires = time.strptime(response.headers.get('expires'), "%a, %d %b %Y %H:%M:%S %Z")
            expires_in = time.mktime(expires) - time.mktime(time.gmtime())
            last_modified = response.headers.get('last-modified')

            print(f'{response.status_code} - weather')
            #Success, parse and save data
            if response.status_code == 200 or response.status_code == 203:
                data = response.json()
                #print(data) # TODO only relevant data

                write_weather_data(data)
            print(f'Last modified: {last_modified} \nExpires in: {expires_in} sec \nExpires: {expires}')
            #In case of expires header being in the past, retry in 5 minutes
            return expires_in if expires_in > 0 else 5*60
        case 400:
            print_http_error(response.status_code, "Bad Request")
            code = -1
        case 401:
            print_http_error(response.status_code, "Unauthorized")
            code = -1
        case 403:
            print_http_error(response.status_code, "Forbidden", "Did you forget to use a proper User-Agent header?")
            code = -1
        case 404:
            print_http_error(response.status_code, "Not Found", "Handler has no data to offer")
            code = -2
        case 405:
            print_http_error(response.status_code, "Method Not Allowed", "Are you sending POST requests?")
            code = -1
        case 422:
            print_http_error(response.status_code, "Unprocessable Entity", "The service does not offer data for specified parameters")
            code = -1
        case 429:
            print_http_error(response.status_code, "Too Many Requests")
            code = -1
        case 499:
            print_http_error(response.status_code, "Request timeout")
            code = -2
        case 500 | 502 | 503 | 504:
            print_http_error(response.status_code, "Remote Server Error")
            code -2
        case _:
            print('The internet is broken! You receive a medal for breaking the internet')
            code -1

    return code

### Space Weather data collection
def collect_space_weather_data():
    response = requests.get('https://services.swpc.noaa.gov/products/noaa-scales.json')
    print(f'{response.status_code} - space weather')
    if response.status_code == 200:
        json = response.json()
        data = {'R': json['0']['R']['Scale'], 'S': json['0']['S']['Scale'], 'G': json['0']['G']['Scale']}
        write_space_weather_data(data)

### Coroutines
async def collect_weather_data_coroutine():
    while weather_config['enable']:
        expires = collect_weather_data()
        match expires:
            case -1: #Irrecoverable
                print('Fatal error, shutting down terrestrial weather collection...')
                print('Refer to the error above. You need to restart this container if you change any configuration')
                print("Run 'docker compose restart' to restart all containers in the stack")
                break
            case -2: #Recoverable, missing data
                delay = 30
                print('Encountered non-fatal error, retrying in {delay} minutes')
                await asyncio.sleep(delay*60)
            case _ if expires >= 0: #Succeeded & has timer
                await asyncio.sleep(expires)
            case _: #Destruction???
                print("Unknown fatal error, total destruction imminent")
                print("I have no clue what you've done")
                print("Exiting terrestrial weather collection...")
                break


async def collect_space_weather_data_coroutine():
    while space_weather_config['enable']:
        collect_space_weather_data()
        await asyncio.sleep(60)

async def main():
    task1 = asyncio.create_task(collect_space_weather_data_coroutine())
    task2 = asyncio.create_task(collect_weather_data_coroutine())

    await task1
    await task2

try:
    asyncio.run(main())
except:
    pass