class BaseVar():
    def __init__(self):
        pass

    @property
    def value(self):
        raise NotImplementedError

    @value.setter
    def value(self, value):
        raise NotImplementedError


class Config(dict):
    def __init__(self):
        dict.__init__(self)
