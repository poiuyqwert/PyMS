
from .Delegates import MiniEditorDelegate

from ..Utilities import Assets
from ..Utilities import UIKit as UI
from ..Utilities.PyMSDialog import PyMSDialog

from enum import Enum

from typing import Callable

class Click(Enum):
	left = 0
	right = 1

	def config_key(self) -> str:
		if self == Click.left:
			return 'fg'
		return 'bg'

class MiniEditor(PyMSDialog):
	def __init__(self, parent: UI.Misc, tile_id: int, delegate: MiniEditorDelegate, colors: dict[Click, int] | None = None) -> None:
		self.colors = colors if colors is not None else {Click.left:0, Click.right:0}
		self.click: Click | None = None
		self.select = False
		self.id = tile_id
		self.delegate = delegate
		self.edited = True
		PyMSDialog.__init__(self, parent, f'MiniTile Editor [{tile_id}]', resizable=(False,False))

	def widgetize(self) -> UI.Widget:
		tileset = self.delegate.get_tileset()
		assert tileset is not None
		self.canvas = UI.Canvas(self, width=202, height=114)
		self.canvas.pack(padx=3,pady=3)
		self.canvas.bind(UI.ButtonRelease.Click_Left(), self.release)
		self.canvas.bind(UI.ButtonRelease.Click_Right(), self.release)
		self.canvas.bind(UI.Mouse.Motion(), self.motion)
		self.canvas.bind(UI.Mouse.Drag_Left(), self.motion)
		self.canvas.bind(UI.Mouse.Drag_Right(), self.motion)
		d = tileset.vr4.get_image(self.id)
		self.colors[Click.left] = d[0][0]
		self.indexs = []
		def color_callback(pos: tuple[int, int], click: Click) -> Callable[[UI.Event], None]:
			def color(_: UI.Event) -> None:
				self.color(pos, click)
			return color
		def pen_callback(index: int, click: Click) -> Callable[[UI.Event], None]:
			def pen(_: UI.Event) -> None:
				self.pencolor(index, click)
			return pen
		for y,row in enumerate(d):
			self.indexs.append(list(row))
			for x,index in enumerate(row):
				cx = x * 10 + 2
				cy = y * 10 + 2
				c = UI.Colors.to_html(tileset.wpe.palette[index])
				t = f'tile{x},{y}'
				self.canvas.create_rectangle(cx, cy, cx+10, cy+10, fill=c, outline=c, tags=t)
				self.canvas.tag_bind(t, UI.Mouse.Click_Left(), color_callback((x,y), Click.left))
				self.canvas.tag_bind(t, UI.Mouse.Click_Right(), color_callback((x,y), Click.right))
				cx,cy = x + 32,y + 90
				self.canvas.create_rectangle(cx, cy, cx+2, cy+2, fill=c, outline=c, tags=f'scale{x},{y}')
		self.canvas.create_rectangle(90, 2, 202, 114, fill='#000000', outline='#000000')
		for n,rgb in enumerate(tileset.wpe.palette):
			cx = (n % 16) * 7 + 91
			cy = (n // 16) * 7 + 3
			c = UI.Colors.to_html(rgb)
			t = f'pal{n}'
			self.canvas.create_rectangle(cx, cy, cx+5, cy+5, fill=c, outline=c, tags=t)
			c = UI.Colors.to_html(tileset.wpe.palette[self.colors[Click.right]])
			self.canvas.tag_bind(t, UI.Mouse.Click_Left(), pen_callback(n, Click.left))
			self.canvas.tag_bind(t, UI.Mouse.Click_Right(), pen_callback(n, Click.right))
		c = UI.Colors.to_html(tileset.wpe.palette[self.colors[Click.right]])
		self.canvas.create_rectangle(10, 98, 26, 114, fill=c, outline=c, tags='bg')
		c = UI.Colors.to_html(tileset.wpe.palette[self.colors[Click.left]])
		self.canvas.create_rectangle(2, 90, 18, 106, fill=c, outline=c, tags='fg')
		self.canvas.create_image(56, 101, image=Assets.get_image('eyedropper'), tags='eyedropper')
		self.canvas.tag_bind('eyedropper', UI.Mouse.Click_Left(), self.dropper)
		b = UI.Frame(self)
		ok = UI.Button(b, text='Ok', width=10, command=self.ok)
		ok.pack(side=UI.LEFT, padx=2)
		UI.Button(b, text='Cancel', width=10, command=self.cancel).pack(side=UI.LEFT)
		b.pack(pady=3)
		return ok

	def dropper(self, _event: UI.Event | None = None) -> None:
		if self.select:
			self.canvas.delete('dropbd')
		else:
			self.canvas.create_rectangle(45, 90, 66, 111, outline='#000000', tags='dropbd')
		self.select = not self.select

	def release(self, _event: UI.Event | None = None) -> None:
		self.click = None

	def motion(self, event: UI.Event) -> None:
		items = self.canvas.find_overlapping(event.x,event.y,event.x,event.y)
		if self.click is None or not items:
			return
		tags = items[0].get_tags()
		if not tags or not tags[0].startswith('tile'):
			return
		coords_str = tags[0][4:].split(',')
		self.color((int(coords_str[0]), int(coords_str[1])), self.click)

	def color(self, pos: tuple[int, int], click: Click) -> None:
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		if self.select:
			self.colors[click] = self.indexs[pos[1]][pos[0]]
			r = UI.Colors.to_html(tileset.wpe.palette[self.colors[click]])
			self.canvas.itemconfig(click.config_key(), fill=r, outline=r)
			self.dropper()
		else:
			self.indexs[pos[1]][pos[0]] = self.colors[click]
			r = UI.Colors.to_html(tileset.wpe.palette[self.colors[click]])
			self.canvas.itemconfig(f'tile{pos[0]},{pos[1]}', fill=r, outline=r)
			self.canvas.itemconfig(f'scale{pos[0]},{pos[1]}', fill=r, outline=r)
			self.click = click
		self.edited = True

	def pencolor(self, index: int, click: Click) -> None:
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		self.colors[click] = index
		r = UI.Colors.to_html(tileset.wpe.palette[index])
		self.canvas.itemconfig(click.config_key(), fill=r, outline=r)

	def ok(self, _: UI.Event | None = None) -> None:
		tileset = self.delegate.get_tileset()
		if not tileset:
			return
		if self.edited:
			tileset.vr4.set_image(self.id, self.indexs)
			self.delegate.mark_edited()
			from .TilePalette import TilePalette  # pylint: disable=cyclic-import
			TilePalette.TILE_CACHE.clear()
			self.delegate.draw_tiles(force=True)
		PyMSDialog.ok(self)
