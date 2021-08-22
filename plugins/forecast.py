
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

def draw_weather_text(data):
    global hour_touched
    current_hour = int(time.strftime("%H"))
    hoursAhead = hour_touched - current_hour
    if hoursAhead < 0:
        hoursAhead = (hoursAhead + 24) % 12

    fc = data["hourly"][hoursAhead]
    dt = datetime.fromtimestamp(fc["dt"])

    txt.goto(txt_x, spacing*3)
    txt.write("Day", align="right", font=("Verdana", FontSize, "bold"))
    val.goto(val_x, spacing*3)
    val.write(dt.strftime('%A'), align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("hour", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(dt.strftime("%H:%S"), align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("temp", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(str(round_half_up(fc["temp"], 1)) + degree_sign, align="left", font=("Verdana", FontSize, "bold"))
    
    txt.fd(spacing)
    txt.write("Feels like", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(str(round_half_up(fc["feels_like"], 1)) + degree_sign, align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("POP", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(str(int(fc["pop"]*100)) + " %", align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("Rain", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    if 'rain' not in fc:
        val.write("--", align="left", font=("Verdana", FontSize, "bold"))
    else:
        val.write(str(round_half_up(fc["rain"]["1h"] / 25.4, 2)) + " in", align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("Wind", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(str(round_half_up(fc["wind_speed"] * 0.6213712, 1)) + " mph", align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("Gust", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(str(round_half_up(fc["wind_gust"] * 0.6213712, 1)) + " mph", align="left", font=("Verdana", FontSize, "bold"))

    txt.fd(spacing)
    txt.write("code", align="right", font=("Verdana", FontSize, "bold"))
    val.fd(spacing)
    val.write(fc["weather"][0]["id"], align="left", font=("Verdana", FontSize, "bold"))

    pen.penup()
    pen.goto(0, -150)
    pen.pendown()
    pen.fd(300)
    
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
    global hours, hour_touched
    hour_touched = False
    
    for i in range(0, 12):
        if (touch_in_box(x, y, hours[i][0], hours[i][1], hourlyTouchSize, hourlyTouchSize)):
            hour_touched = i + 1
            break
    return hour_touched

def click_off(x, y):
    global txt, pen
    txt.clear()
    val.clear()
    pen.clear()
    if touch_in_box(x, y, 0, 0, 200, 200):
        return False
    return None

icon_set_name = settings.ICON_SET_NAME
hour_touched = None
hourlyTouchSize = 180

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

spacing = 30
FontSize = 18
DataFontSize = 18

pen = turtle.Turtle(visible=False)
pen.pensize(3)
pen.color("white")
pen.setheading(90)

degree_sign = u"\N{DEGREE SIGN}"

