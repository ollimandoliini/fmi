import requests
from timezonefinder import TimezoneFinder
import pytz
import datetime
import os
import sys

# Tampere
coords = (61.497753, 23.760954)


def get_timezone(coords):
    tf = TimezoneFinder()
    latitude, longitude = coords
    timezone_name = tf.timezone_at(lng=longitude, lat=latitude)
    timezone_object = pytz.timezone(timezone_name)
    return timezone_object


def get_daytime_data(coords, date='today'):
    SUNRISE_SUNSET_API = f'https://api.sunrise-sunset.org/json?lat={coords[0]}&lng={coords[1]}&formatted=0&date={date}'
    return requests.get(SUNRISE_SUNSET_API).json()


def parse_to_local_time(iso8601, tz):
    dt = datetime.datetime.fromisoformat(iso8601)
    return pytz.utc.normalize(dt).astimezone(tz)


timezone = get_timezone(coords)
today_daytime_data = get_daytime_data(coords)
sunrise_today = parse_to_local_time(
    today_daytime_data['results']['sunrise'], timezone)
sunset_today = parse_to_local_time(
    today_daytime_data['results']['sunset'], timezone)

sunrise_today.strftime('%H:%M:%S')
sunset_today.strftime('%H:%M:%S')

day_length_today = datetime.timedelta(
    seconds=today_daytime_data['results']['day_length'])

yesterday_daytime_data = get_daytime_data(
    coords, date=datetime.datetime.today() - datetime.timedelta(1))
day_length_yesterday = datetime.timedelta(
    seconds=yesterday_daytime_data['results']['day_length'])

day_before_yesterday_daytime_data = get_daytime_data(
    coords, date=datetime.datetime.today() - datetime.timedelta(2))
day_length_before_yesterday = datetime.timedelta(
    seconds=day_before_yesterday_daytime_data['results']['day_length'])


change = day_length_today - day_length_yesterday

change_delta = abs((day_length_today - day_length_yesterday) -
                   (day_length_yesterday - day_length_before_yesterday))


TELEGRAM_URL = f"https://api.telegram.org/{os.environ['BOT_KEY']}/sendMessage"

msg = f"""
```AURINKOA ☀️
Nousu:  {sunrise_today.strftime('%H:%M:%S')}
Lasku:  {sunset_today.strftime('%H:%M:%S')}
Pituus: {day_length_today}
Muutos:  {change}
Muutoksen muutos: {change_delta}```"""
data = {'chat_id': os.environ['CHAT_ID'],
        'text': msg, 'parse_mode': 'Markdown'}

try:
    r = requests.post(url=TELEGRAM_URL, data=data)
    r.raise_for_status()
except requests.exceptions.HTTPError as err:
    r = requests.post(url=TELEGRAM_URL, data={'chat_id': os.environ['CHAT_ID'],
                                              'text': str(err), 'parse_mode': 'Markdown'})
    sys.exit(1)
