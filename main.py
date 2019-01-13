import requests
import json
import datetime
import time
import dateutil.parser
import pytz
import schedule
import os


def get_coordinates(cityname):
    GEO_CODING_API = f"https://maps.googleapis.com/maps/api/geocode/json?address={cityname}&key={os.environ['GEO_CODING_API_KEY']}"
    r = requests.get(GEO_CODING_API).content
    json_data = json.loads(r)
    lat = json_data['results'][0]['geometry']['bounds']['southwest']['lat']
    lng = json_data['results'][0]['geometry']['bounds']['southwest']['lng']
    coordinates = (lat, lng)
    return coordinates


def daytime_data(latitude, longitude, date='today'):
    SUNRISE_SUNSET_API = f'https://api.sunrise-sunset.org/json?lat={latitude}&lng={longitude}&formatted=0&date={date}'
    r = requests.get(SUNRISE_SUNSET_API).content
    json_data = json.loads(r)
    return json_data


def get_timezone(cityname):
    city_coordinates = get_coordinates(cityname)
    CURRENT_TIME = int(time.mktime(datetime.datetime.now().timetuple()))
    TIME_ZONE_API = f"https://maps.googleapis.com/maps/api/timezone/json?location={city_coordinates[0]},{city_coordinates[1]}&timestamp={CURRENT_TIME}&key={os.environ['GEO_CODING_API_KEY']}"
    r = requests.get(TIME_ZONE_API).content
    json_data = json.loads(r)
    return json_data


def daytime_data_by_city(cityname, date='today'):
    city_coordinates = get_coordinates(cityname)
    city_daytime_data = daytime_data(
        city_coordinates[0], city_coordinates[1], date)
    timezone_data = get_timezone(cityname)
    tz = pytz.timezone(timezone_data['timeZoneId'])

    sunrise = dateutil.parser.parse(city_daytime_data['results']['sunrise'])
    sunset = dateutil.parser.parse(city_daytime_data['results']['sunset'])
    day_length = datetime.timedelta(
        seconds=city_daytime_data['results']['day_length'])

    sunrise_normalized = pytz.utc.normalize(sunrise).astimezone(tz)
    sunset_normalized = pytz.utc.normalize(sunset).astimezone(tz)

    sunset_sunrise_daylenght = {'sunrise':
                                sunrise_normalized,  'sunset': sunset_normalized, 'day_length': day_length}
    return sunset_sunrise_daylenght


def day_lenght_difference(date1, date2, cityname):
    date1_lenght = daytime_data_by_city(cityname, date1)['day_length']
    date2_lenght = daytime_data_by_city(cityname, date2)['day_length']
    difference = date1_lenght - date2_lenght
    return difference


def send_daylight_message():
    today = datetime.date.today()
    yesterday = datetime.date.today() - datetime.timedelta(1)
    daytime_data = daytime_data_by_city('tampere')
    TELEGRAM_URL = f"https://api.telegram.org/{os.environ['BOT_KEY']}/sendMessage"
    msg = str('Aurinko nousee tänään klo ' + daytime_data['sunrise'].time().strftime(
        '%H:%M:%S') + ' ja laskee klo ' + daytime_data['sunset'].time().strftime('%H:%M:%S') +
        '. Päivän pituus on ' + str(daytime_data['day_length']) + '. Pituuden muutos eilisestä ' + str(
            day_lenght_difference(today, yesterday, 'tampere')))
    data = {'chat_id': os.environ['CHAT_ID'], 'text': msg}
    r = requests.post(url=TELEGRAM_URL, data=data)
    return json.loads(r.content)


if __name__ == "__main__":
    send_daylight_message()
    schedule.every().day.at("7:00").do(send_daylight_message)
    while True:
        schedule.run_pending()
        time.sleep(60)
