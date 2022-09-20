
from ..FileFormats.Tileset.Tileset import TILETYPE_GROUP, TILETYPE_MEGA, TILETYPE_MINI

from ..Utilities.UIKit import *

from math import ceil, floor

class TilePaletteView(Frame):
	# sub_select currently only supported by TILETYPE_GROUP when multiselect=False
	def __init__(self, parent, tiletype=TILETYPE_GROUP, select=None, delegate=None, multiselect=True, sub_select=False):
		Frame.__init__(self, parent)
		self.tiletype = tiletype
		self.selected = []
		self.last_selection = None # (index, on_or_off)
		self.sub_selection = 0
		if select != None:
			if isinstance(select, list):
				self.selected.extend(sorted(select))
			else:
				self.selected.append(select)
		self.delegate = delegate or parent
		self.multiselect = multiselect
		if not multiselect:
			if not self.selected:
				self.selected.append(0)
			elif len(self.selected) > 1:
				self.selected = self.selected[:1]
		self.sub_select = not self.multiselect and sub_select

		self.visible_range = None
		self.gettile = self.delegate.tile_palette_get_tile()

		tile_size = self.get_tile_size()
		self.canvas = Canvas(self, width=2 + tile_size[0] * 16, height=2 + tile_size[1] * 8, background='#000000')
		self.canvas.images = {}
		self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
		scrollbar = Scrollbar(self, command=self.canvas.yview)
		scrollbar.pack(side=LEFT, fill=Y)

		def canvas_resized(e):
			self.update_size()
		self.canvas.bind(WidgetEvent.Configure, canvas_resized)
		binding_widget = self.delegate.tile_palette_binding_widget()
		binding_widget.bind(Mouse.Scroll, lambda e: self.canvas.yview('scroll', -(e.delta / abs(e.delta)) if e.delta else 0,'units'))
		if not hasattr(self.delegate, 'tile_palette_bind_updown') or self.delegate.tile_palette_bind_updown():
			binding_widget.bind(Key.Down, lambda e: self.canvas.yview('scroll', 1,'units'))
			binding_widget.bind(Key.Up, lambda e: self.canvas.yview('scroll', -1,'units'))
		binding_widget.bind(Key.Next, lambda e: self.canvas.yview('scroll', 1,'page'))
		binding_widget.bind(Key.Prior, lambda e: self.canvas.yview('scroll', -1,'page'))
		def update_scrollbar(l,h,bar):
			scrollbar.set(l,h)
			self.draw_tiles()
		self.canvas.config(yscrollcommand=lambda l,h,s=scrollbar: update_scrollbar(l,h,s))

		self.initial_scroll_bind = None
		def initial_scroll(_):
			self.scroll_to_selection()
			self.canvas.unbind(WidgetEvent.Configure, self.initial_scroll_bind)
		self.initial_scroll_bind = self.canvas.bind(WidgetEvent.Configure, initial_scroll, add=True)


	def get_tile_size(self, tiletype=None, group=False):
		tiletype = self.tiletype if tiletype == None else tiletype
		if tiletype == TILETYPE_GROUP:
			return [32.0 * (16 if group else 1),33.0]
		elif tiletype == TILETYPE_MEGA:
			return [32.0 + (0 if group else 1),32.0 + (0 if group else 1)]
		elif tiletype == TILETYPE_MINI:
			return [25.0,25.0]
	def get_tile_count(self):
		tileset = self.delegate.tile_palette_get_tileset()
		if not tileset:
			return 0
		if self.tiletype == TILETYPE_GROUP:
			return len(tileset.cv5.groups) * 16
		elif self.tiletype == TILETYPE_MEGA:
			return len(tileset.vx4.graphics)
		elif self.tiletype == TILETYPE_MINI:
			return len(tileset.vr4.images)
	def get_total_size(self):
		tile_size = self.get_tile_size()
		tile_count = self.get_tile_count()
		width = self.canvas.winfo_width()
		columns = floor(width / tile_size[0])
		total_size = [0,0]
		if columns:
			total_size = [width,int(ceil(tile_count / columns)) * tile_size[1] + 1]
		return total_size

	def update_size(self):
		total_size = self.get_total_size()
		self.canvas.config(scrollregion=(0,0,total_size[0],total_size[1]))
		self.draw_tiles()

	def draw_selections(self):
		self.canvas.delete('selection')
		self.canvas.delete('sub_selection')
		tile_size = self.get_tile_size(group=self.tiletype == TILETYPE_GROUP)
		columns = int(floor(self.canvas.winfo_width() / tile_size[0]))
		if columns:
			for id in self.selected:
				x = (id % columns) * tile_size[0]
				y = (id / columns) * tile_size[1]
				self.canvas.create_rectangle(x, y, x+tile_size[0], y+tile_size[1], outline='#AAAAAA' if self.sub_select else '#FFFFFF', tags='selection')
				if self.sub_select:
					mega_size = self.get_tile_size(TILETYPE_MEGA, group=True)
					x += mega_size[0] * self.sub_selection
					self.canvas.create_rectangle(x, y, x+mega_size[0]+1, y+mega_size[1]+1, outline='#FFFFFF', tags='sub_selection')

	def draw_tiles(self, force=False):
		tileset = self.delegate.tile_palette_get_tileset()
		if force or not tileset:
			self.visible_range = None
			self.canvas.delete(ALL)
			self.canvas.images.clear()
		if not tileset:
			return
		viewport_size = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		tile_size = self.get_tile_size()
		tile_count = self.get_tile_count()
		total_height = float((self.canvas.cget('scrollregion') or '0').split(' ')[-1])
		topy = int(self.canvas.yview()[0] * total_height)
		start_row = int(floor(topy / tile_size[1]))
		start_y = start_row * int(tile_size[1])
		tiles_size = [int(floor(viewport_size[0] / tile_size[0])),int(ceil((viewport_size[1] + topy-start_y) / tile_size[1]))]
		first = start_row * tiles_size[0]
		last = min(tile_count,first + tiles_size[0] * tiles_size[1]) - 1
		visible_range = [first,last]
		if visible_range != self.visible_range:
			update_ranges = [visible_range]
			overlaps = self.visible_range \
				and ((self.visible_range[0] <= visible_range[0] <= self.visible_range[1] or self.visible_range[0] <= visible_range[1] <= self.visible_range[1]) \
				or (visible_range[0] <= self.visible_range[0] <= visible_range[1] or visible_range[0] <= self.visible_range[1] <= visible_range[1]))
			if overlaps:
				update_ranges = [[min(self.visible_range[0],visible_range[0]),max(self.visible_range[1],visible_range[1])]]
			elif self.visible_range:
				update_ranges.append(self.visible_range)
			for update_range in update_ranges:
				for id in range(update_range[0],update_range[1]+1):
					if (id < visible_range[0] or id > visible_range[1]) and id >= self.visible_range[0] and id <= self.visible_range[1]:
						del self.canvas.images[id]
						self.canvas.delete('tile%s' % id)
					else:
						n = id - visible_range[0]
						x = 1 + (n % tiles_size[0]) * tile_size[0]
						y = 1 + start_y + floor(n / tiles_size[0]) * tile_size[1]
						if self.visible_range and id >= self.visible_range[0] and id <= self.visible_range[1]:
							self.canvas.coords('tile%s' % id, x,y)
						else:
							if self.tiletype == TILETYPE_GROUP:
								group = int(id / 16.0)
								megatile = tileset.cv5.groups[group][13][id % 16]
								self.canvas.images[id] = self.gettile(megatile,cache=True)
							elif self.tiletype == TILETYPE_MEGA:
								self.canvas.images[id] = self.gettile(id,cache=True)
							elif self.tiletype == TILETYPE_MINI:
								self.canvas.images[id] = self.gettile((id,0),cache=True)
							tag = 'tile%s' % id
							self.canvas.create_image(x,y, image=self.canvas.images[id], tags=tag, anchor=NW)
							def select(id, modifier):
								sub_select = None
								if self.tiletype == TILETYPE_GROUP:
									if self.sub_select:
										sub_select = id % 16
									id /= 16
								self.select(id, sub_select, modifier)
							self.canvas.tag_bind(tag, Mouse.Click_Left, lambda e,id=id: select(id,None))
							self.canvas.tag_bind(tag, Shift.Click_Left, lambda e,id=id: select(id,'shift'))
							self.canvas.tag_bind(tag, Ctrl.Click_Left, lambda e,id=id: select(id,'cntrl'))
							if hasattr(self.delegate, 'tile_palette_double_clicked'):
								self.canvas.tag_bind(tag, Double.Click_Left, lambda e,id=id / (16 if self.tiletype == TILETYPE_GROUP else 1): self.delegate.tile_palette_double_clicked(id))
			self.visible_range = visible_range
			self.draw_selections()

	def select(self, select, sub_select=None, modifier=None, scroll_to=False):
		if self.multiselect:
			if modifier == 'shift':
				if self.last_selection != None:
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
					select = None
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
			elif select != None:
				if isinstance(select, list):
					select = sorted(select)
				else:
					select = [select]
				self.selected = select
				if self.selected:
					self.last_selection = (self.selected[-1], True)
				else:
					self.last_selection = None
		else:
			if isinstance(select, list):
				select = select[0] if select else 0
			self.selected = [select]
			if sub_select != None:
				self.sub_selection = sub_select
		self.draw_selections()
		if scroll_to:
			self.scroll_to_selection()
		if hasattr(self.delegate, 'tile_palette_selection_changed'):
			self.delegate.tile_palette_selection_changed()

	def scroll_to_selection(self):
		if not len(self.selected):
			return
		tile_size = self.get_tile_size(group=True)
		viewport_size = [self.canvas.winfo_width(),self.canvas.winfo_height()]
		columns = int(floor(viewport_size[0] / tile_size[0]))
		if not columns:
			return
		total_size = self.get_total_size()
		max_y = total_size[1] - viewport_size[1]
		id = self.selected[0]
		y = max(0,min(max_y,(id / columns + 0.5) * tile_size[1] - viewport_size[1]/2.0))
		self.canvas.yview_moveto(y / total_size[1])
