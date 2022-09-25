
from .DATTab import DATTab
from .DataID import DATID
from .DATRef import DATRefs, DATRef

from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.UIKit import *
from ..Utilities.ScrollView import ScrollView
from ..Utilities import Assets

class SpritesTab(DATTab):
	DAT_ID = DATID.sprites

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		scrollview = ScrollView(self)

		self.imageentry = IntegerVar(0, [0,998])
		self.imagedd = IntVar()
		self.visible = IntVar()
		self.unused = IntVar()
		self.selcircleentry = IntegerVar(0, [0,19], callback=lambda n: self.selcircle(n,1))
		self.selcircledd = IntVar()
		self.healthbar = IntegerVar(0, [0,255], callback=lambda n,i=0: self.updatehealth(n,i))
		self.boxes = IntegerVar(1, [1,84], callback=lambda n,i=1: self.updatehealth(n,i))
		self.vertpos = IntegerVar(0, [0,255])

		l = LabelFrame(scrollview.content_view, text='Sprite Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Image:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.imageentry, font=Font.fixed(), width=5).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.image_ddw = DropDown(f, self.imagedd, [], self.imageentry, width=30)
		self.image_ddw.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.images, self.imagedd.get())).pack(side=LEFT, padx=2)
		self.tip(f, 'Image', 'SpriteImage')
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Is Visible', variable=self.visible)
		self.tip(c, 'Is Visible', 'SpriteVisible')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Unused', variable=self.unused)
		self.tip(c, 'Unused', 'SpriteUnused')
		c.pack(side=LEFT)
		f.pack()
		f = Frame(s)
		Label(f, text='Sel. Circle:', width=12, anchor=E).pack(side=LEFT)
		self.selentry = Entry(f, textvariable=self.selcircleentry, font=Font.fixed(), width=5)
		self.selentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.seldd = DropDown(f, self.selcircledd, Assets.data_cache(Assets.DataReference.SelCircleSize), self.selcircle, width=30)
		self.seldd.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda: self.jump(DATID.images, self.selcircledd.get() + 561)).pack(side=LEFT, padx=2)
		self.tip(f, 'Selection Circle', 'SpriteSelCircle')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Health Bar:', width=12, anchor=E).pack(side=LEFT)
		self.hpentry = Entry(f, textvariable=self.healthbar, font=Font.fixed(), width=5)
		self.hpentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.hpboxes = Entry(f, textvariable=self.boxes, font=Font.fixed(), width=2)
		self.hpboxes.pack(side=LEFT, padx=2)
		Label(f, text='boxes').pack(side=LEFT)
		self.tip(f, 'Health Bar', 'SpriteHPBar')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vert. Position:', width=12, anchor=E).pack(side=LEFT)
		self.vertentry = Entry(f, textvariable=self.vertpos, font=Font.fixed(), width=5)
		self.vertentry.pack(side=LEFT, padx=2)
		self.tip(f, 'Vertical Position', 'SpriteCircleOff')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.previewing = None
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.data_context.settings.preview.sprite.get('show', False))

		x = Frame(scrollview.content_view)
		l = LabelFrame(x, text='Preview:')
		s = Frame(l)
		self.preview = Canvas(s, width=257, height=257, background='#000000')
		self.preview.pack()
		Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack()
		s.pack()
		l.pack(side=LEFT)
		x.pack(fill=X)
		scrollview.pack(fill=BOTH, expand=1)

		self.setup_used_by((
			DATRefs(DATID.flingy, lambda flingy: (
				DATRef('Sprite', flingy.sprite),
			)),
		))

		self.vertpos.trace('w', lambda *_: self.drawpreview())

	def updated_pointer_entries(self, ids):
		if DATID.flingy in ids and self.toplevel.dattabs.active == self:
			self.check_used_by_references()
		if DATID.images in ids:
			self.image_ddw.setentries(self.toplevel.data_context.images.names)

		if DATID.images in ids:
			self.imageentry.range[1] = self.toplevel.data_context.images.entry_count() - 1

	def selcircle(self, n, t=0):
		if t:
			self.selcircledd.set(n)
		else:
			self.selcircleentry.set(n)
		self.drawpreview()

	def updatehealth(self, num, type):
		if type:
			self.healthbar.check = False
			self.healthbar.set((num + 1) * 3)
		else:
			self.boxes.check = False
			self.boxes.set(max(1,(num - 1) / 3))
		self.drawpreview()

	def drawpreview(self, e=None):
		if self.previewing != self.id or (self.previewing != None and not self.showpreview.get()) or (self.previewing == None and self.showpreview.get()):
			self.preview.delete(ALL)
			if self.showpreview.get():
				i = int(self.selentry.get())
				if self.selentry['state'] == NORMAL:
					image_id = 561 + i
					frame = self.toplevel.data_context.get_image_frame(image_id)
					if frame:
						y = 130+int(self.vertpos.get())
						self.preview.create_image(130, y, image=frame[0])
						w = 3*int(self.boxes.get())
						hp = [130-(w/2),y+6+(frame[4]-frame[3])/2]
						self.preview.create_rectangle(hp[0], hp[1], hp[0]+w, hp[1]+4, fill='#000000')
						hp[0] += 1
						hp[1] += 1
						for _ in range(int(self.boxes.get())):
							self.preview.create_rectangle(hp[0], hp[1], hp[0]+1, hp[1]+2, outline='#008000', fill='#008000')
							hp[0] += 3
				image_id = self.toplevel.data_context.sprites.dat.get_entry(self.id).image
				frame = self.toplevel.data_context.get_image_frame(image_id)
				if frame:
					self.preview.create_image(130, 130, image=frame[0])
				self.previewing = i
			else:
				self.previewing = None

	def load_entry(self, entry):
		self.imageentry.set(entry.image)
		self.unused.set(entry.unused)
		self.visible.set(entry.is_visible)

		fields = (
			(entry.health_bar, self.healthbar, (self.hpentry, self.hpboxes)),

			(entry.selection_circle_image, self.selcircleentry, (self.selentry, self.seldd)),
			(entry.selection_circle_offset, self.vertpos, (self.vertentry,)),
		)
		for (value, variable, widgets) in fields:
			has_value = value != None
			variable.set(value if has_value else 0)
			state = NORMAL if has_value else DISABLED
			for widget in widgets:
				widget['state'] = state

		self.drawpreview()

	def save_entry(self, entry):
		if self.imageentry.get() != entry.image:
			entry.image = self.imageentry.get()
			self.edited = True
		if self.unused.get() != entry.unused:
			entry.unused = self.unused.get()
			self.edited = True
		if self.visible.get() != entry.is_visible:
			entry.is_visible = self.visible.get()
			self.edited = True
		
		if entry.health_bar != None and self.healthbar.get() != entry.health_bar:
			entry.health_bar = self.healthbar.get()
			self.edited = True
		if entry.selection_circle_image != None and self.selcircleentry.get() != entry.selection_circle_image:
			entry.selection_circle_image = self.selcircleentry.get()
			self.edited = True
		if entry.selection_circle_offset != None and self.vertpos.get() != entry.selection_circle_offset:
			entry.selection_circle_offset = self.vertpos.get()
			self.edited = True

		self.toplevel.data_context.settings.preview.sprite.show = not not self.showpreview.get()
