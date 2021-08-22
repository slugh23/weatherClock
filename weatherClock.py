import time
import turtle
import json
import requests
import globals
from datetime import datetime
from plugins.utils import round_half_up, touch_in_box
from plugins import alerts, sun, forecast, special_events

# currently set to Vancouver, BC CANADA
#latitude = 49.2827
#longtitude = -123.1207

settings = globals.get_settings()

url = f'{globals.OWM_BASEURI}?lat={settings["latitude"]}&lon={settings["longitude"]}&exclude={globals.OWM_EXCLUDES}&appid={settings["APIKEY"]}&units=metric'

clock_mode = True
radius = globals.CLOCK_RADIUS

data = None
weatherUpdatePeriod = 10

#current_hour = 0
day = None

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
pen = turtle.Turtle(visible=False)
pen.speed(0)
pen.pensize(3)

weatherText = turtle.Turtle(visible=False)
weatherText_Description = -30
weatherText_Data = 30
weatherText_vertSpacing = 30
weatherText_DescriptionFontSize = 18
weatherText_DataFontSize = 18
sun.FontSize = weatherText_DataFontSize

weatherDividerPen = turtle.Turtle(visible=False)

degree_sign = u"\N{DEGREE SIGN}"

dateText = turtle.Turtle(visible=False)
dateText.penup()

wn = pen.getscreen()
wn.bgcolor("black")
wn.screensize()

if "screen" in settings:
    wn.setup(width=settings["screen"]["width"], height=settings["screen"]["height"])
else:
    wn.setup(width = 1.0, height = 1.0)

wn.title("WeatherClock 0.0.0")
wn.tracer(0)

print(dir(forecast))
forecast.initialize(wn)

def draw_weather_text(hourTouched):
    global pen, dateText, day
    
    day = None

    current_hour = int(time.strftime("%H"))
    hoursAhead = hourTouched - current_hour
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
    if touch_in_box(x, y, 0, 0, 200, 200):
        weatherText.clear()
        weatherDividerPen.clear()
        return False
    return None
        

touch_fcn = None

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

    hourTouched = forecast.click(cursor_x, cursor_y)
        
    if clock_mode:
        if alerts.click(cursor_x, cursor_y) != None:
            touch_fcn = alerts.click
            clock_mode = False
        elif special_events.click(cursor_x, cursor_y) != None:
            touch_fcn = special_events.click
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
    elif not clock_mode:
        day = None
        pen.clear()
        dateText.clear()
        
    alerts.update(data)
    sun.update(data)
    special_events.update(data)

    if (m % weatherUpdatePeriod == 0 and s == 0):
        if m != last_fetch:
            data = fetch_weather_data(url)
            last_fetch = m

    if clock_mode and s != last_draw:
        last_draw = s
        pen.clear()
        draw_clock(h, m, s, pen)
        forecast.update(data)


    wn.update()
    time.sleep(0.25)
