
from DATUnitsTab import DATUnitsTab

from ..FileFormats.DAT.ImagesDAT import Image as DATImage

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class GraphicsUnitsTab(DATUnitsTab):
	def __init__(self, parent, toplevel, parent_tab):
		DATUnitsTab.__init__(self, parent, toplevel, parent_tab)
		self.toplevel = toplevel
		frame = Frame(self)

		self.graphicsentry = IntegerVar(0, [0,208])
		self.graphicsdd = IntVar()
		self.constructionentry = IntegerVar(0, [0,998])
		self.constructiondd = IntVar()
		self.portraitsentry = IntegerVar(0, [0,109], maxout=65535)
		self.portraitsdd = IntVar()
		self.elevationentry = IntegerVar(0, [0,19])
		self.elevationdd = IntVar()
		self.direction = IntegerVar(0, [0,255])

		gfx = [
			('Graphics', self.graphicsentry, self.graphicsdd, 'Flingy.txt', 'UnitGfx', None),
			('Construction', self.constructionentry, self.constructiondd, 'Images.txt', 'UnitConstruction', None),
			('Portraits', self.portraitsentry, self.portraitsdd, 'Portdata.txt', 'UnitPortrait', 65535),
			('Elevation', self.elevationentry, self.elevationdd, 'ElevationLevels.txt', 'UnitElevationLevel', None),
		]
		l = LabelFrame(frame, text='Sprite Graphics:')
		s = Frame(l)
		for t,e,d,q,h,n in gfx:
			f = Frame(s)
			Label(f, text=t + ':', width=13, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=e, font=couriernew, width=5).pack(side=LEFT)
			Label(f, text='=').pack(side=LEFT)
			DropDown(f, d, DATA_CACHE[q], e, width=30, none_value=n).pack(side=LEFT, fill=X, expand=1, padx=2)
			if t != 'Elevation':
				Button(f, text='Jump ->', command=lambda t=q.split('.')[0],i=d: self.jump(t,i)).pack(side=LEFT)
			self.tip(f, t, h)
			f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Direction:', width=13, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.direction, font=couriernew, width=3).pack(side=LEFT)
		self.tip(f, 'Direction', 'UnitDirection')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.left = IntegerVar(0, [0,65535])
		self.right = IntegerVar(0, [0,65535])
		self.up = IntegerVar(0, [0,65535])
		self.down = IntegerVar(0, [0,65535])
		self.horizontal = IntegerVar(0, [0,65535])
		self.vertical = IntegerVar(0, [0,65535])
		self.previewing = None
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.data_context.settings.preview.unit.get('show', False))
		self.showplace = IntVar()
		self.showplace.set(self.toplevel.data_context.settings.preview.unit.get('show_placement', False))
		self.showdims = IntVar()
		self.showdims.set(self.toplevel.data_context.settings.preview.unit.get('show_dimensions', False))
		self.show_addon_placement = IntVar()
		self.show_addon_placement.set(self.toplevel.data_context.settings.preview.unit.get('show_addon_placement', False))
		self.addon_parent_id = IntegerVar(0, [0,228])
		self.addon_parent_id.set(self.toplevel.data_context.settings.preview.unit.get('addon_parent_unit_id', 106))

		bottom = Frame(frame)
		left = Frame(bottom)
		l = LabelFrame(left, text='Unit Dimensions:')
		s = Frame(l)
		dims = [
			('Left', self.left),
			('Right', self.right),
			('Up', self.up),
			('Down', self.down),
		]
		for t,v in dims:
			f = Frame(s)
			Label(f, text='%s:' % t, width=13, anchor=E).pack(side=LEFT)
			Entry(f, textvariable=v, font=couriernew, width=5).pack(side=LEFT)
			self.tip(f, t + ' Dimension', 'UnitDim' + t)
			f.pack(fill=X)
		s.pack(padx=5, pady=5)
		l.pack(side=TOP, fill=X)
		l = LabelFrame(left, text='Addon Position:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Horizontal:', width=13, anchor=E).pack(side=LEFT)
		self.horizontalw = Entry(f, textvariable=self.horizontal, font=couriernew, width=5)
		self.horizontalw.pack(side=LEFT)
		self.tip(f, 'Addons Horizontal Position', 'UnitAddPosX')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vertical:', width=13, anchor=E).pack(side=LEFT)
		self.verticalw = Entry(f, textvariable=self.vertical, font=couriernew, width=5)
		self.verticalw.pack(side=LEFT)
		self.tip(f, 'Addons Vertical Position', 'UnitAddPosY')
		f.pack(fill=X)
		s.pack(padx=5, pady=5)
		l.pack(side=TOP, fill=X)
		left.pack(side=LEFT, fill=BOTH, expand=1)
		l = LabelFrame(bottom, text='Preview:')
		s = Frame(l)
		self.preview = Canvas(s, width=257, height=257, background='#000000')
		self.preview.pack(side=TOP)
		self.preview.create_rectangle(0, 0, 0, 0, outline='#00FF00', tags='size')
		self.preview.create_rectangle(0, 0, 0, 0, outline='#FF0000', tags='place')
		self.preview.create_rectangle(0, 0, 0, 0, outline='#FFFF00', tags='addon_parent_size')
		Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack(side=TOP)
		o = Frame(s)
		Checkbutton(o, text='Show StarEdit Placement Box (Red)', variable=self.showplace, command=self.drawboxes).pack(side=LEFT)
		Checkbutton(o, text='Show Dimensions Box (Green)', variable=self.showdims, command=self.drawboxes).pack(side=LEFT)
		o.pack(side=TOP)
		a = Frame(s)
		self.show_addon_placement_checkbox = Checkbutton(a, text='Show Addon Placement (Yellow) with parent building:', variable=self.show_addon_placement, command=self.drawpreview)
		self.show_addon_placement_checkbox.pack(side=LEFT)
		self.addon_parent_id_entry = Entry(a, textvariable=self.addon_parent_id, font=couriernew, width=3)
		self.addon_parent_id_entry.pack(side=LEFT)
		a.pack(side=BOTTOM)
		s.pack()
		l.pack()
		bottom.pack(fill=X)

		frame.pack(side=LEFT, fill=Y)

		for v in (self.graphicsentry, self.horizontal, self.vertical, self.addon_parent_id):
			v.trace('w', lambda *_: self.drawpreview())
		for v in (self.left, self.up, self.right, self.down):
			v.trace('w', lambda *_: self.drawboxes())

	def drawboxes(self):
		if self.showpreview.get() and self.showplace.get():
			entry = self.parent_tab.dat.get_entry(self.parent_tab.id)
			w = entry.staredit_placement_size.width / 2
			h = entry.staredit_placement_size.height / 2
			self.preview.coords('place', 129-w, 129-h, 129+w, 129+h)
			self.preview.lift('place')
		else:
			self.preview.coords('place', 0, 0, 0, 0)
		if self.showpreview.get() and self.showdims.get():
			self.preview.coords('size', 129-self.left.get(), 129-self.up.get(), 129+self.right.get(), 129+self.down.get())
			self.preview.lift('size')
		else:
			self.preview.coords('size', 0, 0, 0 ,0)

	def draw_image(self, image_id, tag, x=130, y=130):
		image_entry = self.toplevel.images.get_entry(image_id)
		tbl_index = image_entry.grp_file
		if tbl_index:
			grp_path = self.toplevel.data_context.imagestbl.strings[tbl_index - 1][:-1]
			sprite = self.toplevel.data_context.get_grp_frame(grp_path)
			if sprite:
				self.preview.create_image(x, y, image=sprite[0], tags=tag)

	def draw_addon_preview(self):
		self.preview.delete('addon_parent')
		addon_preview = self.showpreview.get()
		addon_preview = addon_preview and self.show_addon_placement_checkbox['state'] == NORMAL
		addon_preview = addon_preview and self.show_addon_placement.get()
		addon_preview = addon_preview and (self.horizontal.get() or self.vertical.get())
		if addon_preview:
			entry = self.parent_tab.dat.get_entry(self.parent_tab.id)
			w = entry.staredit_placement_size.width
			h = entry.staredit_placement_size.height
			parent_id = self.addon_parent_id.get()
			parent_entry = self.parent_tab.dat.get_entry(parent_id)
			parent_w = parent_entry.staredit_placement_size.width
			parent_h = parent_entry.staredit_placement_size.height
			x = 129 - w/2 - self.horizontal.get()
			y = 129 - h/2 - self.vertical.get()
			parent_flingy = self.toplevel.flingy.get_entry(parent_entry.graphics)
			parent_sprite = self.toplevel.sprites.get_entry(parent_flingy.sprite)
			self.draw_image(parent_sprite.image_file, 'addon_parent', x=x+parent_w/2, y=y+parent_h/2)
			self.preview.coords('addon_parent_size', x, y, x+parent_w, y+parent_h)
			self.preview.lift('addon_parent_size')
		else:
			self.preview.coords('addon_parent_size', 0, 0, 0 ,0)

	def drawpreview(self):
		self.draw_addon_preview()
		self.preview.delete('unit')
		if self.showpreview.get():
			flingy_id = self.graphicsentry.get()
			flingy = self.toplevel.flingy.get_entry(flingy_id)
			sprite = self.toplevel.sprites.get_entry(flingy.sprite)
			self.draw_image(sprite.image_file, 'unit')
		self.drawboxes()

	def load_data(self, entry):
		self.graphicsentry.set(entry.graphics)
		self.constructionentry.set(entry.construction_animation)
		self.direction.set(entry.unit_direction)
		self.elevationentry.set(entry.elevation_level)
		self.left.set(entry.unit_extents.left)
		self.up.set(entry.unit_extents.up)
		self.right.set(entry.unit_extents.right)
		self.down.set(entry.unit_extents.down)
		self.portraitsentry.set(entry.portrait)

		has_addon_positon = entry.addon_position != None
		self.horizontal.set(entry.addon_position.x if has_addon_positon else 0)
		self.vertical.set(entry.addon_position.y if has_addon_positon else 0)
		state = (DISABLED,NORMAL)[has_addon_positon]
		self.horizontalw['state'] = state
		self.verticalw['state'] = state
		self.show_addon_placement_checkbox['state'] = state
		self.addon_parent_id_entry['state'] = state
		self.drawpreview()

	def save_data(self, entry):
		self.toplevel.data_context.settings.preview.unit.show = not not self.showpreview.get()
		self.toplevel.data_context.settings.preview.unit.show_placement = not not self.showplace.get()
		self.toplevel.data_context.settings.preview.unit.show_dimensions = not not self.showdims.get()
		self.toplevel.data_context.settings.preview.unit.show_addon_placement = not not self.show_addon_placement.get()
		self.toplevel.data_context.settings.preview.unit.addon_parent_id = self.addon_parent_id.get()

		edited = False
		if self.graphicsentry.get() != entry.graphics:
			entry.graphics = self.graphicsentry.get()
			edited = True
		if self.constructionentry.get() != entry.construction_animation:
			entry.construction_animation = self.constructionentry.get()
			edited = True
		if self.direction.get() != entry.unit_direction:
			entry.unit_direction = self.direction.get()
			edited = True
		if self.elevationentry.get() != entry.elevation_level:
			entry.elevation_level = self.elevationentry.get()
			edited = True
		if self.left.get() != entry.unit_extents.left:
			entry.unit_extents.left = self.left.get()
			edited = True
		if self.up.get() != entry.unit_extents.up:
			entry.unit_extents.up = self.up.get()
			edited = True
		if self.right.get() != entry.unit_extents.right:
			entry.unit_extents.right = self.right.get()
			edited = True
		if self.down.get() != entry.unit_extents.down:
			entry.unit_extents.down = self.down.get()
			edited = True
		if self.portraitsentry.get() != entry.portrait:
			entry.portrait = self.portraitsentry.get()
			edited = True

		if entry.addon_position != None:
			if self.horizontal.get() != entry.addon_position.x:
				entry.addon_position.x = self.horizontal.get()
				edited = True
			if self.vertical.get() != entry.addon_position.y:
				entry.addon_position.y = self.vertical.get()
				edited = True

		return edited
