from datetime import datetime
from utils import round_to_half
import settings
import turtle

FontSize = settings.FONT_SIZE
SunFont = ("Verdana", FontSize, "bold")

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
    pen.goto(-270, -270)
    pen.color("cyan")
    pen.write(str(round_to_half(today["temp"]["morn"])) + degree_sign, align="center", font=SunFont)
    pen.fd(30)
    pen.color("yellow")
    pen.write(to_string(today["sunrise"]), align="center", font=SunFont)
    pen.fd(30)
    pen.color("orange")
    pen.write(to_string(today["sunset"]), align="center", font=SunFont)
    
    pen.goto(270, -270)
    pen.color("cyan")
    pen.write(str(round_to_half(tomorrow["temp"]["morn"])) + degree_sign, align="center", font=SunFont)
    pen.fd(30)
    pen.color("yellow")
    pen.write(to_string(tomorrow["sunrise"]), align="center", font=SunFont)
    pen.fd(30)
    pen.color("orange")
    pen.write(to_string(tomorrow["sunset"]), align="center", font=SunFont)


def update(data):
    global today, tomorrow
    daily = data["daily"]
    if daily[0]["dt"] != today["dt"]:
        today = daily[0]
        tomorrow = daily[1]
        pen.clear()
        draw_times()

def click(x, y):
    return None
