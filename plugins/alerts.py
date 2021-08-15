import turtle

PADDING = 5
HCHAR = 20
WCHAR = 9

dot = turtle.Turtle()
dot.hideturtle()
dot.speed(0)
dot.pensize(3)
txt = turtle.Turtle()
txt.hideturtle()
txt.speed(0)
txt.pensize(3)

MsgFont = ("Inconsolata", 14, "bold")

alertable = False
active = False
on_screen = False

def get_dims(message):
    height = len(message) * HCHAR
    width = max([len(line) for line in message]) * WCHAR
    return (width, height)

def display_alert(alert):
    global on_screen
    lines = alert["description"].split('\n')
    (width, height) = get_dims(lines)
    boxw = width + 2 * PADDING
    boxh = height + 2 * PADDING
    
    if not on_screen:
        txt.penup()
        txt.goto(-1 * (width / 2 + PADDING) , height / 2 + PADDING)
        txt.setheading(90)
        txt.pendown()
        txt.fillcolor("white")
        txt.pencolor("red")
        txt.begin_fill()
        txt.rt(90)
        txt.fd(boxw)
        txt.rt(90)
        txt.fd(boxh)
        txt.rt(90)
        txt.fd(boxw)
        txt.rt(90)
        txt.fd(boxh)
        txt.end_fill()
        txt.penup()
        txt.goto(width / -2, height / 2 - HCHAR)
        txt.setheading(270)
        txt.color("black")
        for line in lines:
            txt.write(line, align="left", font=MsgFont)
            txt.getscreen().update()
            txt.fd(HCHAR)
        on_screen = True


def close_alert():
    global on_screen
    if on_screen:
        txt.clear()
        on_screen = False


def update(data):
    global active, alertable
    dot.clear()
    if "alerts" in data:
        dot.penup()
        dot.goto(-280, 300)
        dot.setheading(180)
        dot.pendown()
        dot.pencolor("white")
        dot.fillcolor("red")
        dot.begin_fill()
        dot.circle(30, None, 3)
        dot.end_fill()
        #dot.write("!", align="center", font=("Inconsolata", 24, "bold"))
        alertable = True
        if active:
            display_alert(data["alerts"][0])
        else:
            close_alert()
    else:
        alertable = False

def click(x, y):
    global active, alertable
    if alertable:
        if active:
            txt.clear()
            active = False
            return False
        else:
            if -360 < x and x < -240 and 240 < y and y < 360:
                active = True
                return True
    return None
    
