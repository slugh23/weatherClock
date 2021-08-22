
import math
import time
import turtle
import json
import settings
from datetime import datetime
from utils import touch_in_box, round_half_up


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

    radius = settings.CLOCK_RADIUS
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

def get_hourly_forecasts(data, idx):
    fc = data["hourly"][idx]
    dt = datetime.fromtimestamp(fc["dt"])

    degree_sign = u"\N{DEGREE SIGN}"

    return [
        ("Day", dt.strftime('%A')),
        ("Hour", dt.strftime('%H:%S')),
        ("Temp", f"{round_half_up(fc['temp'], 1)} {degree_sign}"),
        ("Feels like", f"{round_half_up(fc['feels_like'], 1)} {degree_sign}"),
        ("PoP", f"{fc['pop']*100} %"),
        ("Rain", f"{round_half_up(fc['rain']['1h'] / 25.4, 2)} in" if "rain" in fc else "--"),
        ("Wind", f"{round_half_up(fc['wind_speed'] * 0.6213712, 1)} mph"),
        ("Gust", f"{round_half_up(fc['wind_gust'] * 0.6213712, 1)} mph"),
        ("code", f"{fc['weather'][0]['id']}")
    ]

def draw_weather_text(data):
    global hour_touched, txt, val, pen, on_screen

    if on_screen:
        return

    on_screen = True
    current_hour = int(time.strftime("%H"))
    hours_ahead = hour_touched - current_hour
    if hours_ahead < 0:
        hours_ahead = (hours_ahead + 24) % 12

    hf = get_hourly_forecasts(data, hours_ahead)

    height = SPACING * (len(hf) - 1)
    txt.goto(txt_x, height/2 - HCHAR/2)
    val.goto(val_x, height/2 - HCHAR/2)

    for line in hf:
        txt.write(line[0], align="right", font=("Verdana", FONT_SIZE, "bold"))
        txt.fd(SPACING)
        val.write(line[1], align="left", font=("Verdana", FONT_SIZE, "bold"))
        val.fd(SPACING)

    pen.penup()
    pen.goto(0, (height + SPACING) / 2)
    print("Pen y: {(height + SPACING) / 2}")
    pen.pendown()
    pen.fd(height + SPACING)



    
def update(data):
    '''
    weather ID breakdown https://openweathermap.org/weather-conditions
    use https://ezgif.com/maker for gif conversion
    '''
    global bg_hours, active

    currentHour = int(time.strftime("%H"))
    if currentHour > 12:
        hourCursor = currentHour - 12
    elif currentHour == 0:
        hourCursor = 12
    else:
        hourCursor = currentHour

    idImage_array = get_image_array(data["hourly"])

    if active:
        draw_weather_text(data)

    for i in range(1, 13):
        if(i-hourCursor < 0):
            bg_hours[i-1].shape(idImage_array[12-abs(i-hourCursor)])
        else:
            bg_hours[i-1].shape(idImage_array[i-hourCursor])

def close_forecast():
    global txt, val, pen, on_screen
    txt.clear()
    val.clear()
    pen.clear()
    on_screen = False

def click(x, y):
    global active
    if not active:
        return click_on(x, y)
    else:
        return click_off(x, y)

def click_on(x, y):
    global hours, hour_touched, active
    hour_touched = False
    
    for i in range(0, 12):
        if (touch_in_box(x, y, hours[i][0], hours[i][1], hourlyTouchSize, hourlyTouchSize)):
            hour_touched = i + 1
            close_forecast()
            active = True
            break
    return hour_touched

def click_off(x, y):
    global txt, pen, val, active
    if touch_in_box(x, y, 0, 0, 200, 200):
        close_forecast()
        active = False
        return False
    else:
        click_on(x, y)
    return None

icon_set_name = settings.ICON_SET_NAME
hour_touched = None
hourlyTouchSize = 180
active = False
on_screen = False

codes = {}
hours = []
bg_hours = [None]*12

# create our drawing pens
txt = turtle.Turtle(visible=False)
txt.penup()
txt.color("white")
txt.setheading(270)
txt_x = -30

val = turtle.Turtle(visible=False)
val.penup()
val.color("white")
val.setheading(270)
val_x = 30

FONT_SIZE = 18
SPACING = 30
HCHAR = 24

pen = turtle.Turtle(visible=False)
pen.pensize(3)
pen.color("white")
pen.setheading(270)
