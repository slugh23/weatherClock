
import turtle
import json

icon_set_name = "owm-std"
hour_touched = None

codes = {}

def initialize(screen):
    global codes
    with open(f"plugins/icons/{icon_set_name}/icons.json") as cfg:
        dork = cfg.read()
        icon_sets = json.loads(dork)
        for icon in icon_sets:
            for name in icon["images"]:
                shape = f"plugins/icons/{icon_set_name}/{name}.gif"
                if shape not in screen.getshapes():
                    screen.addshape(shape)
            for code in icon["codes"]:
                codes[code] = icon["images"]

def get_image_array(hourly):
    global codes
    images = []
    for idx in range(12):
        dork = hourly[idx]["weather"][0]["icon"][2]
        dn = 0 if dork == "d" else 1
        icons = codes[hourly[idx]["weather"][0]["id"]]
        images.append(f"plugins/icons/{icon_set_name}/{icons[dn]}.gif")
    return images