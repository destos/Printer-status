# This file is executed on every boot (including wake-boot from deepsleep)

#disable debug
import esp
esp.osdebug(None)

# duplicate terminal
# import uos, machine
# uos.dupterm(machine.UART(0, 115200), 1)

import gc
gc.enable()

# import webrepl
# webrepl.start()
