# 3DSLinux LEDs
**Power LED States:**
*(Controlled via register 0x29)*

Blue (*Powered On*) = 
`sudo i2ctransfer -y -f 1 w2@0x25 0x29 0x01`
OR
`sudo i2ctransfer -y -f 1 w2@0x25 0x29 0x05`

Dim Blue Blinking = `sudo i2ctransfer -y -f 1 w2@0x25 0x29 0x02`

Off = `sudo i2ctransfer -y -f 1 w2@0x25 0x29 0x03`

###

**Wireless LED:**
*(Controlled via register 0x28)*

On = `sudo i2ctransfer -y -f 1 w2@0x25 0x28 0x0F`
Off = `sudo i2ctransfer -y -f 1 w2@0x25 0x28 0x00`


#### Notes:

The standard Linux `/sys/class/leds/10144000.i2c:mcu@25:mcu-led@2d/brightness` seems to not do anything when using `tee` to interact... Probably doesn't work.


SMBus also doesn't seem to work, all commands must use raw I2C transfer packets (`i2ctransfer`) paired with the force (`-f`) flag.

Animated LEDs need to be zeroed out before being replaced with another color.
This can be done by sending a fully blank payload, filled with `0x00`.

