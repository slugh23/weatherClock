from os.path import exists
import json

codes = [
    200, 201, 202, 210, 211, 212, 221, 230, 231, 232,
    300, 301, 302, 310, 311, 312, 313, 314, 321,
    500, 501, 502, 503, 504, 511, 520, 521, 522, 531,
    600, 601, 602, 611, 612, 613, 615, 616, 620, 621, 622,
    701, 711, 721, 731, 741, 751, 761, 762, 771, 781,
    800,
    801, 802, 803, 804
]

with open("icons.json", "r") as icons_file:
    icons = json.loads(icons_file.read())

found = []
for icon in icons:
    for image in icon["images"]:
        if not exists(f"{image}.gif"):
            print(f"Missing icon: {image}.gif")
    for code in icon["codes"]:
        if code in found:
            print(f"Duplicate code found: {code}")
        else:
            found.append(code)

for code in codes:
    if code not in found:
        print(f"Code not found: {code}")
