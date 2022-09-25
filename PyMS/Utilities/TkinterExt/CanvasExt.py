
from ..utils import is_mac

try:
	import Tkinter as Tk
except:
	import tkinter as Tk

class Canvas(Tk.Canvas):
	class Item(object):
		def __init__(self, canvas, item_id):
			self.canvas = canvas # type: Tk.Canvas
			self.item_id = item_id

		def cget(self, option):
			return self.canvas.itemcget(self.item_id, option)
		def __getitem__(self, option):
			return self.cget(option)

		def config(self, **kwargs):
			self.canvas.itemconfig(self.item_id, **kwargs)
		def __setitem__(self, option, value):
			self.config(**{option: value})

		def coords(self, x,y, x2=None,y2=None):
			x,y = self.canvas.coordinate_adjust(x, y)
			if x2 != None and y2 != None:
				x2,y2 = self.canvas.coordinate_adjust(x2, y2)
			self.canvas.coords(self.item_id, x,y, x2,y2)

		def delete(self):
			self.canvas.delete(self.item_id)

		def tag_raise(self):
			self.canvas.tag_raise(self.item_id)

		def tag_lower(self):
			self.canvas.tag_lower(self.item_id)

		def __str__(self):
			return str(self.item_id)

		def __eq__(self, other):
			if isinstance(other, Canvas.Item):
				return other.item_id == self.item_id
			return other == self.item_id

		def __hash__(self):
			return self.item_id

	@staticmethod
	def coordinate_adjust_none(x, y):
		return (x, y)

	@staticmethod
	# Adjust the coordinates to work for Mac an Windows
	def coordinate_adjust_os(x, y):
		return (x + (1 if is_mac() else 0), y + (1 if is_mac() else 0))

	def __init__(self, master=None, cnf={}, coordinate_adjust=None, **kw):
		self.coordinate_adjust = coordinate_adjust or Canvas.coordinate_adjust_none
		Tk.Canvas.__init__(self, master, cnf, **kw)

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

	def create_arc(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_arc(self, x1,y1, x2,y2, *args, **kwargs))

	def create_bitmap(self, x,y, bitmap=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['bitmap'] = bitmap
		return Canvas.Item(self, Tk.Canvas.create_bitmap(self, x,y, *args, **kwargs))

	def create_image(self, x,y, image=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['image'] = image
		return Canvas.Item(self, Tk.Canvas.create_image(self, x,y, *args, **kwargs))

	def create_line(self, *points, **kwargs):
		points = tuple(self.coordinate_adjust(points[n],points[n+1]) for n in range(0,len(points),2))
		return Canvas.Item(self, Tk.Canvas.create_line(self, *points, **kwargs))

	def create_oval(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_oval(self, x1,y1, x2,y2, *args, **kwargs))

	def create_polygon(self, *points, **kwargs):
		points = tuple(self.coordinate_adjust(points[n],points[n+1]) for n in range(0,len(points),2))
		return Canvas.Item(self, Tk.Canvas.create_polygon(self, *points, **kwargs))

	def create_rectangle(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_rectangle(self, x1,y1, x2,y2, *args, **kwargs))

	def create_text(self, x,y, text=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['text'] = text
		return Canvas.Item(self, Tk.Canvas.create_text(self, x,y, *args, **kwargs))

	def create_window(self, x,y, window=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['window'] = window
		return Canvas.Item(self, Tk.Canvas.create_window(self, x,y, *args, **kwargs))

	def coords(self, item_id, x,y, x2=None,y2=None):
		x,y = self.coordinate_adjust(x, y)
		if x2 != None and y2 != None:
			x2,y2 = self.coordinate_adjust(x2, y2)
		Tk.Canvas.coords(self, item_id, x,y, x2,y2)
