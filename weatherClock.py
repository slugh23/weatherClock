import os
import time
import turtle
import math
import requests
from datetime import datetime
from datetime import timedelta
import json
from plugins.utils import round_half_up
from plugins import *

# currently set to Vancouver, BC CANADA
#latitude = 49.2827
#longtitude = -123.1207
radius = 270

settings = None
with open("settings.json", "r") as settings_file:
    settings = json.loads(settings_file.read())

url = f'http://api.openweathermap.org/data/2.5/onecall?lat={settings["latitude"]}&lon={settings["longitude"]}&exclude=current,minutely,flags&appid={settings["APIKEY"]}&units=metric'

CLOCK_MODE = 0
HOURLY_MODE = 1
ALERT_MODE = 2

clock_mode = True

data = None
weatherUpdatePeriod = 10

id_array = [0] * 12
idImage_array = [""] * 12

currentHour = 0
day = None

hourCursor = 0

forecast.icon_set_name = "blue-filled-line"
forecast.initialize()

def fetch_weather_data(owm_url):
    res = requests.get(owm_url)
    weather_data = res.json()
    with open("/tmp/weather.json", "w") as cache:
        cache.write(json.dumps(weather_data))
    return weather_data

try:
    with open("/tmp/weather.json", "r") as cache:
        data = json.loads(cache.read())
        if data["hourly"][1]["dt"] < time.time():
            print("Old data --  Refreshing cache!")
            data = fetch_weather_data(url)
except:
    data = fetch_weather_data(url)
    
if data == None:
    data = fetch_weather_data(url)

#if "alerts" not in data:
#    data["alerts"] = [{"sender_name": "NWS Buffalo (Western New York)", "event": "Heat Advisory", "start": 1628668260, "end": 1628726400, "description": "...HEAT ADVISORY REMAINS IN EFFECT UNTIL 8 PM EDT THIS EVENING...\n* WHAT...Heat index values this afternoon from the upper 90s to\n105.\n* WHERE...Niagara, Orleans, Monroe, Wayne, and Livingston\ncounties.\n* WHEN...Until 8 PM EDT this evening.\n* IMPACTS...Hot temperatures and high humidity may cause heat\nillnesses to occur.", "tags": ["Extreme temperature value"]}]

cursor_x = 0
cursor_y = 0
cursor_xform = 1
if "invert-cursor" in settings:
    cursor_xform = -1 if settings["invert-cursor"] else 1

# create our drawing pen
pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(3)

weatherText = turtle.Turtle()
weatherText.hideturtle()
weatherText_Description = -30
weatherText_Data = 30
weatherText_vertSpacing = 30
weatherText_DescriptionFontSize = 18
weatherText_DataFontSize = 18
sun.FontSize = weatherText_DataFontSize

weatherDividerPen = turtle.Turtle()
weatherDividerPen.hideturtle()

degree_sign = u"\N{DEGREE SIGN}"

dateText = turtle.Turtle()
dateText.hideturtle()
dateText.penup()

hourlyTouchSize = 180 # determines radius for user touch when going into hourly detail mode

hours = []
for i in range(60, -300, -30):
    i_r = math.radians(i)
    hours.append((math.cos(i_r)*radius, math.sin(i_r)*radius))

wn = turtle.Screen()
wn.bgcolor("black")
wn.screensize()

if "screen" in settings:
    wn.setup(width=settings["screen"]["width"], height=settings["screen"]["height"])
else:
    wn.setup(width = 1.0, height = 1.0)

wn.title("WeatherClock 0.0.0")
wn.tracer(0)

def touchInBox(touch_x, touch_y, center_x, center_y, size_x, size_y):
    if (touch_x > (center_x - size_x/2) and touch_x < (center_x + size_x/2) and touch_y > (center_y - size_y/2) and touch_y < (center_y + size_y/2)):
        return True
    else:
        return False

def draw_weather_text(hourTouched):
    global pen, dateText, day
    
    pen.clear()
    dateText.clear()
    day = None

    currentHour = int(time.strftime("%H"))
    hoursAhead = hourTouched - currentHour
    if hoursAhead < 0:
        hoursAhead = (hoursAhead + 24) % 12

    fc = data["hourly"][hoursAhead]
    dt = datetime.fromtimestamp(fc["dt"])

    weatherText.penup()
    weatherText.goto(weatherText_Description, weatherText_vertSpacing*3)
    weatherText.color("white")
    weatherText.write("Day", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # day of the week

    weatherText.goto(weatherText_Data, weatherText_vertSpacing*3)
    weatherText.write(dt.strftime('%A'), align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, weatherText_vertSpacing*2)
    weatherText.write("hour", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # hour of the day

    weatherText.goto(weatherText_Data, weatherText_vertSpacing*2)
    weatherText.write(dt.strftime("%H:%S"), align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, weatherText_vertSpacing)
    weatherText.write("temp", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # temperature

    weatherText.goto(weatherText_Data, weatherText_vertSpacing)
    weatherText.write(str(round_half_up(fc["temp"], 1)) + degree_sign, align="left", font=("Verdana", weatherText_DataFontSize, "bold"))
    
    weatherText.goto(weatherText_Description, 0)
    weatherText.write("Feels like", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # Feels like

    weatherText.goto(weatherText_Data, 0)
    weatherText.write(str(round_half_up(fc["feels_like"], 1)) + degree_sign, align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, -weatherText_vertSpacing)
    weatherText.write("POP", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # POP

    weatherText.goto(weatherText_Data, -weatherText_vertSpacing)
    weatherText.write(str(int(fc["pop"]*100)) + " %", align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, -weatherText_vertSpacing*2)
    weatherText.write("Rain", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # Rain

    weatherText.goto(weatherText_Data, -weatherText_vertSpacing*2)
    if 'rain' not in fc:
        weatherText.write("--", align="left", font=("Verdana", weatherText_DataFontSize, "bold"))
    else:
        weatherText.write(str(round_half_up(fc["rain"]["1h"] / 25.4, 2)) + " in", align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, -weatherText_vertSpacing*3)
    weatherText.write("Wind", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # Wind

    weatherText.goto(weatherText_Data, -weatherText_vertSpacing*3)
    weatherText.write(str(round_half_up(fc["wind_speed"] * 0.6213712, 1)) + " mph", align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, -weatherText_vertSpacing*4)
    weatherText.write("Gust", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # Wind

    weatherText.goto(weatherText_Data, -weatherText_vertSpacing*4)
    weatherText.write(str(round_half_up(fc["wind_gust"] * 0.6213712, 1)) + " mph", align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.goto(weatherText_Description, -weatherText_vertSpacing*5)
    weatherText.write("code", align="right", font=("Verdana", weatherText_DescriptionFontSize, "bold")) # Wind

    weatherText.goto(weatherText_Data, -weatherText_vertSpacing*5)
    weatherText.write(fc["weather"][0]["id"], align="left", font=("Verdana", weatherText_DataFontSize, "bold"))

    weatherText.hideturtle()

    weatherDividerPen.pensize(3)

    weatherDividerPen.penup()
    weatherDividerPen.goto(0, -150)
    weatherDividerPen.color("white")
    weatherDividerPen.setheading(90)
    weatherDividerPen.pendown()
    weatherDividerPen.fd(300)
    weatherDividerPen.hideturtle()
    
def forecast_click(x, y):
    global weatherText, weatherDividerPen
    if touchInBox(x, y, 0, 0, 200, 200):
        weatherText.clear()
        weatherDividerPen.clear()
        return False
    return None
        
def update_forecast():
    '''
    weather ID breakdown https://openweathermap.org/weather-conditions
    use https://ezgif.com/maker for gif conversion
    '''
    global hourCursor, data, idImage_array

    currentHour = int(time.strftime("%H"))
    if currentHour > 12:
        hourCursor = currentHour - 12
    elif currentHour == 0:
        hourCursor = 12
    else:
        hourCursor = currentHour

    idImage_array = forecast.get_image_array(data["hourly"])

    '''
    for num in range(12):
        id_array[num] = data["hourly"][num]["weather"][0]["id"]

        if 200 <= id_array[num] and id_array[num] <= 232:
            idImage_array[num] = "plugins/icons/11d@2x.gif"
        elif 300 <= id_array[num] and id_array[num] <= 321:
            idImage_array[num] = "plugins/icons/09d@2x.gif"
        elif 500 <= id_array[num] and id_array[num] <= 504:
            idImage_array[num] = "plugins/icons/10d@2x.gif"
        elif id_array[num] == 511:
            idImage_array[num] = "plugins/icons/13d@2x.gif"
        elif 520 <= id_array[num] and id_array[num] <= 531:
            idImage_array[num] = "plugins/icons/09d@2x.gif"
        elif 600 <= id_array[num] and id_array[num] <= 622:
            idImage_array[num] = "plugins/icons/13d@2x.gif"
        elif 701 <= id_array[num] and id_array[num] <= 781:
            idImage_array[num] = "plugins/icons/50d@2x.gif"
        elif id_array[num] == 800:
            idImage_array[num] = "plugins/icons/01d@2x.gif"
        elif id_array[num] == 801:
            idImage_array[num] = "plugins/icons/02d@2x.gif"
        elif id_array[num] == 802:
            idImage_array[num] = "plugins/icons/03d@2x.gif"
        elif id_array[num] == 803 or id_array[num] == 804:
            idImage_array[num] = "plugins/icons/04d@2x.gif"
        else:
            print("Invalid weather ID")

    for image in idImage_array:
        wn.addshape(image)
    '''

touch_fcn = None

def clock_click(x, y):
    '''
    when this event is triggered, it means someone pressed the screen,
    therefore we should check what state we are going into (clock mode,
    or hourly detail mode)
    '''
    global cursor_x, cursor_y, cursor_xform, clock_mode, mode, touch_fcn

    cursor_x = x * cursor_xform
    cursor_y = y * cursor_xform

    print(f"Click! ({cursor_x}, {cursor_y})")

    hourTouched = False

    for i in range(0, 12):
        if (touchInBox(cursor_x, cursor_y, hours[i][0], hours[i][1], hourlyTouchSize, hourlyTouchSize)):
            hourTouched = i + 1
            break

        
    if clock_mode:
        if alerts.click(cursor_x, cursor_y) != None:
            touch_fcn = alerts.click
            clock_mode = False
        elif hourTouched:
            touch_fcn = forecast_click
            clock_mode = False
            draw_weather_text(hourTouched)
    else:
        if touch_fcn:
            if touch_fcn(cursor_x, cursor_y) == False:
                touch_fcn = None
                clock_mode = True


bg_hours = [None]*12
for i in range(0, 12):
    bg_hours[i] = turtle.Turtle()
    bg_hours[i].goto(hours[i][0], hours[i][1])


def draw_clock(h, m, s, pen): # draw a clock using the pen i created
    global dateText
    # Draw the clock face
    #pen.up()
    # pen.goto(0, 210)
    # pen.setheading(180)
    # pen.color("green")
    # pen.pendown()
    # pen.circle(210)

    # Draw lines for the hours
    # pen.penup()
    # pen.goto(0,0)
    # pen.setheading(90)

    # for _ in range(12):
    #     pen.fd(190)
    #     pen.pendown()
    #     pen.fd(20)
    #     pen.penup()
    #     pen.goto(0,0)
    #     pen.rt(30)

    pen.hideturtle()

    # Draw the hour hand
    pen.penup()
    pen.goto(0,0)
    pen.color("white")
    pen.setheading(90)
    angle = (h / 12) * 360 + (m/60) * 30
    pen.rt(angle)
    pen.pendown()
    pen.fd(radius / 2 - 10)

    # Draw the minute hand
    pen.penup()
    pen.goto(0,0)
    pen.color("white")
    pen.setheading(90)
    angle = (m / 60) * 360  # optional + (s/60) * 6
    pen.rt(angle)
    pen.pendown()
    pen.fd(2 * radius / 3 + 30)

    # Draw the second hand
    pen.penup()
    pen.goto(0,0)
    pen.color("red")
    pen.setheading(90)
    angle = (s / 60) * 360
    pen.rt(angle)
    pen.pendown()
    pen.fd(radius / 3 * 2)

    # Draw circle
    pen.penup()
    pen.goto(10,0)
    pen.setheading(90)
    pen.color("white")
    pen.pendown()
    pen.begin_fill()
    pen.circle(10)
    pen.end_fill()
    
    wn.update()
    
    # Draw circle
    '''
    pen.penup()
    pen.goto(radius,0)
    pen.setheading(90)
    pen.color("green")
    pen.pendown()
    #pen.begin_fill()
    pen.circle(radius)
    #pen.end_fill()
    '''

turtle.onscreenclick(clock_click)

last_fetch = None

while True:
    h = int(time.strftime("%I"))
    m = int(time.strftime("%M"))
    s = int(time.strftime("%S"))
    d = time.strftime("%d")
    
    if d != day and clock_mode:
        day = d
        dateText.clear()
        dateText.color("white")
        dateText.setheading(270)
        dateText.goto(186,28)
        dateText.write(time.strftime("%b").upper(), align="center", font=("Verdana", 18, "bold"))
        dateText.fd(68)
        dateText.write(day, align="center", font=("Verdana", 48, "normal"))
        dateText.fd(18)
        dateText.write(time.strftime("%a").upper(), align="center", font=("Verdana", 18, "bold"))
    elif day != None and not clock_mode:
        day = None
        dateText.clear()
        
    alerts.update(data)
    sun.update(data)

    if (m % weatherUpdatePeriod == 0 and s == 0):
        if m != last_fetch:
            data = fetch_weather_data(url)
            last_fetch = m

    if clock_mode:
        draw_clock(h, m, s, pen)
        update_forecast()

        for i in range(1, 13):
            if(i-hourCursor < 0):
                bg_hours[i-1].shape(idImage_array[12-abs(i-hourCursor)])
            else:
                bg_hours[i-1].shape(idImage_array[i-hourCursor])

    wn.update()
    time.sleep(0.25)
    pen.clear()
