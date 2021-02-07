import os
import sys

#Setting QUIET to True will stop almost all console messages
QUIET = False
DEBUG = False
VERSION = sys.version_info[0]
IN_AXIS = "AXIS_PROGRESS_BAR" in os.environ

if VERSION == 3:
    from tkinter import *
    import tkinter.messagebox
else:
    from Tkinter import *
    import tkMessageBox


###############################################################################
#             Function for outputting messages to different locations         #
#            depending on what options are enabled                            #
###############################################################################
def fmessage(text, newline=True):
    global IN_AXIS, QUIET
    if (not IN_AXIS and not QUIET):
        if newline:
            try:
                sys.stdout.write(text)
                sys.stdout.write("\n")
            except:
                pass
        else:
            try:
                sys.stdout.write(text)
            except:
                pass


def message_box(title, message):
    if VERSION == 3:
        tkinter.messagebox.showinfo(title, message)
    else:
        tkMessageBox.showinfo(title, message)
        pass


def message_ask_ok_cancel(title, message):
    if VERSION == 3:
        result = tkinter.messagebox.askokcancel(title, message)
    else:
        result = tkMessageBox.askokcancel(title, message)
    return result


###############################################################################
#                         Debug Message Box                                   #
###############################################################################
def debug_message(message):
    global DEBUG
    title = "Debug Message"
    if DEBUG:
        if VERSION == 3:
            tkinter.messagebox.showinfo(title, message)
        else:
            tkMessageBox.showinfo(title, message)
            pass


class Message():
    def __init__(self, quiet=False, debug=False):
        self.quiet = quiet
        self.debug = debug

    def debug_message(self, message):
        if self.debug:
            title = "Debug Message"
            if VERSION == 3:
                tkinter.messagebox.showinfo(title, message)
            else:
                tkMessageBox.showinfo(title, message)

    def message_ask_ok_cancel(self, title, message):
        if VERSION == 3:
            result = tkinter.messagebox.askokcancel(title, message)
        else:
            result = tkMessageBox.askokcancel(title, message)
        return result

    def message_box(self, title, message):
        if VERSION == 3:
            tkinter.messagebox.showinfo(title, message)
        else:
            tkMessageBox.showinfo(title, message)

    def fmessage(self, text, newline=True):
        if not self.quiet:
            if newline:
                try:
                    sys.stdout.write(text)
                    sys.stdout.write("\n")
                except:
                    pass
            else:
                try:
                    sys.stdout.write(text)
                except:
                    pass
