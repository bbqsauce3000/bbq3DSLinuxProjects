#!/usr/bin/env python3
import subprocess

# A development of "greennotificationledexample.py".
# This will show how to create a blinking LED, as well as how to switch colors!

# Animation/timing parameters.
animation = [0x00, 0x00, 0x00, 0x04]
# Animation settings:
#
# Byte 0 (first byte) - Delay: 
# How long each animation step is displayed.
# Uses 1/16 second units:
# 0x01 = 1/16 second
# 0x10 = 1 second
# 0x20 = 2 seconds
# 0xFF = about 16 seconds
#
# Byte 1 - Smoothing:
# Controls how smoothly the LED transitions between animation steps.
# Lower values = less smoothing.
#
# Byte 2 - Loop delay:
# How long to wait before repeating the animation.
# Uses the same 1/16 second units as the delay.
# 0x00 = no delay between loops
# 0xFF = play the pattern only once
#
# Byte 3 - Blink speed:
# Controls the speed of the LED's blinking.
# This is separate from the delay values above.
# Alternate between full brightness and off.

# IMPORTANT!!!
# [0xFF, 0x00] is two bytes. This means that the 32 bytes per color becomes 64 bytes for the color!
# To keep the channel at 32 bytes, use * 16 instead.
# * 16 repeats the two-byte sequence 16 times: 2 * 16 = 32.
red = [0xA5, 0x00] * 16
green = [0x55, 0x00] * 16
blue = [0x00] * 32
# You can use hexcodes as your reference to change the color on the notification LED!
# For example, the hexcode I used for this example was #A55500, you split the Red, Green, and Blue values into bytes. (RGB!)
# Therefore, the hex codes would be translated to bytes as [0xA5], [0x55], [0x00].
# If a part of the hex code is blank, like blue in this example, and the payload is animated, 
# simply write the byte as it was not animated, multiplying it by 32.

# 4 animation bytes + 32 bytes per color = 100 bytes.
payload = animation + red + green + blue

assert len(payload) == 100

# 0x25 = 3DS MCU
# 0x2D = notification LED pattern register
# 101 bytes = register byte + 100-byte pattern
args = [
    "sudo", "i2ctransfer", "-y", "-f", "1",
    "w101@0x25", "0x2D"
] + [f"0x{x:02X}" for x in payload]

subprocess.run(args, check=True)

print("A friend came online!")