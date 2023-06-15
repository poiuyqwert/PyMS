
from .Delegates import TilePaletteViewDelegate

from ..FileFormats.Tileset.Tileset import TileType
from ..FileFormats.Tileset.VX4 import VX4Minitile

from ..Utilities.UIKit import *

from math import ceil

from typing import Callable

class TilePaletteView(Frame):
	# sub_select currently only supported by TileType.group when multiselect=False
	def __init__(self, parent, delegate, tiletype=TileType.group, select=None, multiselect=True, sub_select=False): # type: (Misc, TilePaletteViewDelegate, TileType, int | list[int] | None, bool, bool) -> None
		Frame.__init__(self, parent)
		self.tiletype = tiletype
		self.selected = [] # type: list[int]
		self.last_selection = None # type: tuple[int, bool] | None # (index, on_or_off)
		self.sub_selection = 0
		if select is not None:
			if isinstance(select, list):
				self.selected.extend(sorted(select))
			else:
				self.selected.append(select)
		self.delegate = delegate
		self.multiselect = multiselect
		if not multiselect:
			if not self.selected:
				self.selected.append(0)
			elif len(self.selected) > 1:
				self.selected = self.selected[:1]
		self.sub_select = not self.multiselect and sub_select

		self.visible_range = (-1, -1)

		tile_size = self.get_tile_size()
		self.canvas = Canvas(self, width=2 + tile_size[0] * 16, height=2 + tile_size[1] * 8, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.canvas_images = {} # type: dict[int, Image]
		self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
		scrollbar = Scrollbar(self, command=self.canvas.yview)
		scrollbar.pack(side=LEFT, fill=Y)

		def canvas_resized(e):
			self.update_size()
		self.canvas.bind(WidgetEvent.Configure(), canvas_resized)
		binding_widget = self.delegate.tile_palette_binding_widget()
		binding_widget.bind(Mouse.Scroll(), lambda e: self.canvas.yview('scroll', -(e.delta // abs(e.delta)) if e.delta else 0,'units'))
		if self.delegate.tile_palette_bind_updown():
			binding_widget.bind(Key.Down(), lambda e: self.canvas.yview('scroll', 1,'units'))
			binding_widget.bind(Key.Up(), lambda e: self.canvas.yview('scroll', -1,'units'))
		binding_widget.bind(Key.Next(), lambda e: self.canvas.yview('scroll', 1,'page'))
		binding_widget.bind(Key.Prior(), lambda e: self.canvas.yview('scroll', -1,'page'))
		def yscrollcommand(scrollbar): # type: (Scrollbar) -> Callable[[float, float], None]
			def update_scrollbar(l,h): # type: (float, float) -> None
				scrollbar.set(l,h)
				self.draw_tiles()
			return update_scrollbar
		self.canvas.config(yscrollcommand=yscrollcommand(scrollbar))

		self.initial_scroll_bind = None
		def initial_scroll(_): # type: (Any) -> None
			self.scroll_to_selection()
			if self.initial_scroll_bind is None:
				return
			self.canvas.remove_bind(WidgetEvent.Configure(), self.initial_scroll_bind)
			self.initial_scroll_bind = None
		self.initial_scroll_bind = self.canvas.bind(WidgetEvent.Configure(), initial_scroll, add=True)

	def get_tile_size(self, tiletype=None, group=False): # type: (TileType | None, bool) -> tuple[int, int]
		tiletype = self.tiletype if tiletype is None else tiletype
		match tiletype:
			case TileType.group:
				return (32 * (16 if group else 1), 33)
			case TileType.mega:
				return (32 + (0 if group else 1), 32 + (0 if group else 1))
			case TileType.mini:
				return (25, 25)

	def get_tile_count(self): # type: () -> int
		tileset = self.delegate.get_tileset()
		if not tileset:
			return 0
		match self.tiletype:
			case TileType.group:
				return tileset.cv5.group_count() * 16
			case TileType.mega:
				return tileset.vx4.megatile_count()
			case TileType.mini:
				return tileset.vr4.image_count()

	def get_total_size(self): # type: () -> tuple[int,int]
		tile_size = self.get_tile_size()
		tile_count = self.get_tile_count()
		width = self.canvas.winfo_width()
		columns = width // tile_size[0]
		if not columns:
			return (0, 0)
		return (width, int(ceil(tile_count / float(columns))) * tile_size[1] + 1)

	def update_size(self): # type: () -> None
		total_size = self.get_total_size()
		self.canvas.config(scrollregion=(0,0,total_size[0],total_size[1]))
		self.draw_tiles()

	def draw_selections(self): # type: () -> None
		self.canvas.delete('selection')
		self.canvas.delete('sub_selection')
		tile_size = self.get_tile_size(group=self.tiletype == TileType.group)
		columns = self.canvas.winfo_width() // tile_size[0]
		if not columns:
			return
		for id in self.selected:
			x = (id % columns) * tile_size[0]
			y = (id // columns) * tile_size[1]
			self.canvas.create_rectangle(x, y, x+tile_size[0], y+tile_size[1], outline='#AAAAAA' if self.sub_select else '#FFFFFF', tags='selection')
			if self.sub_select:
				mega_size = self.get_tile_size(TileType.mega, group=True)
				x += mega_size[0] * self.sub_selection
				self.canvas.create_rectangle(x, y, x+mega_size[0]+1, y+mega_size[1]+1, outline='#FFFFFF', tags='sub_selection')

	def draw_tiles(self, force=False): # type: (bool) -> None
		tileset = self.delegate.get_tileset()
		if force or not tileset:
			self.visible_range = (-1, -1)
			self.canvas.delete(ALL)
			self.canvas_images.clear()
		if not tileset:
			return
		viewport_size = (self.canvas.winfo_width(), self.canvas.winfo_height())
		tile_size = self.get_tile_size()
		tile_count = self.get_tile_count()
		_,_,_,total_height = parse_scrollregion(self.canvas.cget('scrollregion'))
		topy = int(self.canvas.yview()[0] * total_height)
		start_row = topy // tile_size[1]
		start_y = start_row * int(tile_size[1])
		tiles_size = (viewport_size[0] // tile_size[0], int(ceil((viewport_size[1] + topy-start_y) / float(tile_size[1]))))
		first = start_row * tiles_size[0]
		last = min(tile_count,first + tiles_size[0] * tiles_size[1]) - 1
		visible_range = (first, last)
		if visible_range != self.visible_range:
			update_ranges = [visible_range]
			overlaps = self.visible_range[0] > -1 \
				and ((self.visible_range[0] <= visible_range[0] <= self.visible_range[1] or self.visible_range[0] <= visible_range[1] <= self.visible_range[1]) \
				or (visible_range[0] <= self.visible_range[0] <= visible_range[1] or visible_range[0] <= self.visible_range[1] <= visible_range[1]))
			if overlaps:
				update_ranges = [(min(self.visible_range[0],visible_range[0]), max(self.visible_range[1],visible_range[1]))]
			elif self.visible_range[0] > -1:
				update_ranges.append(self.visible_range)
			for update_range in update_ranges:
				for id in range(update_range[0],update_range[1]+1):
					if (id < visible_range[0] or id > visible_range[1]) and id >= self.visible_range[0] and id <= self.visible_range[1]:
						del self.canvas_images[id]
						self.canvas.delete('tile%s' % id)
					else:
						n = id - visible_range[0]
						x = 1 + (n % tiles_size[0]) * tile_size[0]
						y = 1 + start_y + (n // tiles_size[0]) * tile_size[1]
						if self.visible_range and id >= self.visible_range[0] and id <= self.visible_range[1]:
							self.canvas.coords('tile%s' % id, x,y)
						else:
							if self.tiletype == TileType.group:
								group = id // 16
								megatile = tileset.cv5.get_group(group).megatile_ids[id % 16]
								self.canvas_images[id] = self.delegate.get_tile(megatile)
							elif self.tiletype == TileType.mega:
								self.canvas_images[id] = self.delegate.get_tile(id)
							elif self.tiletype == TileType.mini:
								self.canvas_images[id] = self.delegate.get_tile(VX4Minitile(id, False))
							tag = 'tile%s' % id
							self.canvas.create_image(x,y, image=self.canvas_images[id], tags=tag, anchor=NW)
							def select_callback(id, modifier): # type: (int, str | None) -> Callable[[Event], None]
								def select(_): # type: (Event) -> None
									select_id = id
									sub_select = None
									if self.tiletype == TileType.group:
										if self.sub_select:
											sub_select = id % 16
										select_id //= 16
									self.select(select_id, sub_select, modifier)
								return select
							self.canvas.tag_bind(tag, Mouse.Click_Left(), select_callback(id,'set'))
							self.canvas.tag_bind(tag, Shift.Click_Left(), select_callback(id,'shift'))
							self.canvas.tag_bind(tag, Ctrl.Click_Left(), select_callback(id,'cntrl'))
							def double_click_callback(id): # type: (int) -> Callable[[Event], None]
								id //= (16 if self.tiletype == TileType.group else 1)
								def double_click(_): # type: (Event) -> None
									self.delegate.tile_palette_double_clicked(id)
								return double_click
							self.canvas.tag_bind(tag, Double.Click_Left(), double_click_callback(id))
			self.visible_range = visible_range
			self.draw_selections()

	def set_selection(self, selection, scroll_to=False): # type: (int | list[int], bool) -> None
		self.last_selection = None
		if isinstance(selection, list):
			self.selected = selection
		else:
			self.selected = [selection]
		self.draw_selections()
		if scroll_to:
			self.scroll_to_selection()
		self.delegate.tile_palette_selection_changed()

	def select(self, select, sub_select=None, modifier=None, scroll_to=False): # type: (int, int | None, str | None, bool) -> None
		if self.multiselect:
			if modifier == 'shift':
				if self.last_selection is not None:
					last_select,enable = self.last_selection
					start = min(last_select,select)
					end = max(last_select,select)
					for index in range(start,end+1):
						if enable and not index in self.selected:
							self.selected.append(index)
						elif not enable and index in self.selected:
							self.selected.remove(index)
					if enable:
						self.selected.sort()
					self.last_selection = (select, enable)
					modifier = None
				else:
					modifier = 'cntrl'
			if modifier == 'cntrl':
				if select in self.selected:
					self.selected.remove(select)
					self.last_selection = (select, False)
				else:
					self.selected.append(select)
					self.selected.sort()
					self.last_selection = (select, True)
			elif modifier == 'set':
				self.selected = [select]
				if self.selected:
					self.last_selection = (select, True)
				else:
					self.last_selection = None
		else:
			self.last_selection = None
			self.selected = [select]
			if sub_select is not None:
				self.sub_selection = sub_select
		self.draw_selections()
		if scroll_to:
			self.scroll_to_selection()
		self.delegate.tile_palette_selection_changed()

	def scroll_to_selection(self): # type: () -> None
		if not len(self.selected):
			return
		tile_size = self.get_tile_size(group=True)
		viewport_size = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		columns = viewport_size[0] // tile_size[0]
		if not columns:
			return
		total_size = self.get_total_size()
		max_y = total_size[1] - viewport_size[1]
		id = self.selected[0]
		y = max(0,min(max_y,(id // columns + 0.5) * tile_size[1] - viewport_size[1]/2.0))
		self.canvas.yview_moveto(y // total_size[1])
