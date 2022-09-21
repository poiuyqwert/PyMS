
try:
	import Tkinter as Tk
except:
	import tkinter as Tk

import re as _re

def _clipboard_set(obj, text):
	obj.clipboard_clear()
	obj.clipboard_append(text)
Tk.Misc.clipboard_set = _clipboard_set

RE_GEOMETRY = _re.compile(r'(?:(\d+)x(\d+))?\+(-?\d+)\+(-?\d+)(\^)?')
def parse_geometry(geometry):
	match = RE_GEOMETRY.match(geometry)
	return tuple(None if v == None else int(v) for v in match.groups()[:-1]) + (True if match.group(5) else False,)

def parse_scrollregion(scrollregion):
	return tuple(int(v) for v in scrollregion.split(' '))

def parse_resizable(resizable): # type: (tuple[int, int] | str) -> tuple[bool, bool]
	if isinstance(resizable, str):
		resizable = resizable.split(' ')
	return tuple(bool(v) for v in resizable)

def apply_cursor(widget, cursors):
	for cursor in reversed(cursors):
		try:
			widget.config(cursor=cursor)
			return cursor
		except:
			pass
