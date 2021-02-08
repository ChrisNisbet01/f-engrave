from config import BaseVar
import sys

VERSION = sys.version_info[0]

if VERSION == 3:
    from tkinter import StringVar
else:
    from Tkinter import StringVar


class TkStringVar(BaseVar):
    def __init__(self, initial_value = ""):
        BaseVar.__init__(self)
        self.tk_string_var = StringVar()
        self.tk_string_var.set(initial_value)

    @property
    def value(self):
        return self.tk_string_var.get()

    @value.setter
    def value(self, value):
        self.tk_string_var.set(str(value))

    @property
    def tkinter(self):
        return self.tk_string_var
