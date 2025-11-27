import time
import turtle
import json
import requests
import settings
from datetime import datetime
from utils import round_half_up
from plugins import alerts, sun, forecast, special_events
import syslog
import paho.mqtt.client as MQTT


#https://www.weatherbit.io/api/codes

# currently set to Vancouver, BC CANADA
#latitude = 49.2827
#longtitude = -123.1207

cfg = settings.settings

mqtt_en = False
if "mqtt" in cfg:
    mqtt = cfg["mqtt"]
    mqtt_en = mqtt["enable"]

radius = settings.CLOCK_RADIUS
clock_mode = True
data = None
current_day = None
current_temp = None
mqtt_evt = None

cursor_xform = 1
if "invert-cursor" in cfg:
    cursor_xform = -1 if cfg["invert-cursor"] else 1


def fetch_weather_data():
    global error
    error.clearstamps()
    syslog.syslog(syslog.LOG_DEBUG, "Fetching forecast")
    tries = 6
    while tries > 0:
        try:
            res = requests.get(settings.WEATHER_DATA_URL)
            syslog.syslog(syslog.LOG_DEBUG, f"Status code: {res.status_code}")
            weather_data = res.json()
            with open("/tmp/weather.json", "w") as cache:
                cache.write(json.dumps(weather_data))
            return weather_data
        except Exception as ex:
            syslog.syslog(syslog.LOG_ERR, f"Fetch error: {ex}")
            tries = tries - 1
            time.sleep(3)
    error.stamp()
    return None

syslog.openlog(ident="wclock", logoption=syslog.LOG_PID, facility=syslog.LOG_USER)
syslog.setlogmask(syslog.LOG_UPTO(syslog.LOG_DEBUG))

pen = turtle.Turtle(visible=False)
pen.speed(0)
pen.pensize(3)

dateText = turtle.Turtle(visible=False)
dateText.penup()
dateFontName="DejaVuSans"

tempText = turtle.Turtle(visible=False)
tempText.penup()
tempFont=("DejaVuSans", 32, "normal")

mqttText = turtle.Turtle(visible=False)
mqttText.penup()
mqttFont = ("DejaVuSans", 24, "bold")

wn = pen.getscreen()
wn.bgcolor("black")
wn.screensize()
wn.addshape("clock.gif")
ps = pen.shape()
pen.shape("clock.gif")
pen.stamp()

wn.addshape("error.gif")
error = turtle.Turtle(visible=False)
error.penup()
error.shape("error.gif")
error.goto(-360 + 24, 360 - 24)#220)

if "screen" in cfg:
    wn.setup(width=cfg["screen"]["width"], height=cfg["screen"]["height"])
else:
    wn.setup(width = 1.0, height = 1.0)

wn.title("WeatherClock 0.0.0")
wn.tracer(0)

forecast.initialize(wn)

try:
    with open("/tmp/weather.json", "r") as cache:
        data = json.loads(cache.read())
        if data["hourly"][1]["dt"] < time.time():
            print("Old data --  Refreshing cache!")
            data = fetch_weather_data()
except:
    data = fetch_weather_data()

sleep = 5
while data is None:
    if sleep > 1400:
        quit()
    time.sleep(sleep)
    sleep = (sleep + 1) * 1.3
    data = fetch_weather_data()

#if "alerts" not in data:
#    data["alerts"] = [{"sender_name": "NWS Buffalo (Western New York)", "event": "Heat Advisory", "start": 1628668260, "end": 1628726400, "description": "...HEAT ADVISORY REMAINS IN EFFECT UNTIL 8 PM EDT THIS EVENING...\n* WHAT...Heat index values this afternoon from the upper 90s to\n105.\n* WHERE...Niagara, Orleans, Monroe, Wayne, and Livingston\ncounties.\n* WHEN...Until 8 PM EDT this evening.\n* IMPACTS...Hot temperatures and high humidity may cause heat\nillnesses to occur.", "tags": ["Extreme temperature value"]}]

pen.clearstamps()
pen.shape(ps)

touch_fcn = None

# The callback for when the client receives a CONNACK response from the server.
def on_konnect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("rtl_433/+/events")

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    global clock_mode, mqtt_evt
    if clock_mode:
        evt = json.loads(msg.payload.decode())
        mqtt_evt = evt

mc = False
def start_mqtt():
    global mc
    mc = MQTT.Client()
    mc.on_connect = on_konnect
    mc.on_message = on_message

    mc.connect(mqtt["host"], mqtt["port"], mqtt["timeout"])
    mc.loop_start()
    pass

def get_temperature(data):
    temp = data['feels_like'] if 'feels_like' in data else data['temp']
    return round_half_up(temp, 1)

def set_click_fcn(function):
    global touch_fcn, clock_mode, pen, dateText
    if function is None:
        clock_mode = True
    else:
        pen.clear()
        dateText.clear()
        tempText.clear()
        mqttText.clear()
        clock_mode = False
    touch_fcn = function


def clock_click(x, y):
    '''
    when this event is triggered, it means someone pressed the screen,
    therefore we should check what state we are going into (clock mode,
    or hourly detail mode)
    '''
    global cursor_xform, clock_mode, touch_fcn

    cursor_x = x * cursor_xform
    cursor_y = y * cursor_xform

    print(f"Click! ({cursor_x}, {cursor_y})")

    if clock_mode:
        if alerts.click(cursor_x, cursor_y) != None:
            set_click_fcn(alerts.click)
        elif special_events.click(cursor_x, cursor_y) != None:
            set_click_fcn(special_events.click)
        elif sun.click(cursor_x, cursor_y):
            set_click_fcn(sun.click)
        elif forecast.click(cursor_x, cursor_y):
            set_click_fcn(forecast.click)
    else:
        if touch_fcn:
            if touch_fcn(cursor_x, cursor_y) == False:
                set_click_fcn(None)
                clock_click(x, y)


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
    
    #wn.update()
    
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

if mqtt_en:
    start_mqtt()

run = True
try:
    while run:
        h = int(time.strftime("%I"))
        m = int(time.strftime("%M"))
        s = int(time.strftime("%S"))
        d = time.strftime("%d")
        tfl = get_temperature(data["current"])
        
        if clock_mode:
            if d != current_day:
                current_day = d
                dateText.clear()
                dateText.color("white")
                dateText.setheading(270)
                dateText.goto(186,28)
                dateText.write(time.strftime("%b").upper(), align="center", font=(dateFontName, 18, "bold"))
                dateText.fd(68)
                dateText.write(current_day, align="center", font=(dateFontName, 48, "normal"))
                dateText.fd(18)
                dateText.write(time.strftime("%a").upper(), align="center", font=(dateFontName, 18, "bold"))
            if tfl != current_temp:
                current_temp = tfl
                tempText.clear()
                tempText.color("cyan")
                tempText.goto(-160,-24)
                tempText.write(f'{current_temp}°', align="center", font=tempFont)
            if mqtt_evt:
                mqttText.clear()
                mqttText.color("white")
                mqttText.setheading(270)
                mqttText.goto(0,160)
                tempC = int((mqtt_evt['temperature_F'] - 32) * 50 / 9) / 10.0
                mqttText.write(f"{tempC}°", align="center", font=mqttFont)
                mqttText.fd(35)
                mqttText.write(f"{mqtt_evt['humidity']}%", align="center", font=mqttFont)
                mqtt_evt = None
        else:
            current_day = None
            current_temp = None

        updates = [
            alerts.update(data),
            sun.update(data),
            special_events.update(data),
            forecast.update(data),
        ]

        if False in updates:
            set_click_fcn(None)

        if m % settings.UPDATE_PERIOD == 0 and s == 0:
            if m != last_fetch:
                fetch = fetch_weather_data()
                if fetch is not None:
                    last_fetch = m
                    data = fetch

        if clock_mode:
            last_draw = s
            pen.clear()
            draw_clock(h, m, s, pen)

        wn.update()
        time.sleep(0.25)
except KeyboardInterrupt:
    run = False 
 
if mc:
    mc.loop_stop()
