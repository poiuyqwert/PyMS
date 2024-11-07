
from __future__ import annotations

import tkinter as _Tk
import re as _re
from dataclasses import dataclass

from typing import Sequence

@dataclass
class Point:
	x: int
	y: int

	@staticmethod
	def of(point: tuple[int,int]) -> Point:
		return Point(point[0], point[1])

	def __add__(self, other) -> Point:
		if isinstance(other, Point):
			return Point(self.x + other.x, self.y + other.y)
		elif isinstance(other, Size):
			return Point(self.x + other.width, self.y + other.height)
		else:
			raise ValueError('Can only add `Point` or `Size`')

	def __sub__(self, other) -> Point:
		if isinstance(other, Point):
			return Point(self.x - other.x, self.y - other.y)
		elif isinstance(other, Size):
			return Point(self.x - other.width, self.y - other.height)
		else:
			raise ValueError('Can only subtract `Point` or `Size`')

	def __eq__(self, other) -> bool:
		if isinstance(other, tuple) and len(other) == 2:
			return other[0] == self.x and other[1] == self.y
		elif isinstance(other, Point):
			return other.x == self.x and other.y == self.y
		return False

@dataclass
class Size:
	width: int
	height: int

	@staticmethod
	def of(size: tuple[int,int]) -> Size:
		return Size(size[0], size[1])

	def __floordiv__(self, divisor) -> Size:
		if not isinstance(divisor, int):
			raise ValueError('Can only divide by int')
		return Size(self.width // divisor, self.height // divisor)

	@property
	def center(self) -> Point:
		return Point(self.width // 2, self.height // 2)

	def centered_in(self, other: Size) -> Point:
		return Point((other.width - self.width) // 2, (other.height - self.height) // 2)

	def __eq__(self, other) -> bool:
		if isinstance(other, Sequence) and len(other) == 2:
			return other[0] == self.width and other[1] == self.height
		elif isinstance(other, Size):
			return other.width == self.width and other.height == self.height
		return False

@dataclass
class Rect:
	pos: Point
	size: Size

	@property
	def center(self) -> Point:
		return Point(self.pos.x + self.size.width // 2, self.pos.y + self.size.height // 2)

	@property
	def max_x(self) -> int:
		return self.pos.x + self.size.width

	@property
	def max_y(self) -> int:
		return self.pos.y + self.size.height

	def clamp(self, *, size: Size, pos: Point = Point(0,0), min_size: Size | None = None, max_size: Size | None = None) -> None:
		if self.pos.x < pos.x:
			self.pos.x = pos.x
		if self.pos.y < pos.y:
			self.pos.y = pos.y
		if self.max_x > pos.x + size.width:
			self.size.width = size.width - (self.pos.x - pos.x)
		if self.max_y > pos.y + size.height:
			self.size.height = size.height - (self.pos.y - pos.y)
		if min_size:
			self.size.width = max(min_size.width, self.size.width)
		if max_size:
			self.size.width = min(max_size.width, self.size.width)
		if min_size:
			self.size.height = max(min_size.height, self.size.height)
		if max_size:
			self.size.height = min(max_size.height, self.size.height)

	def __eq__(self, other) -> bool:
		if isinstance(other, Sequence):
			if len(other) == 2:
				return self.pos == other[0] and self.size == other[1]
			elif len(other) == 4:
				return other[0] == self.pos.x and other[1] == self.pos.y and other[2] == self.size.width and other[3] == self.size.height
		elif isinstance(other, Rect):
			return other.pos == self.pos and other.size == self.size
		return False

@dataclass
class Geometry(Rect):
	maximized: bool = False

	@staticmethod
	def of(widget: _Tk.Misc | _Tk.Wm) -> Geometry:
		if isinstance(widget, _Tk.Wm):
			geometry = Geometry.parse(widget.geometry())
		else:
			geometry = Geometry.parse(widget.winfo_geometry())
		assert geometry is not None
		return geometry

	_RE = _re.compile(r'(\d+)x(\d+)\+(-?\d+)\+(-?\d+)(\^)?')
	@staticmethod
	def parse(text: str) -> (Geometry | None):
		match = Geometry._RE.match(text)
		if not match:
			return None
		size = Size(int(match.group(1)), int(match.group(2)))
		pos = Point(int(match.group(3)), int(match.group(4)))
		maximized = not not match.group(5)
		return Geometry(pos, size, maximized)

	@property
	def text(self) -> str:
		return f'{self.size.width}x{self.size.height}+{self.pos.x}+{self.pos.y}{"^" if self.maximized else ""}'

	def __str__(self) -> str:
		return self.text
	
	def adjust_center_at(self, pos: Point = Point(0,0)) -> GeometryAdjust:
		adjust_pos = pos - self.size // 2
		return GeometryAdjust(pos=adjust_pos)

	def adjust_center_in(self, size: Size, pos: Point = Point(0,0)) -> GeometryAdjust:
		adjust_pos = Point(size.width // 2 - self.size.width // 2, size.height // 2 - self.size.height // 2)
		adjust_pos += pos
		return GeometryAdjust(pos=adjust_pos)

@dataclass
class GeometryAdjust:
	pos: Point | None = None
	size: Size | None = None
	maximized: bool = False

	_RE = _re.compile(r'(?:(\d+)x(\d+))?\+(-?\d+)\+(-?\d+)(\^)?')
	@staticmethod
	def parse(text: str) -> (GeometryAdjust | None):
		match = GeometryAdjust._RE.match(text)
		if not match:
			return None
		if match.group(1):
			size = Size(int(match.group(1)), int(match.group(2)))
		else:
			size = None
		pos = Point(int(match.group(3)), int(match.group(4)))
		maximized = not not match.group(5)
		return GeometryAdjust(pos, size, maximized)

	@property
	def is_empty(self) -> bool:
		return self.pos is None and self.size is None

	@property
	def text(self) -> str:
		if self.is_empty:
			raise ValueError('Must have `pos` or `size`')
		text = ''
		if self.size is not None:
			text += f'{self.size.width}x{self.size.height}'
		if self.pos is not None:
			text += f'+{self.pos.x}+{self.pos.y}'
		if self.maximized:
			text += '^'
		return text

	def __str__(self) -> str:
		return self.text

	@property
	def geometry(self) -> (Geometry | None):
		if self.pos is None or self.size is None:
			return None
		return Geometry(pos=self.pos, size=self.size, maximized=self.maximized)

ScrollRegion = tuple[int, int, int, int]

RE_SCROLLREGION = _re.compile(r'(\d+) (\d+) (\d+) (\d+)')
def parse_scrollregion(scrollregion: str, default: ScrollRegion = (0, 0, 0, 0)) -> ScrollRegion:
	match = RE_SCROLLREGION.match(scrollregion)
	if not match:
		return default
	return (int(match.group(1)), int(match.group(2)), int(match.group(3)), int(match.group(4)))

Resizable = tuple[bool, bool]

RE_RESIZABLE = _re.compile(r'([01]) ([01])')
def parse_resizable(resizable: tuple[int, int] | str, default: Resizable = (False, False)) -> Resizable:
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
def repr_event(event: _Tk.Event) -> str:
	result = '<Event'
	for attr in EVENT_ATTRS:
		if hasattr(event, attr):
			value = getattr(event, attr)
			result += '\n\t%s = %s' % (attr, repr(value))
			if attr == 'widget':
				result += ' (%s)' % value
	return result + '\n>'

def remove_bind(widget: _Tk.Misc, sequence: str, funcid: str):
	"""Unbind for this WIDGET for event SEQUENCE  the
	function identified with FUNCID."""
	bound = ''
	if funcid:
		widget.deletecommand(funcid)
		funcs = widget.tk.call('bind', getattr(widget, '_w'), sequence, None).split('\n')
		bound = '\n'.join([f for f in funcs if not f.startswith('if {{"[{0}'.format(funcid))])
	widget.tk.call('bind', getattr(widget, '_w'), sequence, bound)
