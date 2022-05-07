
import math
import time
import turtle
import json
import settings
from datetime import datetime
from utils import touch_in_box, round_half_up

wind_colors = [
    (69/255,117/255,180/255),
    (116/255,173/255,209/255),
    (171/255,217/255,233/255),
    (224/255,243/255,248/255),
    (254/255,224/255,144/255),
    (253/255,174/255,97/255),
    (244/255,109/255,67/255),
    (215/255,48/255,39/255)
]

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
    fc = data["hourly"][idx] if idx < 48 else data["current"]
    dt = datetime.fromtimestamp(fc["dt"])

    degree_sign = u"\N{DEGREE SIGN}"

    precip = "rain"
    precip_name = "Rain"
    
    if "snow" in fc:
        precip = "snow"
        precip_name = "Snow"
    
    return [
        ("Day", dt.strftime('%A')),
        ("Hour", dt.strftime('%H:%M')),
        ("Weather", f"{fc['weather'][0]['description']}"),
        ("Temperature", f"{round_half_up(fc['temp'], 1)} {degree_sign}C"),
        ("Feels like", f"{round_half_up(fc['feels_like'], 1)} {degree_sign}C"),
        ("Humidity", f"{fc['humidity']} %"),
        ("Pressure", f"{fc['pressure']} hPa"),
        ("PoP", f"{round_half_up(fc['pop']*100)} %" if 'pop' in fc else "--"),
        (f"{precip_name}", f"{round_half_up(fc[precip]['1h'] / 25.4, 2)} in" if precip in fc else "--"),
        ("Wind", f"{round_half_up(fc['wind_speed'] * 3.6 * 0.6213712, 1)} mph" if "wind_speed" in fc else "--"),
        ("Gust", f"{round_half_up(fc['wind_gust'] * 3.6 * 0.6213712, 1)} mph" if "wind_gust" in fc else "--"),
        #("code", f"{fc['weather'][0]['id']}")
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

    fc = get_hourly_forecasts(data, hours_ahead)
    txt.color('pink' if hours_ahead > 48 else 'white')

    height = SPACING * (len(fc) - 1)
    txt.goto(txt_x, height/2 - HCHAR/2)
    val.goto(val_x, height/2 - HCHAR/2)

    for line in fc:
        txt.write(line[0], align="right", font=("Verdana", FONT_SIZE, "bold"))
        txt.fd(SPACING)
        val.write(line[1], align="left", font=("Verdana", FONT_SIZE, "bold"))
        val.fd(SPACING)

    pen.penup()
    pen.goto(0, (height + SPACING) / 2)
    print("Pen y: {(height + SPACING) / 2}")
    pen.pendown()
    pen.fd(height + SPACING)

    hd = data['hourly'][hours_ahead] if hours_ahead < 48 else data['current']
    if "wind_deg" in hd:
        wind.clear()
        draw_arrow(hd['wind_speed'], hd['wind_deg'], 220)
        if 'wind_gust' in hd:
            draw_arrow(hd['wind_gust'], hd['wind_deg'], 230)

def draw_arrow(mps, heading, radius):
    wind_spd = mps * 3.6 * 0.6213712
    wind_ci = int(wind_spd) // 10
    if wind_ci > 7:
        wind_ci = 7
    color = wind_colors[wind_ci]
    #wind_deg_to = heading + 180
    wind_rad = heading * math.pi / 180
    (x, y) = (math.sin(wind_rad) * radius, math.cos(wind_rad) * radius)
    #wind.colormode(255)
    wind.goto(x, y)
    wind.setheading(270 - heading)
    wind.pendown()
    wind.color(color)
    wind.begin_fill()
    wind.right(150)
    wind.forward(30)
    wind.right(150)
    wind.forward(30 / math.sqrt(3))
    wind.left(60)
    wind.forward(30 / math.sqrt(3))
    wind.right(150)
    wind.forward(30)
    wind.end_fill()
    wind.penup()

def update(data):
    '''
    weather ID breakdown https://openweathermap.org/weather-conditions
    use https://ezgif.com/maker for gif conversion
    '''
    global bg_hours, active, last_on

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

    if active:
        if time.time() - last_on < TIMEOUT:
            draw_weather_text(data)
        else:
            close_forecast()
            active = False
            return False
    else:
        if "wind_deg" in data["current"]:
            wind.clear()
            draw_arrow(data['current']['wind_speed'], data['current']['wind_deg'], 220)
            if 'wind_gust' in data['current']:
                draw_arrow(data['current']['wind_gust'], data['current']['wind_deg'], 230)

def close_forecast():
    global txt, val, pen, on_screen
    txt.clear()
    val.clear()
    pen.clear()
    wind.clear()
    on_screen = False

def click(x, y):
    global active, hour_touched
    if not active:
        if hour_touched == 1000:
            hour_touched = False
            return False
        return click_on(x, y)
    else:
        return click_off(x, y)

def click_on(x, y):
    global hours, hour_touched, active, last_on
    hour_touched = False
    
    if touch_in_box(x, y, 0, 0, hourlyTouchSize, hourlyTouchSize):
        hour_touched = 1000
    else:
        for i in range(0, 12):
            if touch_in_box(x, y, hours[i][0], hours[i][1], hourlyTouchSize, hourlyTouchSize):
                hour_touched = i + 1
                break
    close_forecast()
    if hour_touched:
        active = True
        last_on = time.time()
    else:
        active = False
    return hour_touched

def click_off(x, y):
    global active
    if touch_in_box(x, y, 0, 0, 200, 200):
        close_forecast()
        active = False
        return False
    else:
        return click_on(x, y)
    return None

icon_set_name = settings.ICON_SET_NAME
hour_touched = None
hourlyTouchSize = 140
active = False
on_screen = False
last_on = 0

codes = {}
hours = []
bg_hours = [None]*12

FONT_SIZE = 18
SPACING = 30
HCHAR = 24
TIMEOUT = 90

# create our drawing pens
txt = turtle.Turtle(visible=False)
txt.penup()
txt.color("white")
txt.setheading(270)
txt_x = -20

val = turtle.Turtle(visible=False)
val.penup()
val.color("white")
val.setheading(270)
val_x = 20

pen = turtle.Turtle(visible=False)
pen.pensize(3)
pen.color("white")
pen.setheading(270)

wind = turtle.Turtle(visible=False)
wind.penup()
wind.color("white")
