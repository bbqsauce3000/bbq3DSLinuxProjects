#!/usr/bin/env python3
import subprocess
# This is a copy of the previous "greennotificationled.py" for convenience on turning off the notification LED.
animation = [0x00, 0x00, 0x00, 0x00]

# All fields are zeroed out, this will turn off the LED.
red = [0x00] * 32
green = [0x00] * 32
blue = [0x00] * 32
payload = animation + red + green + blue

assert len(payload) == 100

# Register byte + 100-byte pattern = 101 bytes total.
args = [
    "i2ctransfer", "-y", "-f", "1",
    f"w101@0x25",
    "0x2D"
] + [f"0x{x:02X}" for x in payload]

subprocess.run(["sudo"] + args, check=True)

print("Turned off the notification LED!")
