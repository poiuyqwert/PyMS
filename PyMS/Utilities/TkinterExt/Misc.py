
try:
	import Tkinter as Tk
except:
	import tkinter as Tk

def _clipboard_set(obj, text):
	obj.clipboard_clear()
	obj.clipboard_append(text)
Tk.Misc.clipboard_set = _clipboard_set
