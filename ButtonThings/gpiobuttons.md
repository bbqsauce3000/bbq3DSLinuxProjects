# 3DSlinux Buttons

####
####
## hid\_buttons



**Face buttons:**

A = BTN\_SOUTH

B = BTN\_EAST

X = BTN\_NORTH

Y = BTN\_WEST



**Shoulder buttons:**

L = BTN\_TL

R = BTN\_TR



**D-pad:**

Up = KEY\_UP

Down = KEY\_DOWN

Left = KEY\_LEFT

Right = KEY\_RIGHT



**Start/Select:**

Select = BTN\_SELECT

Start = BTN\_START



## mcu_buttons



**Menu/Special Buttons:**

Home = KEY\_HOME

WIFI Switch = KEY\_WIMAX (*Physical wireless switch on the side of the system)*

Power Button = KEY\_POWER (*Must hold for approx. one second)*



#### Notes:



REL\_X and REL\_Y (*from Nintendo 3DS touch HID, interestingly enough*) are interpreted by X11 (*tested on jwm),* as mouse movement, allowing the 3DS Slide Pad to control the mouse pointer.



REL\_X and REL\_Y seem to have -10 to 10 as their possible values, as shown below:

![Nintendo 3DS](3dsslidepadxyvalues.png)

