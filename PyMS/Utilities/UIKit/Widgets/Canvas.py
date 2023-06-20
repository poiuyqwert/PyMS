
from __future__ import annotations

from ...utils import is_mac
from .. import Theme
from .Extensions import Extensions

import tkinter as _Tk

from typing import Any, Callable

CoordinateAdjuster = Callable[[int, int], tuple[int, int]]

class Canvas(_Tk.Canvas, Extensions):
	class Item(object):
		def __init__(self, canvas: Canvas, item_id: int):
			self.canvas = canvas
			self.item_id = item_id

		def cget(self, option: str) -> Any:
			return self.canvas.itemcget(self.item_id, option)
		def __getitem__(self, option: str) -> Any:
			return self.cget(option)

		def config(self, **kwargs) -> None:
			self.canvas.itemconfig(self.item_id, **kwargs)
		def __setitem__(self, option: str, value: Any) -> None:
			self.config(**{option: value})

		def coords(self, x: int, y: int, x2: int | None = None, y2: int | None = None):
			x,y = self.canvas.coordinate_adjust(x, y)
			if x2 is not None and y2 is not None:
				x2,y2 = self.canvas.coordinate_adjust(x2, y2)
			self.canvas.coords(self.item_id, x,y, x2,y2)

		def delete(self) -> None:
			self.canvas.delete(self.item_id)

		def tag_raise(self) -> None:
			self.canvas.tag_raise(self.item_id)

		def tag_lower(self) -> None:
			self.canvas.tag_lower(self.item_id)

		def __str__(self) -> str:
			return str(self.item_id)

		def __eq__(self, other: Any) -> bool:
			if isinstance(other, Canvas.Item):
				return other.item_id == self.item_id
			return other == self.item_id

		def __hash__(self) -> int:
			return self.item_id

	@staticmethod
	def coordinate_adjust_none(x: int, y: int) -> tuple[int, int]:
		return (x, y)

	@staticmethod
	# Adjust the coordinates to work for Mac an Windows
	def coordinate_adjust_os(x: int, y: int) -> tuple[int, int]:
		return (x + (1 if is_mac() else 0), y + (1 if is_mac() else 0))

	def __init__(self, master: _Tk.Misc | None = None, cnf: dict[str, Any] = {}, coordinate_adjust: CoordinateAdjuster | None = None, **kw):
		self.coordinate_adjust: CoordinateAdjuster = coordinate_adjust or Canvas.coordinate_adjust_none
		kw, self.theme_tag = Theme.get_tag(kw)
		_Tk.Canvas.__init__(self, master, cnf, **kw)
		Theme.apply_theme(self)

	# TODO: Apply coordinate adjust
	# def addtag_closest(self, newtag, x, y, halo=None, start=None):
    # def addtag_enclosed(self, newtag, x1, y1, x2, y2):
    # def addtag_overlapping(self, newtag, x1, y1, x2, y2):
	# def bbox(self, *args):
	# def canvasx(self, screenx, gridspacing=None):
    # def canvasy(self, screeny, gridspacing=None):
	# def coords(self, *args):
	# def find_closest(self, x, y, halo=None, start=None):
    # def find_enclosed(self, x1, y1, x2, y2):
    # def find_overlapping(self, x1, y1, x2, y2):
	# def scan_mark(self, x, y):
    # def scan_dragto(self, x, y, gain=10):

	def create_arc(self, x1: int, y1: int, x2: int, y2: int, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, _Tk.Canvas.create_arc(self, x1,y1, x2,y2, *args, **kwargs))

	def create_bitmap(self, x: int, y: int, bitmap: _Tk.BitmapImage | None = None, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x,y = self.coordinate_adjust(x,y)
		kwargs['bitmap'] = bitmap
		return Canvas.Item(self, _Tk.Canvas.create_bitmap(self, x,y, *args, **kwargs))

	def create_image(self, x: int, y: int, image: _Tk.Image | None = None, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x,y = self.coordinate_adjust(x,y)
		kwargs['image'] = image
		return Canvas.Item(self, _Tk.Canvas.create_image(self, x,y, *args, **kwargs))

	def create_line(self, *points: tuple[int,int], **kwargs) -> Canvas.Item: # type: ignore[override]
		points = tuple(self.coordinate_adjust(point[0],point[1]) for point in points)
		coords = sum(points, ())
		return Canvas.Item(self, _Tk.Canvas.create_line(self, *coords, **kwargs))

	def create_oval(self, x1: int, y1: int, x2: int, y2: int, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, _Tk.Canvas.create_oval(self, x1,y1, x2,y2, *args, **kwargs))

	def create_polygon(self, *points: tuple[int,int], **kwargs) -> Canvas.Item: # type: ignore[override]
		points = tuple(self.coordinate_adjust(point[0],point[1]) for point in points)
		coords = sum(points, ())
		return Canvas.Item(self, _Tk.Canvas.create_polygon(self, *coords, **kwargs))

	def create_rectangle(self, x1: int, y1: int, x2: int, y2: int, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, _Tk.Canvas.create_rectangle(self, x1,y1, x2,y2, *args, **kwargs))

	def create_text(self, x: int, y: int, text: str | None = None, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x,y = self.coordinate_adjust(x,y)
		kwargs['text'] = text
		return Canvas.Item(self, _Tk.Canvas.create_text(self, x,y, *args, **kwargs))

	def create_window(self, x: int, y: int, window: _Tk.Widget | None = None, *args, **kwargs) -> Canvas.Item: # type: ignore[override]
		x,y = self.coordinate_adjust(x,y)
		kwargs['window'] = window
		return Canvas.Item(self, _Tk.Canvas.create_window(self, x,y, *args, **kwargs))

	def coords(self, item_id: int, x: int, y: int, x2: int | None = None, y2: int | None = None) -> None: # type: ignore[override]
		x,y = self.coordinate_adjust(x, y)
		if x2 is not None and y2 is not None:
			x2,y2 = self.coordinate_adjust(x2, y2)
			_Tk.Canvas.coords(self, item_id, x,y, x2,y2)
		else:
			_Tk.Canvas.coords(self, item_id, x,y)
