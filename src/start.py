import machine
import math
import ubinascii

from config import Config
from mqtt import MQTTClient
from progress import TrackerHandler, ProgressTracker
from connection import connect


client_id = b'esp8266_' + ubinascii.hexlify(machine.unique_id())


CONFIG_DEFAULTS = {
    'network': '',
    'network_password': '',
    'broker': '',
    'port': 1883,
    'client_id': client_id,
    'octoprint_topic': 'octoprint/',
    'CONNECTED': b'devices/'+client_id+'/connected',
    'DISCONNECTED': b'devices/'+client_id+'/disconnected',
}

global prev_percent

def start():
    CONFIG = Config(CONFIG_DEFAULTS)

    connect(CONFIG.network, CONFIG.network_password)

    handler = TrackerHandler(CONFIG, printer='pat-prusa')
    progress_tracker = ProgressTracker()
    handler.add_tracker(progress_tracker)

    import neopixel
    PX_COUNT = 60

    np = neopixel.NeoPixel(machine.Pin(5), PX_COUNT, bpp=4)

    green = (0, 100, 0, 10)
    prev_percent = 0

    def update_pixels():
        percent = progress_tracker.progress
        if prev_percent == percent:
            return
        prev_percent = percent
        pixels = math.floor((percent * PX_COUNT) / 100)
        print('pixels on', pixels)

        for p in range(PX_COUNT):
            if p < pixels:
                np[p] = green
            else:
                np[p] = (0, 0, 0, 0)

        np.write()

    # update every second
    timer = machine.Timer(-1)
    timer.init(period=1000, mode=machine.Timer.PERIODIC, callback=lambda t: update_pixels())
