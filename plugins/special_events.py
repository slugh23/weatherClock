import json
import time
from datetime import datetime
import os.path
import turtle

FONT_SIZE = 18
PADDING = 5
HCHAR = 24
WCHAR = 12
WICON = 24

def get_fqip(name):
    return f"plugins/icons/events/{name}.gif"

def add_event(events, month, day, dow, evt):
    if type(month) is list:
        for m in month:
            add_event(events, m, day, dow, evt)
    elif type(day) is list:
        for d in day:
            add_event(events, month, d, dow, evt)
    elif type(dow) is list:
        for n in dow:
            add_event(events, month, day, n, evt)
    else:
        events.append({
            "trigger": {
                "month": month,
                "day": day,
                "dow": dow
            },
            "description": evt["description"],
            "priority": evt["priority"],
            "image": evt["image"]
        })

def expand_event(evt):
    events = []
    trigger = evt["trigger"]
    month = trigger["month"] if "month" in trigger else None
    day = trigger["day"] if "day" in trigger else None
    dow = trigger["dow"] if "dow" in trigger else None
    add_event(events, month, day, dow, evt)
    return events


def expand_events(evts):
    expanded = []
    for e in evts:
        expanded.extend(expand_event(e))
    return expanded

def test_event(month, day, dow, trigger):
    if "disabled" in trigger and trigger["disabled"]:
        return False
    if "month" in trigger and trigger["month"] != month:
        return False
    if "day" in trigger and trigger["day"] != day:
        return False
    if "dow" in trigger and trigger["dow"] != dow:
        return False
    return True

def get_pen_shape(events):
    global evt
    wn = evt.getscreen()
    if "image" in events[0]:
        shape = get_fqip(events[0]["image"])
    else:
        shape = get_fqip(events[0]["icon"])

    if shape not in wn.getshapes():
        wn.addshape(shape)

    return shape

def sort_events(events):
    if len(events):
        return sorted(events, key=lambda evt: evt["priority"])
    return events

def fetch_current_events():
    global last_mod, events
    mod_time = os.path.getmtime("special-events.json")
    if mod_time > last_mod:
        events = None
        last_mod = mod_time
        with open("special-events.json", "r") as events_file:
            events = json.loads(events_file.read())
    return events

def get_events(month, day, dow):
    all_events = fetch_current_events()
    today_events = []
    for e in all_events:
        if test_event(month, day, dow, e["trigger"]):
            today_events.append(e)
    return sort_events(today_events)

def get_events_today():
    month = int(time.strftime("%m"))
    day = int(time.strftime("%d"))
    dow = int(time.strftime("%w"))
    return get_events(month, day, dow)

def get_dims(message):
    height = len(message) * HCHAR
    width = max([len(line) for line in message]) * WCHAR + WICON
    return (width, height)

def display_events(events):
    global on_screen, MsgFont, txt
    lines = []
    for e in events:
        lines.extend(e["description"].split('\n'))
    (width, height) = get_dims(lines)
    boxw = width + 2 * PADDING
    boxh = height + 2 * PADDING
    
    if not on_screen:
        txt.penup()
        txt.goto(-1 * (width / 2 + PADDING) , height / 2 + PADDING)
        txt.setheading(90)
        txt.pendown()
        txt.fillcolor("white")
        txt.pencolor("green")
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
        txt.goto(width / -2 + WICON, height / 2 - HCHAR)
        txt.setheading(270)
        txt.color("black")
        for line in lines:
            txt.write(line, align="left", font=MsgFont)
            txt.getscreen().update()
            txt.fd(HCHAR)
        txt.goto(width / -2 + WICON / 2, height / 2 - HCHAR / 2 + 1)
        for e in events:
            txt.shape(get_fqip(f"{e['icon']}-24"))
            txt.stamp()
            txt.fd(HCHAR * len(e['description'].split('\n')))
        on_screen = True

def close_event():
    global on_screen, txt
    if on_screen:
        txt.clearstamps()
        txt.clear()
        on_screen = False


def update(data):
    global active, alertable, evt
    today = get_events_today()
    if len(today):
        if not alertable:
            evt.shape(get_pen_shape(today))
            evt.stamp()
            alertable = True
        if active:
            display_events(today)
        else:
            close_event()
    else:
        evt.clearstamps()
        alertable = False

def click(x, y):
    global active, alertable, txt
    if alertable:
        if active:
            txt.clear()
            active = False
            return False
        else:
            if 240 < x and x < 360 and 240 < y and y < 360:
                active = True
                return True
    return None

txt = turtle.Turtle()
txt.hideturtle()
txt.speed(0)
txt.pensize(3)

evt = turtle.Turtle()
evt.hideturtle()
evt.speed(0)
evt.penup()
evt.goto(280,275)

MsgFont = ("Inconsolata", FONT_SIZE, "bold")

alertable = False
active = False
on_screen = False

last_mod = 0
events = None

wn = evt.getscreen()
for e in fetch_current_events():
    if 'icon' in e:
        icon = get_fqip(f"{e['icon']}-24")
        if icon not in wn.getshapes():
            wn.addshape(icon)

#all = expand_events(events)
#print(all)

#print(get_events(12, 3, 1))
#print(get_events(1, 1, None))
