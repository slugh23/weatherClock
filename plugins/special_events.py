import json
import time
from datetime import datetime
import turtle

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
    if "month" in trigger and trigger["month"] != month:
        return False
    if "day" in trigger and trigger["day"] != day:
        return False
    if "dow" in trigger and trigger["dow"] != dow:
        return False
    return True

def get_events(month, day, dow):
    global events
    today_events = []
    for e in events:
        if test_event(month, day, dow, e["trigger"]):
            today_events.append(e)
    return today_events

def get_events_today():
    month = int(time.strftime("%m"))
    day = int(time.strftime("%d"))
    dow = int(time.strftime("%w"))
    return get_events(month, day, dow)

wn = turtle.getscreen()

events = None
with open("special-events.json", "r") as events_file:
    events = json.loads(events_file.read())

#all = expand_events(events)
#print(all)

#print(get_events(12, 3, 1))
#print(get_events(1, 1, None))
