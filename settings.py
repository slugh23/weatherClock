import json

def SECONDS(seconds):
    return seconds

def MINUTES(seconds):
    return 60 * SECONDS(seconds)

def HOURS(seconds):
    return 60 * MINUTES(seconds)

CLOCK_RADIUS = 270
OWM_BASEURI = "https://api.openweathermap.org/data/2.5/onecall"
OWM_EXCLUDES = "minutely,flags"

ICON_SET_NAME = "owm-std"
UPDATE_PERIOD = MINUTES(10)
FETCH_DELAY_INCR = SECONDS(10)
FONT_SIZE = 18

def get_settings():
    with open("settings.json", "r") as settings_file:
        settings = json.loads(settings_file.read())
        return settings

settings = get_settings()

if "icon-set-name" in settings:
    ICON_SET_NAME = settings["icon-set-name"]

if "update-mins" in settings:
    UPDATE_PERIOD = MINUTES(settings["update-mins"])

if "update-retry-sec" in settings:
    FETCH_DELAY_INCR = SECONDS(settings["update-retry-sec"])

WEATHER_DATA_URL = f'{OWM_BASEURI}?lat={settings["latitude"]}&lon={settings["longitude"]}&exclude={OWM_EXCLUDES}&appid={settings["APIKEY"]}&units=metric'
