
import math
import time
import turtle
import json
import globals
from .utils import touch_in_box


def initialize(screen):
    global codes, hours, bg_hours
    with open(f"plugins/icons/{icon_set_name}/icons.json") as cfg:
        icon_sets = json.loads(cfg.read())
        for icon in icon_sets:
            for name in icon["images"]:
                shape = f"plugins/icons/{icon_set_name}/{name}.gif"
                if shape not in screen.getshapes():
                    screen.addshape(shape)
            for code in icon["codes"]:
                codes[code] = icon["images"]

    radius = globals.CLOCK_RADIUS
    for i in range(60, -300, -30):
        i_r = math.radians(i)
        hours.append((math.cos(i_r)*radius, math.sin(i_r)*radius))

    for i in range(0, 12):
        bg_hours[i] = turtle.Turtle(visible=True)
        bg_hours[i].penup()
        bg_hours[i].goto(hours[i][0], hours[i][1])


def get_image_array(hourly):
    global codes
    images = []
    for idx in range(12):
        dork = hourly[idx]["weather"][0]["icon"][2]
        dn = 0 if dork == "d" else 1
        icons = codes[hourly[idx]["weather"][0]["id"]]
        images.append(f"plugins/icons/{icon_set_name}/{icons[dn]}.gif")
    return images

def update(data):
    '''
    weather ID breakdown https://openweathermap.org/weather-conditions
    use https://ezgif.com/maker for gif conversion
    '''
    global bg_hours #, hourCursor, idImage_array

    currentHour = int(time.strftime("%H"))
    if currentHour > 12:
        hourCursor = currentHour - 12
    elif currentHour == 0:
        hourCursor = 12
    else:
        hourCursor = currentHour

    idImage_array = get_image_array(data["hourly"])

    for i in range(1, 13):
        if(i-hourCursor < 0):
            bg_hours[i-1].shape(idImage_array[12-abs(i-hourCursor)])
        else:
            bg_hours[i-1].shape(idImage_array[i-hourCursor])

def click(x, y):
    global hours
    hourTouched = False
    
    for i in range(0, 12):
        if (touch_in_box(x, y, hours[i][0], hours[i][1], hourlyTouchSize, hourlyTouchSize)):
            hourTouched = i + 1
            break
    return hourTouched


icon_set_name = globals.ICON_SET_NAME
hour_touched = None

codes = {}

hourlyTouchSize = 180

hours = []
bg_hours = [None]*12

