#!/usr/bin/env python3
import subprocess

# 3DS MCU notification LED
# I2C bus: 1
# MCU address: 0x25
# Notification LED register: 0x2D

# Animation:
# delay       = 0x00 -> play the first pattern value immediately
# smoothing   = 0x00
# loop_delay  = 0x00 -> continuously loop
# blink_speed = 0x00
animation = [0x00, 0x00, 0x00, 0x00]

# 32 samples for each color channel.
# Green is full, red and blue are off.
red = [0x00] * 32
green = [0xFF] * 32
blue = [0x00] * 32

payload = animation + red + green + blue

assert len(payload) == 100

# 0x25 = 3DS MCU
# 0x2D = notification LED pattern register
# 101 bytes = register byte + 100-byte pattern
args = [
    "i2ctransfer", "-y", "-f", "1",
    f"w101@0x25",
    "0x2D"
] + [f"0x{x:02X}" for x in payload]

subprocess.run(["sudo"] + args, check=True)

print("Notification LED pattern sent: green")
