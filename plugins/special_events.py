import json
import time
from datetime import datetime
import os.path
import turtle

FONT_SIZE = 18
PADDING = 5
HCHAR = 24
WCHAR = 12
HICON = 64
WICON = 64

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
    global evt, cleared
    wn = evt.getscreen()
    shape = None
    if len(events) > len(cleared):
        for e in events:
            if e["description"] not in cleared:
                if "image" in e:
                    shape = get_fqip(e["image"])
                else:
                    shape = get_fqip(e["icon"])
                break

    if shape and shape not in wn.getshapes():
        wn.addshape(shape)

    return shape if shape else get_fqip("check-round")

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
    global cleared, cleared_day
    all_events = fetch_current_events()
    today_events = []
    if day != cleared_day:
        cleared = []
        cleared_day = day
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
    line_height = len(message) * HCHAR
    height = line_height if line_height > HICON else HICON 
    width = max([len(line) for line in message]) * WCHAR + WICON
    return (width, height + 2 * PADDING, line_height)

def get_regions(events):
    regions = []
    maxw = 0
    totalh = 0
    for e in events:
        desc = e["description"].split('\n')
        (width, height, lh) = get_dims(desc)
        #print(f"events: {width}, {height}, {lh}")
        regions.append({
            "width": width,
            "height": height,
            "text_base": (height + lh) / 2,
            "text": e["description"],
            "icon": e["icon"]
        })
        maxw = width if width > maxw else maxw
        totalh = totalh + height
    boxw = maxw + 3 * PADDING
    boxh = totalh
    return (regions, boxw, boxh)

def display_events(events):
    global on_screen, MsgFont, txt, cleared
    (regions, boxw, boxh) = get_regions(events)
    
    if not on_screen:
        txt.penup()
        txt.goto(-boxw / 2, boxh / 2)
        txt.setheading(0)
        txt.pendown()
        txt.fillcolor("white")
        txt.pencolor("green")
        txt.begin_fill()
        txt.fd(boxw)
        txt.rt(90)
        txt.fd(boxh)
        txt.rt(90)
        txt.fd(boxw)
        txt.rt(90)
        txt.fd(boxh)
        txt.end_fill()
        txt.penup()
        txt.goto(-boxw / 2, boxh / 2)
        first = True
        for reg in regions:
            if not first:
                txt.setheading(0)
                txt.pendown()
                txt.fd(boxw)
                txt.penup()
                txt.bk(boxw)
            txt.setheading(270)
            txt.fd(reg["height"])
            first = False
        txt.penup()
        txt.setheading(270)
        txt.color("black")
        txt.goto(-boxw / 2 + WICON + 2 * PADDING, boxh / 2)
        for reg in regions:
            pos = txt.pos()
            txt.fd(reg["text_base"])
            txt.write(reg["text"], align="left", font=MsgFont)
            txt.goto(pos)
            txt.fd(reg["height"])
        txt.goto(-boxw / 2 + WICON / 2 + PADDING, boxh / 2)
        for reg in regions:
            txt.fd(reg["height"] / 2)
            if reg["text"] not in cleared:
                txt.shape(get_fqip(f"{reg['icon']}"))
            else:
                txt.shape(get_fqip("check-round"))
            txt.stamp()
            txt.fd(reg["height"] / 2)
        on_screen = True

def close_event():
    global on_screen, txt
    if on_screen:
        txt.clearstamps()
        txt.clear()
        on_screen = False

def update(data):
    global active, alertable, evt #, cleared
    today = get_events_today()
    if len(today):
        if not alertable:
            evt.clearstamps()
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

def click_event(regions, top, y):
    global cleared
    b = top
    for r in regions:
        t = b
        b = t - r["height"]
        if b < y and y < t:
            if r["text"] not in cleared:
                cleared.append(r["text"])
            else:
                cleared.remove(r["text"])

def click(x, y):
    global active, alertable, txt
    if alertable:
        if active:
            (regions, boxw, boxh) = get_regions(get_events_today())
            if abs(x) < boxw / 2 and abs(y) < boxh / 2:
                click_event(regions, boxh / 2, y)
                alertable = False
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
cleared = []
cleared_day = 0

wn = evt.getscreen()
for e in fetch_current_events():
    if 'icon' in e:
        icon = get_fqip(f"{e['icon']}")
        if icon not in wn.getshapes():
            wn.addshape(icon)

#wn.addshape(get_fqip("check-list"))
#wn.addshape(get_fqip("check-square"))
wn.addshape(get_fqip("check-round"))
