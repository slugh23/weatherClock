import json

CLOCK_RADIUS = 270
OWM_BASEURI = "https://api.openweathermap.org/data/2.5/onecall"
OWM_EXCLUDES = "current,minutely,flags"

ICON_SET_NAME = "owm-std"
UPDATE_PERIOD = 10
FONT_SIZE = 18

def get_settings():
    with open("settings.json", "r") as settings_file:
        settings = json.loads(settings_file.read())
        return settings

settings = get_settings()

if "icon-set-name" in settings:
    ICON_SET_NAME = settings["icon-set-name"]

if "update-period" in settings:
    UPDATE_PERIOD = settings["update-period"]

WEATHER_DATA_URL = f'{OWM_BASEURI}?lat={settings["latitude"]}&lon={settings["longitude"]}&exclude={OWM_EXCLUDES}&appid={settings["APIKEY"]}&units=metric'
