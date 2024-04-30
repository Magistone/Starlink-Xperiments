import requests
import time
import yaml
import asyncio

### Initial configuration
weather_config = {}
space_weather_config = {}
with open('../config.yml', 'r') as file:
    data = yaml.safe_load(file)
    weather_config = data['weather']
    space_weather_config = data['space_weather']

print(weather_config)
print(space_weather_config)


### Weather data collection
last_modified = 'Mon, 29 Apr 2024 12:32:47 GMT'

headers = {'user-agent': weather_config['user_agent'], 'if-modified-since': last_modified}

response = requests.get(f"https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={weather_config['lattitude']}&lon={weather_config['longtittude']}", headers=headers)
print(response.status_code) #TODO branch on status code
expires = time.strptime(response.headers.get('expires'), "%a, %d %b %Y %H:%M:%S GMT")
last_modified = response.headers.get('last-modified')

print(response.json()) #TODO parse if status 200
# aim: run loop every 5 mins, check expires, if expired request else do nothing


### Space Weather data collection

# :) spaceweather.gov

### InfluxDB writers

# SURPRISED PIKACHU FACE