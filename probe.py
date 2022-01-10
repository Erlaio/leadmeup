# -*- coding: utf-8 -*-
from datetime import datetime

import requests
from geopy.geocoders import Nominatim

city_name = 'Saransk, RU'
geolocator = Nominatim(user_agent='my_request')
location = geolocator.geocode(city_name)
app_id = 'b36b0594dc0126cca33d8538c67a0da1'

data = requests.get('http://api.openweathermap.org/data/2.5/onecall?',
                    params={'lat': location.latitude, 'lon': location.longitude,
                            'exclude': 'current,minutely,hourly,alerts', 'units': 'metric', 'APPID': app_id}).json()

print('Город: {}\n'.format(location.address))

temp_difference = [(datetime.fromtimestamp(i_day['dt']).strftime('%d-%m-%Y'),
                    abs(i_day['temp']['night'] - i_day['feels_like']['night'])) for i_day in data['daily'][:5]]

min_temp = min(temp_difference, key=lambda x: x[1])

print('C {} по {} минимальная разница "ощущаемой" и фактической температуры ночью будет {} и составит {}\xb0С\n'.format(
    temp_difference[0][0], temp_difference[-1][0], min_temp[0], round(min_temp[1], 2)
))

for i_day in data['daily'][:5]:
    date = datetime.fromtimestamp(i_day['dt']).strftime('%d-%m-%Y')
    daylight_hours = datetime.fromtimestamp(i_day['sunset']) - datetime.fromtimestamp(i_day['sunrise'])
    print('Максимальная продолжительность светового дня за {} составит: {}'.format(date, daylight_hours))
