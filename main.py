#!/usr/bin/env python

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk

from src.bot import *

root = tk.Tk()
client = RoboJiub(root)

root.protocol('WM_DELETE_WINDOW', client.end_application)
root.mainloop()
