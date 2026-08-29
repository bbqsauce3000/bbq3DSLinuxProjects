#!/usr/bin/env python3
import curses
import glob
import select
import time
import random
from evdev import InputDevice, ecodes

# A minimalistic clone of the 2004 game, Moon-Buggy.
#
# The buggy drives across the moon and jumps over craters.
#
# Controls:
# A = jump
# WIFI Switch = jump
# Y = restart after death
# B = exit after death

# Load the Linux input codes from buttonbindings.txt.
bindings = {}

with open("buttonbindings.txt") as f:
    for line in f:
        line = line.strip()

        if not line or "=" not in line:
            continue

        name, code = line.split("=", 1)
        bindings[int(code)] = name.upper()

# Open the available Linux input devices.
devices = []

for path in glob.glob("/dev/input/event*"):
    try:
        devices.append(InputDevice(path))
    except PermissionError:
        pass

# Screen layout.
WIDTH = 50
HEIGHT = 30
GROUND_Y = 25
BUGGY_X = 8

# Jump physics.
buggy_y = GROUND_Y - 1
velocity_y = 0

GRAVITY = 1
JUMP_VELOCITY = -5

# Game state.
score = 0
lives = 3
game_over = False

# Each crater is stored as:
# [x position, width, already_scored]
craters = []

# Counts down in physics frames.
crater_timer = 10


def reset_game():
    global buggy_y, velocity_y
    global score, lives, game_over
    global craters, crater_timer

    buggy_y = GROUND_Y - 1
    velocity_y = 0

    score = 0
    lives = 3
    game_over = False

    craters = []
    crater_timer = 10


def lose_life():
    global buggy_y, velocity_y
    global lives, game_over
    global craters, crater_timer

    lives -= 1

    if lives <= 0:
        game_over = True
        return

    # Put the buggy back on the moon.
    buggy_y = GROUND_Y - 1
    velocity_y = 0

    # Clear the current craters so the player gets a
    # fair restart after losing a life.
    craters = []
    crater_timer = 20


def jump():
    global velocity_y

    # Only allow jumping while the buggy is on the ground.
    if buggy_y == GROUND_Y - 1:
        velocity_y = JUMP_VELOCITY


def spawn_crater():
    width = random.randint(3, 6)
    craters.append([WIDTH, width, False])


def crater_at(x):
    for crater in craters:
        crater_x = int(crater[0])
        crater_width = crater[1]

        if crater_x <= x < crater_x + crater_width:
            return True

    return False


def draw(stdscr):
    stdscr.erase()

    stdscr.addstr(1, 2, f"SCORE: {score}")
    stdscr.addstr(1, 25, f"LIVES: {lives}")

    if game_over:
        stdscr.addstr(12, 11, "Game over man, it's game over!")
        stdscr.addstr(14, 14, "Y = RESTART")
        stdscr.addstr(15, 14, "B = EXIT")
        stdscr.refresh()
        return

    # Draw the moon surface.
    for x in range(WIDTH):
        if not crater_at(x):
            stdscr.addch(GROUND_Y, x, "_")

    # Draw crater edges and bottoms.
    for crater in craters:
        x = int(crater[0])
        width = crater[1]

        left = x
        right = x + width - 1

        if 0 <= left < WIDTH:
            stdscr.addch(GROUND_Y, left, "\\")

        if 0 <= right < WIDTH:
            stdscr.addch(GROUND_Y, right, "/")

        for crater_x in range(left + 1, right):
            if 0 <= crater_x < WIDTH:
                stdscr.addch(GROUND_Y + 1, crater_x, "_")

    # Draw the buggy.
    y = int(buggy_y)

    if 0 <= y < HEIGHT:
        stdscr.addch(y, BUGGY_X, "o")

    stdscr.refresh()


def main(stdscr):
    global buggy_y, velocity_y
    global score, lives, game_over
    global craters, crater_timer

    curses.curs_set(0)
    stdscr.nodelay(True)

    reset_game()

    # Run the game at a fixed 20 FPS.
    frame_time = 1 / 20

    while True:
        frame_start = time.monotonic()

        # Read every input event currently waiting.
        readable, _, _ = select.select(devices, [], [], 0)

        for device in readable:
            for event in device.read():
                if event.type != ecodes.EV_KEY:
                    continue

                # Only react to actual key presses.
                if event.value != 1:
                    continue

                button = bindings.get(event.code)

                if button is None:
                    continue

                if not game_over:
                    if button == "A" or button == "WIFI":
                        jump()
                else:
                    if button == "Y":
                        reset_game()
                    elif button == "B":
                        return

        if not game_over:
            # Move craters first so collision uses their new positions.
            for crater in craters:
                crater[0] -= 1

            # Remove craters only after their entire width
            # has left the screen.
            craters = [
                crater
                for crater in craters
                if crater[0] + crater[1] >= 0
            ]

            # Apply gravity.
            velocity_y += GRAVITY
            buggy_y += velocity_y

            # Check whether the buggy's wheel position is inside
            # the dangerous middle of a crater.
            wheel_x = BUGGY_X
            over_crater = False

            for crater in craters:
                crater_left = int(crater[0])
                crater_right = crater_left + crater[1] - 1

                # Leave one character of forgiveness on each edge.
                if crater_left + 1 <= wheel_x <= crater_right - 1:
                    over_crater = True
                    break

            # Handle landing.
            if buggy_y >= GROUND_Y - 1:
                if over_crater:
                    lose_life()
                else:
                    buggy_y = GROUND_Y - 1
                    velocity_y = 0

            # Spawn a new crater.
            crater_timer -= 1

            if crater_timer <= 0:
                spawn_crater()
                crater_timer = random.randint(14, 24)

            # Score craters after they pass the buggy.
            for crater in craters:
                if crater[0] + crater[1] < BUGGY_X and not crater[2]:
                    score += 1
                    crater[2] = True

        draw(stdscr)

        # Maintain the fixed 20 FPS update rate.
        elapsed = time.monotonic() - frame_start

        if elapsed < frame_time:
            time.sleep(frame_time - elapsed)


try:
    curses.wrapper(main)
except KeyboardInterrupt:
    pass