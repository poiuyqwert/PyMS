
import tkinter as _Tk
import re as _re

from typing import Tuple

Geometry = Tuple[int,int, int,int, bool]

RE_GEOMETRY = _re.compile(r'(?:(\d+)x(\d+))?\+(-?\d+)\+(-?\d+)(\^)?')
def parse_geometry(geometry, default=(200,200,200,200,False)): # type: (str, Geometry) -> Geometry
	match = RE_GEOMETRY.match(geometry)
	if not match:
		return default
	return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)), True if match.group(5) else False)

def build_geometry(pos=None, size=None, maximized=False): # type: (tuple[int, int] | None, tuple[int, int] | None, bool) -> str
	if pos is None and size is None:
		raise Exception('At least one of `pos` or `size` must not be `None`')
	geometry = ''
	if size is not None:
		geometry += '%dx%d' % size
	if pos is not None:
		geometry += '+%d+%d' % pos
	if maximized:
		geometry += '^'
	return geometry

ScrollRegion = Tuple[int, int, int, int]

RE_SCROLLREGION = _re.compile(r'(\d+) (\d+) (\d+) (\d+)')
def parse_scrollregion(scrollregion, default=(0, 0, 0, 0)): # type: (str, ScrollRegion) -> ScrollRegion
	match = RE_SCROLLREGION.match(scrollregion)
	if not match:
		return default
	return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))

Resizable = Tuple[bool, bool]

RE_RESIZABLE = _re.compile(r'([01]) ([01])')
def parse_resizable(resizable, default=(False, False)): # type: (tuple[int, int] | str, Resizable) -> Resizable
	if isinstance(resizable, tuple):
		return (bool(resizable[0]), bool(resizable[1]))
	match = RE_RESIZABLE.match(resizable)
	if not match:
		return default
	return (bool(match.group(1)), bool(match.group(2)))

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
def repr_event(event): # type: (_Tk.Event) -> str
	result = '<Event'
	for attr in EVENT_ATTRS:
		if hasattr(event, attr):
			value = getattr(event, attr)
			result += '\n\t%s = %s' % (attr, repr(value))
			if attr == 'widget':
				result += ' (%s)' % value
	return result + '\n>'
