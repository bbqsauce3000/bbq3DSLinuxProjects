#!/usr/bin/env python3
import subprocess

if os.geteuid() != 0:
    print("This program must be run as root.")
    print("Run it with: sudo ./led.py")
    sys.exit(1)

def i2c_write(register, value):
    subprocess.run([
        "i2ctransfer", "-y", "-f", "1",
        "w2@0x25", register, value
    ], check=True)


def notification_led(animation, red, green, blue):
    payload = animation + red + green + blue
    assert len(payload) == 100

    args = [
        "sudo", "i2ctransfer", "-y", "-f", "1",
        "w101@0x25", "0x2D"
    ] + [f"0x{x:02X}" for x in payload]

    subprocess.run(args, check=True)


def custom_color():
    color = input("Enter a hex color (example: #A55500): ").strip().lstrip("#")

    if len(color) != 6:
        print("Invalid hex color.")
        return

    try:
        red = int(color[0:2], 16)
        green = int(color[2:4], 16)
        blue = int(color[4:6], 16)
    except ValueError:
        print("Invalid hex color.")
        return

    print(f"Red:   0x{red:02X}")
    print(f"Green: 0x{green:02X}")
    print(f"Blue:  0x{blue:02X}")

    notification_led(
        [0x00, 0x00, 0x00, 0x04],
        [red] * 32,
        [green] * 32,
        [blue] * 32
    )


def green_notification():
    notification_led(
        [0x00, 0x00, 0x00, 0x00],
        [0x00] * 32,
        [0xFF] * 32,
        [0x00] * 32
    )


def green_flicker():
    notification_led(
        [0x00, 0x00, 0x00, 0x04],
        [0x00] * 32,
        [0xFF, 0x00] * 16,
        [0x00] * 32
    )


def friend_online():
    notification_led(
        [0x00, 0x00, 0x00, 0x04],
        [0xA5, 0x00] * 16,
        [0x55, 0x00] * 16,
        [0x00] * 32
    )


def notification_off():
    notification_led(
        [0x00, 0x00, 0x00, 0x00],
        [0x00] * 32,
        [0x00] * 32,
        [0x00] * 32
    )


while True:
    print("\n3DSLinux LED Control")
    print("1. Power LED - Blue")
    print("2. Power LED - Dim Blinking")
    print("3. Power LED - Off")
    print("4. Wi-Fi LED - On")
    print("5. Wi-Fi LED - Off")
    print("6. Notification LED - Green")
    print("7. Notification LED - Green Flicker")
    print("8. Notification LED - Custom Color")
    print("9. Notification LED - Off")
    print("0. Exit")

    choice = input("\nSelect an option: ")

    if choice == "1":
        i2c_write("0x29", "0x01")
    elif choice == "2":
        i2c_write("0x29", "0x02")
    elif choice == "3":
        i2c_write("0x29", "0x03")
    elif choice == "4":
        i2c_write("0x28", "0x0F")
    elif choice == "5":
        i2c_write("0x28", "0x00")
    elif choice == "6":
        green_notification()
    elif choice == "7":
        green_flicker()
    elif choice == "8":
        print("The notification LED is quite bright.")
        print("Vibrant hex codes may look washed out.")
        custom_color()
    elif choice == "9":
        notification_off()
    elif choice == "0":
        break
    else:
        print("Invalid option.")