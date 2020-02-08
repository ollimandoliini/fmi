import requests
from timezonefinder import TimezoneFinder
import pytz
import datetime
import os
import requests
from PIL import Image, ImageFont, ImageDraw
from IPython.display import display
from io import BytesIO

TAMPERE = 61.497753, 23.760954
STOCKHOLM = 59.334591, 18.063240


def get_timezone(coords):
    tf = TimezoneFinder()
    latitude, longitude = coords
    timezone_name = tf.timezone_at(lng=longitude, lat=latitude)
    timezone_object = pytz.timezone(timezone_name)
    return timezone_object


def get_daytime_data(coords, date='today'):
    lat, long = coords
    sunrise_sunset_api_url = f'https://api.sunrise-sunset.org/json?lat={lat}&lng={long}&formatted=0&date={date}'
    return requests.get(sunrise_sunset_api_url).json()


def parse_to_local_time(iso8601, tz):
    dt = datetime.datetime.fromisoformat(iso8601)
    return pytz.utc.normalize(dt).astimezone(tz)


def day_length_info_string(coords):
    timezone = get_timezone(coords)
    today_daytime_data = get_daytime_data(coords)
    sunrise_today = parse_to_local_time(
        today_daytime_data['results']['sunrise'], timezone)
    sunset_today = parse_to_local_time(
        today_daytime_data['results']['sunset'], timezone)

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

    sunrise_today_str = sunrise_today.strftime('%H:%M:%S')
    sunset_today_str = sunset_today.strftime('%H:%M:%S')
    change_str = str(day_length_today - day_length_yesterday)
    delta = abs((day_length_today - day_length_yesterday) -
                (day_length_yesterday - day_length_before_yesterday))

    return (f"Nousu: {sunrise_today_str:>10}\n"
            f"Lasku: {sunset_today_str:>10}\n"
            f"Pituus: {str(day_length_today):>9}\n"
            f"Muutos: {change_str:>9}\n"
            f"Delta: {str(delta):>10}")


img = Image.new('RGB', (750, 350), color='white')
draw = ImageDraw.Draw(img)
font_heading = ImageFont.truetype("Helvetica.ttc", 48)
font_body = ImageFont.truetype("jetbrains-mono.ttf", 32)

draw.text((75, 10), "Tampere", (0, 0, 0), font=font_heading)
draw.text((475, 10), "Stockholm", (0, 0, 0), font=font_heading)

draw.text((0, 80), day_length_info_string(TAMPERE), (0, 0, 0), font=font_body)
draw.text((400, 80), day_length_info_string(
    STOCKHOLM), (0, 0, 0), font=font_body)

flag_finland = Image.open(
    'flag-finland.png', 'r').resize((64, 64), Image.ANTIALIAS)
img.paste(flag_finland, (0, 0), flag_finland)

flag_sweden = Image.open(
    'flag-sweden.png', 'r').resize((64, 64), Image.ANTIALIAS)
img.paste(flag_sweden, (400, 0), flag_sweden)

fd = BytesIO()
img.save(fd, "png", quality=95)


fd.seek(0)
files = {'photo': fd.read()}
data = {'chat_id': os.environ['CHAT_ID'], 'disable_notification': True}

url = f"https://api.telegram.org/{os.environ['BOT_KEY']}/sendPhoto"

requests.post(url, data=data, files=files).content
