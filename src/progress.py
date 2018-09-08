import machine
import ujson as json

from mqtt import MQTTClient


class Tracker:
    def handle_msg(self, topic, handler, msg):
        msg = json.loads(msg)
        return getattr(self, handler)(msg)

    def get_subscriptions(self):
        return self.topic_handlers.keys()


class ProgressTracker(Tracker):
    progress = 0

    topic_handlers = {
        'progress/printing': 'parse_progress_message',
        'event/PrinterStateChanged': 'parse_status_change',
    }

    def parse_progress_message(self, msg):
        # TODO: track and compare timestamps.
        self.progress = msg['progress']

    def parse_status_change(self, msg):
        print("state: %s", msg['state_string'])


class TrackerHandler:

    def __init__(self, config, printer):
        self.printer= printer
        self.config = config
        self.timers = []
        self.trackers = []
        self.all_topics = []
        self.client = MQTTClient(
            self.config.client_id,
            self.config.broker,
            self.config.port,
        )
        # Subscribed messages will be delivered to this callback
        self.client.set_callback(self.subscription_callback)
        self.client.set_last_will(self.config.DISCONNECTED, b'disconnected')
        self.connect()
        # keep alive
        self.setup_timer(period=500, callback=self.keep_alive)

    def connect(self):
        self.client.connect()
        self.client.publish(self.config.CONNECTED, bytes('connected', 'utf-8'))

    def keep_alive(self):
        self.client.check_msg()

    def setup_timer(self, period=1000, mode=machine.Timer.PERIODIC, callback=None):
        timer = machine.Timer(-1)
        self.timers.append(timer)
        timer.init(period=period, mode=mode, callback=lambda t: callback())

    def subscription_callback(self, rec_topic, msg):
        # basic main subscription
        rec_topic = rec_topic.decode()
        for topic_info in self.all_topics:
            topic = topic_info.get('topic', None)
            tracker = topic_info.get('tracker', None)
            if self.topic_matches(rec_topic, topic):
                # call handler with message
                handler = topic_info.get('handler')
                # print("Calling %s handler on %s", handler, tracker)
                tracker.handle_msg(rec_topic, handler, msg)

    def topic_matches(self, rec_topic, topic):
        return rec_topic == topic

    def get_topic_base(self):
        return '{}{}'.format(self.config.octoprint_topic, self.printer)

    def add_tracker(self, tracker):
        self.trackers.append(tracker)
        # subs = tracker.get_subscriptions()
        base = self.get_topic_base()

        for topic, handler in tracker.topic_handlers.items():
            full_topic = '{}/{}'.format(base, topic)
            self.all_topics.append({
                'topic': full_topic,
                'handler': handler,
                'tracker': tracker,
            })
            print("Subscribing to topic: ", full_topic)
            self.client.subscribe(full_topic)
