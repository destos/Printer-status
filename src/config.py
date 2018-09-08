import ujson as json


class Config(dict):
    config_file = '/config.json'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.load()

    def load(self):
        try:
            with open(self.config_file) as f:
                config_data = json.loads(f.read())
        except (OSError, ValueError):
            print("Couldn't load %s", self.config_file)
            self.save()
        else:
            if config_data:
                self.update(config_data)
                print("Loaded config from %s", self.config_file)

    def save(self):
        try:
            with open(self.config_file, "w") as f:
                f.write(json.dumps(self))
        except OSError:
            print("Couldn't save %s", self.config_file)

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super().__delitem__(key)
        del self.__dict__[key]
