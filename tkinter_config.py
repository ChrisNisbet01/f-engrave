from config import BaseVar
import sys

VERSION = sys.version_info[0]

if VERSION == 3:
    from tkinter import StringVar, BooleanVar
else:
    from Tkinter import StringVar, BooleanVar


class FeStringVar(BaseVar):
    def __init__(self, initial_value=""):
        BaseVar.__init__(self)
        self._tkinter = StringVar()
        self.value = initial_value

    @property
    def value(self):
        return self._tkinter.get()

    @value.setter
    def value(self, value):
        if not value:
            value = ""
        self._tkinter.set(value)

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    @property
    def TK(self):
        return self._tkinter


# Note that some f-engrave code assumes that booleans return 0 or 1,
# so retain this same functionality for backwards compatibility.
class FeBooleanVar(BaseVar):
    def __init__(self, initial_value=False):
        BaseVar.__init__(self)
        self._tkinter = BooleanVar()
        self.value = initial_value

    @property
    def value(self):
        return self._tkinter.get()

    @value.setter
    def value(self, value):
        if not value:
            value = 0
        self._tkinter.set(int(value))

    def set(self, value):
        self.value = value

    def get(self):
        return self.value

    @property
    def TK(self):
        return self._tkinter
