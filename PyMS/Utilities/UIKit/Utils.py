
try:
	import tkinter as _Tk
except:
	import tkinter as _Tk

import re as _re

RE_GEOMETRY = _re.compile(r'(?:(\d+)x(\d+))?\+(-?\d+)\+(-?\d+)(\^)?')
def parse_geometry(geometry): # type: (str) -> tuple[int,int, int,int, bool]
	match = RE_GEOMETRY.match(geometry)
	return tuple(None if v is None else int(v) for v in match.groups()[:-1]) + (True if match.group(5) else False,)

def parse_scrollregion(scrollregion): # type: (str) -> tuple[int, int]
	return tuple(int(v) for v in scrollregion.split(' '))

def parse_resizable(resizable): # type: (tuple[int, int] | str) -> tuple[bool, bool]
	if isinstance(resizable, str):
		resizable = resizable.split(' ')
	return tuple(bool(v) for v in resizable)

EVENT_ATTRS = [
	'serial',
	'num',
	'focus',
	'height',
	'width',
	'keycode',
	'state',
	'time',
	'x',
	'y',
	'x_root',
	'y_root',
	'char',
	'send_event',
	'keysym',
	'keysym_num',
	'type',
	'widget',
	'delta',
]
def repr_event(event):
	result = '<Event'
	for attr in EVENT_ATTRS:
		if hasattr(event, attr):
			value = getattr(event, attr)
			result += '\n\t%s = %s' % (attr, repr(value))
			if attr == 'widget':
				result += ' (%s)' % value
	return result + '\n>'
