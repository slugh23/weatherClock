import math

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

def round_to_half(n):
    return round_half_up(n * 2) / 2

def touch_in_box(touch_x, touch_y, center_x, center_y, size_x, size_y):
    if (touch_x > (center_x - size_x/2) and touch_x < (center_x + size_x/2) and touch_y > (center_y - size_y/2) and touch_y < (center_y + size_y/2)):
        return True
    else:
        return False

