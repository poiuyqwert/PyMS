
from .Delegates import MiniEditorDelegate

from ..Utilities import Assets
from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog

from enum import Enum

from typing import Callable

class Click(Enum):
	left = 0
	right = 1

	def config_key(self): # type () -> str
		if self == Click.left:
			return 'fg'
		return 'bg'

class MiniEditor(PyMSDialog):
	def __init__(self, parent, id, delegate, colors={Click.left:0, Click.right:0}): # type: (Misc, int, MiniEditorDelegate, dict[Click, int]) -> None
		self.colors = colors
		self.click = None # type: Click | None
		self.select = False
		self.id = id
		self.delegate = delegate
		self.edited = True
		PyMSDialog.__init__(self, parent, 'MiniTile Editor [%s]' % id, resizable=(False,False))

	def widgetize(self): # type: () -> Widget
		tileset = self.delegate.get_tileset()
		assert tileset is not None
		self.canvas = Canvas(self, width=202, height=114)
		self.canvas.pack(padx=3,pady=3)
		self.canvas.bind(ButtonRelease.Click_Left(), self.release)
		self.canvas.bind(ButtonRelease.Click_Right(), self.release)
		self.canvas.bind(Mouse.Motion(), self.motion)
		self.canvas.bind(Mouse.Drag_Left(), self.motion)
		self.canvas.bind(Mouse.Drag_Right(), self.motion)
		d = tileset.vr4.get_image(self.id)
		self.colors[Click.left] = d[0][0]
		self.indexs = []
		def color_callback(pos, click): # type: (tuple[int, int], Click) -> Callable[[Event], None]
			def color(_): # type: (Event) -> None
				self.color(pos, click)
			return color
		def pen_callback(index, click): # type: (int, Click) -> Callable[[Event], None]
			def pen(_) : # type: (Event) -> None
				self.pencolor(index, click)
			return pen
		for y,row in enumerate(d):
			self.indexs.append(list(row))
			for x,index in enumerate(row):
				cx,cy,c = x * 10 + 2, y * 10 + 2, '#%02x%02x%02x' % tuple(tileset.wpe.palette[index])
				t = 'tile%s,%s' % (x,y)
				self.canvas.create_rectangle(cx, cy, cx+10, cy+10, fill=c, outline=c, tags=t)
				self.canvas.tag_bind(t, Mouse.Click_Left(), color_callback((x,y), Click.left))
				self.canvas.tag_bind(t, Mouse.Click_Right(), color_callback((x,y), Click.right))
				cx,cy = x + 32,y + 90
				self.canvas.create_rectangle(cx, cy, cx+2, cy+2, fill=c, outline=c, tags='scale%s,%s' % (x,y))
		self.canvas.create_rectangle(90, 2, 202, 114, fill='#000000', outline='#000000')
		for n,rgb in enumerate(tileset.wpe.palette):
			cx,cy,c = (n % 16) * 7 + 91, (n // 16) * 7 + 3, '#%02x%02x%02x' % tuple(rgb)
			t = 'pal%s' % n
			self.canvas.create_rectangle(cx, cy, cx+5, cy+5, fill=c, outline=c, tags=t)
			c = '#%02x%02x%02x' % tuple(tileset.wpe.palette[self.colors[Click.right]])
			self.canvas.tag_bind(t, Mouse.Click_Left(), pen_callback(n, Click.left))
			self.canvas.tag_bind(t, Mouse.Click_Right(), pen_callback(n, Click.right))
		c = '#%02x%02x%02x' % tuple(tileset.wpe.palette[self.colors[Click.right]])
		self.canvas.create_rectangle(10, 98, 26, 114, fill=c, outline=c, tags='bg')
		c = '#%02x%02x%02x' % tuple(tileset.wpe.palette[self.colors[Click.left]])
		self.canvas.create_rectangle(2, 90, 18, 106, fill=c, outline=c, tags='fg')
		self.canvas.create_image(56, 101, image=Assets.get_image('eyedropper'), tags='eyedropper')
		self.canvas.tag_bind('eyedropper', Mouse.Click_Left(), self.dropper)
		b = Frame(self)
		ok = Button(b, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=2)
		Button(b, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		b.pack(pady=3)
		return ok

	def dropper(self, e=None): # type: (Event | None) -> None
		if self.select:
			self.canvas.delete('dropbd')
		else:
			self.canvas.create_rectangle(45, 90, 66, 111, outline='#000000', tags='dropbd')
		self.select = not self.select

	def release(self, e): # type: (Event) -> None
		self.click = None

	def motion(self, e): # type: (Event) -> None
		items = self.canvas.find_overlapping(e.x,e.y,e.x,e.y)
		if self.click is None or not items:
			return
		tags = items[0].get_tags()
		if not tags or not tags[0].startswith('tile'):
			return
		coords_str = tags[0][4:].split(',')
		self.color((int(coords_str[0]), int(coords_str[1])), self.click)

	def color(self, pos, click): # type: (tuple[int, int], Click) -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		if self.select:
			self.colors[click] = self.indexs[pos[1]][pos[0]]
			r = '#%02x%02x%02x' % tuple(tileset.wpe.palette[self.colors[click]])
			self.canvas.itemconfig(click.config_key(), fill=r, outline=r)
			self.dropper()
		else:
			self.indexs[pos[1]][pos[0]] = self.colors[click]
			r = '#%02x%02x%02x' % tuple(tileset.wpe.palette[self.colors[click]])
			self.canvas.itemconfig('tile%s,%s' % pos, fill=r, outline=r)
			self.canvas.itemconfig('scale%s,%s' % pos, fill=r, outline=r)
			self.click = click
		self.edited = True

	def pencolor(self, index, click): # type: (int, Click) -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		self.colors[click] = index
		r = '#%02x%02x%02x' % tuple(tileset.wpe.palette[index])
		self.canvas.itemconfig(click.config_key(), fill=r, outline=r)

	def ok(self, _=None): # type: (Event | None) -> None
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		if self.edited:
			tileset.vr4.set_image(self.id, self.indexs)
			self.delegate.mark_edited()
			from .TilePalette import TilePalette
			TilePalette.TILE_CACHE.clear()
			self.delegate.draw_tiles(force=True)
		PyMSDialog.ok(self)
