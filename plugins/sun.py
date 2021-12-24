from datetime import datetime
from utils import round_to_half
from utils import touch_in_box, round_half_up
import time
import turtle

FontSize = 24
SunFont = ("Arial", FontSize, "bold")
top_x = 270
top_y = -260
spacing = 35

pen = turtle.Turtle()
pen.hideturtle()
pen.speed(0)
pen.pensize(3)
pen.penup()
pen.setheading(270)

today = {"dt": None}
tomorrow = None

degree_sign = u"\N{DEGREE SIGN}"

def to_string(dt):
    return datetime.fromtimestamp(dt).strftime("%H:%M")

def draw_times():
    global today, tomorrow
    pen.goto(-1 * top_x, top_y)
    pen.color("cyan")
    pen.write(str(round_to_half(today["feels_like"]["morn"])) + degree_sign, align="center", font=SunFont)
    pen.fd(spacing)
    pen.color("yellow")
    pen.write(to_string(today["sunrise"]), align="center", font=SunFont)
    pen.fd(spacing)
    pen.color("orange")
    pen.write(to_string(today["sunset"]), align="center", font=SunFont)
    
    pen.goto(top_x, top_y)
    pen.color("cyan")
    pen.write(str(round_to_half(tomorrow["feels_like"]["morn"])) + degree_sign, align="center", font=SunFont)
    pen.fd(spacing)
    pen.color("yellow")
    pen.write(to_string(tomorrow["sunrise"]), align="center", font=SunFont)
    pen.fd(spacing)
    pen.color("orange")
    pen.write(to_string(tomorrow["sunset"]), align="center", font=SunFont)

def draw_text(data):
    global on_screen, draw
    if on_screen:
        return
    on_screen = True
    if draw != None:
        fc = draw(data['daily'])
        height = SPACING * (len(fc) - 1)
        hdr.goto(hdr_x, height/2 - HCHAR/2)
        val.goto(val_x, height/2 - HCHAR/2)

        for line in fc:
            hdr.write(line[0], align="right", font=("Verdana", FONT_SIZE, "bold"))
            hdr.fd(SPACING)
            val.write(line[1], align="left", font=("Verdana", FONT_SIZE, "bold"))
            val.fd(SPACING)

        div.penup()
        div.goto(0, (height + SPACING) / 2)
        print("Pen y: {(height + SPACING) / 2}")
        div.pendown()
        div.fd(height + SPACING)

def draw_today(daily):
    fc = daily[0]
    dt = datetime.fromtimestamp(fc["dt"])

    degree_sign = u"\N{DEGREE SIGN}"
    
    return [
        ("Day", dt.strftime('%A')),
        ("Morning", f"{round_to_half(fc['temp']['morn'])} ({round_to_half(fc['feels_like']['morn'])}){degree_sign}C"),
        ("Evening", f"{round_to_half(fc['temp']['eve'])} ({round_to_half(fc['feels_like']['eve'])}) {degree_sign}C"),
        ("Minimum", f"{round_to_half(fc['temp']['min'])} {degree_sign}C"),
        ("Maximum", f"{round_to_half(fc['temp']['max'])} {degree_sign}C"),
        ("Moonset", f"{to_string(fc['moonset'])}"),
        ("Moonrise", f"{to_string(fc['moonrise'])}"),
        ("Rain", f"{round_half_up(fc['rain'] / 25.4, 2) if 'rain' in fc else '--'}"),
        ("Snow", f"{round_half_up(fc['snow'] / 25.4, 2) if 'snow' in fc else '--'}"),
    ]

def draw_tomorrow(daily):
    info = [("Day", "Rain / Snow")]
    for i in range(1, 8):
        day = daily[i]
        info.append((
            datetime.fromtimestamp(day['dt']).strftime('%A'),
            f"{round_half_up(day['rain'] / 25.4, 2) if 'rain' in day else ' -- '} / {round_half_up(day['snow'] / 25.4, 2) if 'snow' in day else ' -- '}"
        ))
    return info

def update(data):
    global active, today, tomorrow, last_on
    daily = data["daily"]
    if daily[0]["dt"] != today["dt"]:
        today = daily[0]
        tomorrow = daily[1]
        pen.clear()
        draw_times()
    if active:
        if time.time() - last_on < TIMEOUT:
            draw_text(data)
        else:
            close_sun()
            active = False
            return False

def close_sun():
    global active, draw, on_screen
    hdr.clear()
    val.clear()
    div.clear()
    active = False
    draw = None
    on_screen = False

def click(x, y):
    global active
    if active:
        return click_off(x, y)
    else:
        return click_on(x, y)

def click_on(x, y):
    global active, draw, last_on
    if touch_in_box(x, y, -270, -280, 100, 100):
        close_sun()
        draw = draw_today
    elif touch_in_box(x, y, 270, -280, 100, 100):
        close_sun()
        draw = draw_tomorrow
    else:
        return None
    
    active = True
    last_on = time.time()
    return True

def click_off(x, y):
    if not (touch_in_box(x, y, -270, -280, 100, 100) or touch_in_box(x, y, 270, -280, 100, 100)):
        close_sun()
        return False
    else:
        click_on(x, y)
    return None

active = False
on_screen = False
draw = None
last_on = 0

FONT_SIZE = 18
SPACING = 30
HCHAR = 24
TIMEOUT = 90

# create our drawing pens
hdr = turtle.Turtle(visible=False)
hdr.penup()
hdr.color("white")
hdr.setheading(270)
hdr_x = -20

val = turtle.Turtle(visible=False)
val.penup()
val.color("white")
val.setheading(270)
val_x = 20

div = turtle.Turtle(visible=False)
div.pensize(3)
div.color("white")
div.setheading(270)
