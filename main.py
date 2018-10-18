import requests
from bs4 import BeautifulSoup

def get_weather_page(city):
    url_base = 'https://ilmatieteenlaitos.fi/saa/'
    url = url_base + city
    result = requests.get(url)
    if result.status_code == 200:
        return result.content

def day_time(city):
    soup = BeautifulSoup(get_weather_page(city), features='html.parser')
    day_time_str = soup.find('div', {'class':'celestial-status-text'}).text
    return day_time_str

def temperature(city):
    soup = BeautifulSoup(get_weather_page(city), features='html.parser')
    temperature_str = soup.find_all('div')
    return temperature_str

print(temperature('Padasjoki'))