import requests
from timezonefinder import TimezoneFinder
import pytz
import datetime
import os
import settings

cities = {"Tampere": (61.497753, 23.760954), "Helsinki": (60.16952, 24.93545)}


def get_timezone(coords):
    tf = TimezoneFinder()
    latitude, longitude = coords
    timezone_name = tf.timezone_at(lng=longitude, lat=latitude)
    timezone_object = pytz.timezone(timezone_name)
    return timezone_object


def get_daytime_data(coords, date="today"):
    lat, long = coords
    sunrise_sunset_api_url = f"https://api.sunrise-sunset.org/json?lat={lat}&lng={long}&formatted=0&date={date}"
    return requests.get(sunrise_sunset_api_url).json()


def parse_to_local_time(iso8601, tz):
    dt = datetime.datetime.fromisoformat(iso8601)
    return pytz.utc.normalize(dt).astimezone(tz)


def day_length_info_string(coords):
    timezone = get_timezone(coords)
    today_daytime_data = get_daytime_data(coords)
    sunrise_today = parse_to_local_time(
        today_daytime_data["results"]["sunrise"], timezone
    )
    sunset_today = parse_to_local_time(
        today_daytime_data["results"]["sunset"], timezone
    )

    day_length_today = datetime.timedelta(
        seconds=today_daytime_data["results"]["day_length"]
    )

    yesterday_daytime_data = get_daytime_data(
        coords, date=datetime.datetime.today() - datetime.timedelta(1)
    )
    day_length_yesterday = datetime.timedelta(
        seconds=yesterday_daytime_data["results"]["day_length"]
    )

    day_before_yesterday_daytime_data = get_daytime_data(
        coords, date=datetime.datetime.today() - datetime.timedelta(2)
    )
    day_length_before_yesterday = datetime.timedelta(
        seconds=day_before_yesterday_daytime_data["results"]["day_length"]
    )

    sunrise_today_str = sunrise_today.strftime("%H:%M:%S")
    sunset_today_str = sunset_today.strftime("%H:%M:%S")
    change_str = abs(day_length_today - day_length_yesterday)
    delta = abs(
        (day_length_today - day_length_yesterday)
        - (day_length_yesterday - day_length_before_yesterday)
    )

    return (
        f"Nousu: {sunrise_today_str:>10}\n"
        f"Lasku: {sunset_today_str:>10}\n"
        f"Pituus: {str(day_length_today):>9}\n"
        f"Muutos: {str(change_str):>9}\n"
        f"Delta: {str(delta):>10}"
    )


city_messages = [
    f"```\n🌞 {city}\n{day_length_info_string(coords)}```" for city, coords in cities.items()
]


for msg in city_messages:
    data = {
        "chat_id": os.environ["CHAT_ID"],
        "disable_notification": True,
        "text": msg,
        "parse_mode": "MarkdownV2",
    }
    url = f"https://api.telegram.org/{os.environ['BOT_KEY']}/sendMessage"
    requests.post(url, data=data)
