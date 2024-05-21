import requests

### Space Weather data collection
def collect_space_weather_data():
    response = requests.get('https://services.swpc.noaa.gov/products/noaa-scales.json')
    # print(f'{response.status_code} - space weather')
    if response.status_code == 200:
        json = response.json()
        data = {'R': json['0']['R']['Scale'], 'S': json['0']['S']['Scale'], 'G': json['0']['G']['Scale']}
        return data
    return None

def setup(setup):
    pass

def collect():
    data = collect_space_weather_data()
    return data