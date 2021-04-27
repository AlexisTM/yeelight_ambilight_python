# yeelight_ambilight_python
Python ambilight for the Xiaomi Yeelight Jiaoyue 650 ceiling light

NOTE: Sadly, the limit of 60 request cannot be overcome on the ceiling lights.

## Installation

Clone and install dependencies

```py
git clone https://github.com/AlexisTM/yeelight_ambilight_python.git
cd yeelight_ambilight_python
python3 -m pip install -r requirements.txt
```

## Usage

Modify the following parameters:

```py
DO_MAIN = True # Use the main light
DO_MAIN_MOON = True # Use the main light as moon (DO_MAIN should be true)
DO_AMBIENT = True # Use ambient light

DELAY = 0.05 # Additional delay because the 650 cannot use the music mode
MAX_MAIN_LUMINOSITY = 15 # Maximal "main" luminosity (DO_MAIN on and DO_MAIN_MOON off)
LUMINOSITY_THRESHOLD = 1 # Update the main light if the luminosity changes of at least this
TEMPERATURE_THRESHOLD = 100 # Update the main light if the temperature changes of at least this
COLOR_THRESHOLD = 25 # Update the ambient light if the temperature changes of at least this

LIGHT_IP = "192.168.178.20" # The light IP, this creates 3 connections to allow higher rate.
```

## Methodology

1. Grab the screen image
    * Take a screenshot (ImageGrab.grab)
    * Cut the screenshot to fit the film size (image.getbbox)
2. Extract the dominant color
    * Resize the image to a small 100x100 size (nearest neightbour to keep the correct colors)
    * Convert the image to a 32 color image with adaptative palette
    * Get the most used color from these 32 colors subset in the generated palette
3. Compute the luminosity by using the black and white image resized to 1x1 using bicubic to get a mean color
4. Compute the temperature (using RGB to XYZ to xy to CCT)


## Dependencies

* Yeelight-python: Yeelight communication
* numpy: To use colour-science
* colour-science: To convert RGB to Temperature

