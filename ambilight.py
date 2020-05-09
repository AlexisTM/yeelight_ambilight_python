#!/bin/env python3
import time
import yeelight
from PIL import ImageGrab, Image

import numpy as np
np.seterr(all='raise')
from colour import sRGB_to_XYZ, XYZ_to_xy, xy_to_CCT

DO_MAIN = True
DO_MAIN_MOON = True
DO_AMBIENT = True

DELAY = 0.05
MAX_MAIN_LUMINOSITY = 15
LUMINOSITY_THRESHOLD = 1
TEMPERATURE_THRESHOLD = 100
COLOR_THRESHOLD = 25

LIGHT_IP = "192.168.178.20"

class MultiClient:
    def __init__(self, ip):
        self.clients = [
            yeelight.Bulb(
                ip,
                effect="smooth",
                duration=100,
                auto_on=False,
                model=yeelight.BulbType.WhiteTempMood,
            ),
            yeelight.Bulb(
                ip,
                effect="smooth",
                duration=100,
                auto_on=False,
                model=yeelight.BulbType.WhiteTempMood,
            ),
            yeelight.Bulb(
                ip,
                effect="smooth",
                duration=100,
                auto_on=False,
                model=yeelight.BulbType.WhiteTempMood,
            ),
        ]
        self.index = 0

    def get(self):
        self.index += 1
        return self.clients[self.index % 3]

    def send_command(self, method, params):
        self.get().send_command(method, params).get("result", [])

def RGB_dist(rgb1, rgb2):
    return abs(rgb1[0] - rgb2[0]) + abs(rgb1[1] - rgb2[1]) + abs(rgb1[2] - rgb2[2])


def RGB_to_CCT(rgb):
    RGB = np.array(rgb)
    XYZ = sRGB_to_XYZ(RGB / 255)
    xy = XYZ_to_xy(XYZ)
    CCT = xy_to_CCT(xy, "hernandez1999")
    return CCT


def main():
    last_CCT = 0
    last_L = 0
    last_L_Ambient = 0
    last_RGB = (0, 0, 0)
    while True:
        image = ImageGrab.grab()
        image.crop(image.getbbox())
        image = image.resize((100, 100), resample=Image.NEAREST)
        converted_image = image.convert("P", palette=Image.ADAPTIVE, colors=32)
        colors = sorted(converted_image.getcolors(32))
        palette = converted_image.getpalette()
        dominant_color = colors[-1]
        rgb = palette[dominant_color[1] * 3 : dominant_color[1] * 3 + 3]

        black_n_white = image.convert('L')
        black_n_white = black_n_white.resize((1, 1), resample=Image.BICUBIC)
        luminosity = black_n_white.getpixel((0,0))*100/255

        try:
            cct = int(RGB_to_CCT(rgb))
            if cct > 6500 or cct < 1500:
                cct = last_CCT
        except:
            print("CCT exception")
            cct = last_CCT

        if DO_MAIN:
            if DO_MAIN_MOON:
                if abs(luminosity - last_L) > LUMINOSITY_THRESHOLD:
                    lights.send_command("set_scene", ["nightlight", luminosity])
            else:
                if abs(luminosity - last_L) > 25 or abs(last_CCT - cct) > TEMPERATURE_THRESHOLD:
                    effective_luminosity = luminosity * MAX_MAIN_LUMINOSITY / 100
                    effective_luminosity = effective_luminosity if effective_luminosity > 1 else 1
                    lights.send_command("set_scene", ["ct", cct, effective_luminosity])
            last_L = luminosity
            last_CCT = cct

        if DO_AMBIENT:
            if luminosity < 15:
                if last_L_Ambient != 0:
                    lights.send_command(
                        "bg_set_scene",
                        [
                            "color",
                            yeelight.utils.rgb_to_yeelight(rgb[0], rgb[1], rgb[2]),
                            luminosity,
                        ],
                    )
                    last_L_Ambient = 0
            else:
                if RGB_dist(last_RGB, rgb) > COLOR_THRESHOLD:
                    lights.send_command(
                        "bg_set_scene",
                        [
                            "color",
                            yeelight.utils.rgb_to_yeelight(rgb[0], rgb[1], rgb[2]),
                            100,
                        ],
                    )
                    last_RGB = rgb

        time.sleep(DELAY)


lights = MultiClient(LIGHT_IP)
lights.get().turn_on(yeelight.LightType.Main)
lights.get().turn_on(yeelight.LightType.Ambient)

try:
    main()
except Exception as ex:
    print(ex)
    lights.get().turn_off()
