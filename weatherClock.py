import time
import turtle
import json
import requests
import settings
from datetime import datetime
from utils import touch_in_box
from plugins import alerts, sun, forecast, special_events

# currently set to Vancouver, BC CANADA
#latitude = 49.2827
#longtitude = -123.1207

print(globals())

cfg = settings.settings

radius = settings.CLOCK_RADIUS
clock_mode = True
data = None
current_day = None


def fetch_weather_data():
    res = requests.get(settings.WEATHER_DATA_URL)
    weather_data = res.json()
    with open("/tmp/weather.json", "w") as cache:
        cache.write(json.dumps(weather_data))
    return weather_data

try:
    with open("/tmp/weather.json", "r") as cache:
        data = json.loads(cache.read())
        if data["hourly"][1]["dt"] < time.time():
            print("Old data --  Refreshing cache!")
            data = fetch_weather_data()
except:
    data = fetch_weather_data()
    
if data == None:
    data = fetch_weather_data()

#if "alerts" not in data:
#    data["alerts"] = [{"sender_name": "NWS Buffalo (Western New York)", "event": "Heat Advisory", "start": 1628668260, "end": 1628726400, "description": "...HEAT ADVISORY REMAINS IN EFFECT UNTIL 8 PM EDT THIS EVENING...\n* WHAT...Heat index values this afternoon from the upper 90s to\n105.\n* WHERE...Niagara, Orleans, Monroe, Wayne, and Livingston\ncounties.\n* WHEN...Until 8 PM EDT this evening.\n* IMPACTS...Hot temperatures and high humidity may cause heat\nillnesses to occur.", "tags": ["Extreme temperature value"]}]

cursor_x = 0
cursor_y = 0
cursor_xform = 1
if "invert-cursor" in cfg:
    cursor_xform = -1 if cfg["invert-cursor"] else 1

pen = turtle.Turtle(visible=False)
pen.speed(0)
pen.pensize(3)

dateText = turtle.Turtle(visible=False)
dateText.penup()

wn = pen.getscreen()
wn.bgcolor("black")
wn.screensize()

if "screen" in cfg:
    wn.setup(width=cfg["screen"]["width"], height=cfg["screen"]["height"])
else:
    wn.setup(width = 1.0, height = 1.0)

wn.title("WeatherClock 0.0.0")
wn.tracer(0)

forecast.initialize(wn)



touch_fcn = None

def set_click_fcn(function):
    global touch_fcn, clock_mode, pen, dateText
    if function is None:
        clock_mode = True
    else:
        pen.clear()
        dateText.clear()
        clock_mode = False
    touch_fcn = function


def clock_click(x, y):
    '''
    when this event is triggered, it means someone pressed the screen,
    therefore we should check what state we are going into (clock mode,
    or hourly detail mode)
    '''
    global cursor_x, cursor_y, cursor_xform, clock_mode, touch_fcn

    cursor_x = x * cursor_xform
    cursor_y = y * cursor_xform

    print(f"Click! ({cursor_x}, {cursor_y})")

    if clock_mode:
        if alerts.click(cursor_x, cursor_y) != None:
            set_click_fcn(alerts.click)
        elif special_events.click(cursor_x, cursor_y) != None:
            set_click_fcn(special_events.click)
        elif forecast.click(cursor_x, cursor_y):
            set_click_fcn(forecast.click_off)
            forecast.draw_weather_text(data)
    else:
        if touch_fcn:
            if touch_fcn(cursor_x, cursor_y) == False:
                touch_fcn = None
                clock_mode = True


def draw_clock(h, m, s, pen): # draw a clock using the pen i created
    global radius
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

wn.onscreenclick(clock_click)

last_fetch = None
last_draw = None

while True:
    h = int(time.strftime("%I"))
    m = int(time.strftime("%M"))
    s = int(time.strftime("%S"))
    d = time.strftime("%d")
    
    if d != current_day and clock_mode:
        current_day = d
        dateText.clear()
        dateText.color("white")
        dateText.setheading(270)
        dateText.goto(186,28)
        dateText.write(time.strftime("%b").upper(), align="center", font=("Verdana", 18, "bold"))
        dateText.fd(68)
        dateText.write(current_day, align="center", font=("Verdana", 48, "normal"))
        dateText.fd(18)
        dateText.write(time.strftime("%a").upper(), align="center", font=("Verdana", 18, "bold"))
    elif not clock_mode:
        current_day = None
        
    alerts.update(data)
    sun.update(data)
    special_events.update(data)

    if (m % settings.UPDATE_PERIOD == 0 and s == 0):
        if m != last_fetch:
            data = fetch_weather_data()
            last_fetch = m

    if clock_mode:
        last_draw = s
        pen.clear()
        draw_clock(h, m, s, pen)
        forecast.update(data)


    wn.update()
    time.sleep(0.25)
