#!/usr/bin/env python3
import curses
import glob
import select
import time
from evdev import InputDevice, ecodes

# Continuation of the basic input tester, that is buttontest.py
# Instead of printing each event, this version keeps track of
# input state and renders it as a live terminal UI.
#
# The 3DS terminal is 30 rows by 50 columns, so the layout
# is designed specifically around those dimensions.

# Load Linux input codes from our bindings file.
bindings = {}

with open("buttonbindings.txt") as f:
    for line in f:
        line = line.strip()

        if not line or "=" not in line:
            continue

        name, code = line.split("=", 1)
        bindings[int(code)] = name.upper()

# Open every input device available to evdev.
devices = []

for path in glob.glob("/dev/input/event*"):
    try:
        devices.append(InputDevice(path))
    except PermissionError:
        pass

# Keep track of the current state of normal buttons.
buttons = {name: False for name in bindings.values()}

# HOME and WIFI behave differently from the other buttons on the 3DS.
# They generate a momentary event instead of maintaining a normal
# pressed state, so we give them a short visual activation instead.
temporary_active = {}

# Current Slide Pad movement.
joy_x = 0
joy_y = 0
last_joy_event = time.monotonic()

# Keep the most recent input events for the event log.
event_log = []


def active(name):
    # HOME and WIFI are momentary inputs, so check their timeout.
    if name in temporary_active:
        return time.monotonic() < temporary_active[name]

    # Normal buttons stay active until their release event.
    return buttons.get(name, False)


def put(stdscr, y, x, text, attr=0):
    # Prevent writes outside the 30x50 terminal.
    height, width = stdscr.getmaxyx()

    if y < 0 or y >= height or x < 0 or x >= width:
        return

    try:
        stdscr.addstr(y, x, text[:width - x], attr)
    except curses.error:
        pass


def draw_button(stdscr, y, x, name):
    text = f"[{name}]"
    attr = curses.A_REVERSE if active(name) else 0
    put(stdscr, y, x, text, attr)


def log_event(text):
    # Four events fit in rows 26-29 of the 30-row terminal.
    event_log.append(text)

    if len(event_log) > 4:
        event_log.pop(0)


def draw(stdscr):
    stdscr.erase()
    X_OFF = 2

    # Header
    put(stdscr, 1, X_OFF + 15, "INPUT TESTER")

    # Shoulder buttons
    draw_button(stdscr, 3, X_OFF + 2, "L")
    draw_button(stdscr, 3, X_OFF + 34, "R")

    # D-pad
    draw_button(stdscr, 6, X_OFF + 7, "UP")
    draw_button(stdscr, 8, X_OFF + 1, "LEFT")
    draw_button(stdscr, 8, X_OFF + 13, "RIGHT")
    draw_button(stdscr, 10, X_OFF + 7, "DOWN")

    # ABXY
    draw_button(stdscr, 6, X_OFF + 28, "X")
    draw_button(stdscr, 8, X_OFF + 23, "Y")
    draw_button(stdscr, 8, X_OFF + 33, "A")
    draw_button(stdscr, 10, X_OFF + 28, "B")

    # WIFI switch
    draw_button(stdscr, 8, X_OFF + 40, "WIFI")

    # System buttons
    draw_button(stdscr, 13, X_OFF + 2, "SELECT")
    draw_button(stdscr, 13, X_OFF + 16, "HOME")
    draw_button(stdscr, 13, X_OFF + 29, "START")

    # Slide Pad values
    put(stdscr, 16, X_OFF + 4, "SLIDEPAD")
    put(stdscr, 17, X_OFF + 1, f"X:{joy_x:+5d}  Y:{joy_y:+5d}")

    # Slide Pad visualizer
    put(stdscr, 19, X_OFF + 4, "+-----+")
    put(stdscr, 20, X_OFF + 4, "|     |")
    put(stdscr, 21, X_OFF + 4, "|     |")
    put(stdscr, 22, X_OFF + 4, "|     |")
    put(stdscr, 23, X_OFF + 4, "+-----+")

    # Convert the hardware X range into one of five positions.
    if joy_x <= -7:
        dot_x = 0
    elif joy_x <= -2:
        dot_x = 1
    elif joy_x >= 7:
        dot_x = 4
    elif joy_x >= 2:
        dot_x = 3
    else:
        dot_x = 2

    # Convert the hardware Y range into three positions.
    if joy_y <= -4:
        dot_y = 0
    elif joy_y >= 4:
        dot_y = 2
    else:
        dot_y = 1

    put(
        stdscr,
        20 + dot_y,
        X_OFF + 5 + dot_x,
        "O",
        curses.A_BOLD
    )

    # Event log
    put(stdscr, 25, 2, "EVENTS")

    for i, text in enumerate(event_log):
        put(stdscr, 26 + i, 2, text)

    stdscr.refresh()


def main(stdscr):
    global joy_x, joy_y, last_joy_event

    curses.curs_set(0)
    draw(stdscr)

    while True:
        # The short timeout lets us process timed events without
        # blocking indefinitely when no input is available.
        readable, _, _ = select.select(devices, [], [], 0.01)

        for device in readable:
            for event in device.read():

                if event.type == ecodes.EV_KEY:
                    button = bindings.get(event.code)

                    if button is None:
                        continue

                    # HOME and WIFI are different from normal buttons.
                    # On this hardware, they generate a momentary event
                    # rather than staying pressed until released.
                    if button in ("HOME", "WIFI"):
                        if event.value == 1:
                            temporary_active[button] = (
                                time.monotonic() + 0.12
                            )

                            log_event(
                                f"{button} code={event.code} pressed"
                            )

                            draw(stdscr)

                    else:
                        # Normal buttons use the same event handling
                        # as the basic input tester, that is buttontest.py.
                        if event.value == 1:
                            buttons[button] = True

                            log_event(
                                f"{button} code={event.code} pressed"
                            )

                            draw(stdscr)

                        elif event.value == 0:
                            buttons[button] = False

                            log_event(
                                f"{button} code={event.code} released"
                            )

                            draw(stdscr)

                elif event.type == ecodes.EV_REL:
                    if event.code == ecodes.REL_X:
                        joy_x = event.value
                        last_joy_event = time.monotonic()

                        log_event(
                            f"REL_X code={event.code} value={event.value:+d}"
                        )

                        draw(stdscr)

                    elif event.code == ecodes.REL_Y:
                        joy_y = event.value
                        last_joy_event = time.monotonic()

                        log_event(
                            f"REL_Y code={event.code} value={event.value:+d}"
                        )

                        draw(stdscr)

        now = time.monotonic()

        # REL_X/REL_Y are movement events, so there isn't necessarily
        # an event telling us that the Slide Pad has stopped.
        if now - last_joy_event > 0.05:
            if joy_x != 0 or joy_y != 0:
                joy_x = 0
                joy_y = 0
                draw(stdscr)

        # Remove temporary HOME/WIFI activations after their timeout.
        changed = False

        for name in list(temporary_active):
            if now >= temporary_active[name]:
                del temporary_active[name]
                changed = True

        if changed:
            draw(stdscr)


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass