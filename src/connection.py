import time, machine, network


def connect(ssid, pw):
    sta_if = network.WLAN(network.STA_IF)
    ap_if = network.WLAN(network.AP_IF)
    sta_if.active(True)

    # attempt to show connection indicator
    led = machine.Pin(0, machine.Pin.OUT)
    led.off()

    print('connecting to network')
    sta_if.connect(ssid, pw)
    while not sta_if.isconnected():
        led.on()
        time.sleep(0.1)
        led.off()
        time.sleep(0.1)

    print('network config:', sta_if.ifconfig())
    ap_if.active(False)

    led.on()
