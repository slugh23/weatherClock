import turtle

PADDING = 5
HCHAR = 20
WCHAR = 9

txt = turtle.Turtle(visible=False)
#txt.hideturtle()
txt.speed(0)
txt.pensize(3)

alt = turtle.Turtle(visible=False)
#alt.hideturtle()
alt.speed(0)
alt.penup()
alt.goto(-280,275)

alert_name = "plugins/icons/alert-64.gif"
alt.getscreen().addshape(alert_name)
alt.shape(alert_name)

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
    if "alerts" in data:
        #alt.shape(alert_name)
        alt.showturtle()
        alertable = True
        if active:
            display_alert(data["alerts"][0])
        else:
            close_alert()
    else:
        alt.hideturtle()
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
    
