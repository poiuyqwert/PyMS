
from DATTab import DATTab

from ..FileFormats.GRP import rle_outline, OUTLINE_SELF

from ..Utilities.utils import couriernew
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.DropDown import DropDown
from ..Utilities.DataCache import DATA_CACHE

from Tkinter import *

class SpritesTab(DATTab):
	data = 'Sprites.txt'

	def __init__(self, parent, toplevel):
		DATTab.__init__(self, parent, toplevel)
		j = Frame(self)
		frame = Frame(j)

		self.imageentry = IntegerVar(0, [0,998])
		self.imagedd = IntVar()
		self.visible = IntVar()
		self.unknown = IntVar()
		self.selcircleentry = IntegerVar(0, [0,19], callback=lambda n: self.selcircle(n,1))
		self.selcircledd = IntVar()
		self.healthbar = IntegerVar(0, [0,255], callback=lambda n,i=0: self.updatehealth(n,i))
		self.boxes = IntegerVar(1, [1,84], callback=lambda n,i=1: self.updatehealth(n,i))
		self.vertpos = IntegerVar(0, [0,255])

		l = LabelFrame(frame, text='Sprite Properties:')
		s = Frame(l)
		f = Frame(s)
		Label(f, text='Image:', width=12, anchor=E).pack(side=LEFT)
		Entry(f, textvariable=self.imageentry, font=couriernew, width=3).pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		DropDown(f, self.imagedd, DATA_CACHE['Images.txt'], self.imageentry, width=30).pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Images',i=self.imagedd: self.jump(t,i)).pack(side=LEFT, padx=2)
		self.tip(f, 'Image', 'SpriteImage')
		f.pack(fill=X)
		f = Frame(s)
		c = Checkbutton(f, text='Is Visible', variable=self.visible)
		self.tip(c, 'Is Visible', 'SpriteVisible')
		c.pack(side=LEFT)
		c = Checkbutton(f, text='Unknown', variable=self.unknown)
		self.tip(c, 'Unknown', 'SpriteUnk1')
		c.pack(side=LEFT)
		f.pack()
		f = Frame(s)
		Label(f, text='Sel. Circle:', width=12, anchor=E).pack(side=LEFT)
		self.selentry = Entry(f, textvariable=self.selcircleentry, font=couriernew, width=3)
		self.selentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.seldd = DropDown(f, self.selcircledd, DATA_CACHE['SelCircleSize.txt'], self.selcircle, width=30)
		self.seldd.pack(side=LEFT, fill=X, expand=1, padx=2)
		Button(f, text='Jump ->', command=lambda t='Images',i=self.selcircledd,o=561: self.jump(t,i,o)).pack(side=LEFT, padx=2)
		self.tip(f, 'Selection Circle', 'SpriteSelCircle')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Health Bar:', width=12, anchor=E).pack(side=LEFT)
		self.hpentry = Entry(f, textvariable=self.healthbar, font=couriernew, width=3)
		self.hpentry.pack(side=LEFT, padx=2)
		Label(f, text='=').pack(side=LEFT)
		self.hpboxes = Entry(f, textvariable=self.boxes, font=couriernew, width=2)
		self.hpboxes.pack(side=LEFT, padx=2)
		Label(f, text='boxes').pack(side=LEFT)
		self.tip(f, 'Health Bar', 'SpriteHPBar')
		f.pack(fill=X)
		f = Frame(s)
		Label(f, text='Vert. Position:', width=12, anchor=E).pack(side=LEFT)
		self.vertentry = Entry(f, textvariable=self.vertpos, font=couriernew, width=3)
		self.vertentry.pack(side=LEFT, padx=2)
		self.tip(f, 'Vertical Position', 'SpriteCircleOff')
		f.pack(fill=X)
		s.pack(fill=BOTH, padx=5, pady=5)
		l.pack(fill=X)

		self.previewing = None
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.data_context.settings.preview.sprite.get('show', False))

		x = Frame(frame)
		l = LabelFrame(x, text='Preview:')
		s = Frame(l)
		self.preview = Canvas(s, width=257, height=257, background='#000000')
		self.preview.pack()
		Checkbutton(s, text='Show Preview', variable=self.showpreview, command=self.drawpreview).pack()
		s.pack()
		l.pack(side=LEFT)
		x.pack(fill=X)
		frame.pack(side=LEFT)
		j.pack(side=TOP, fill=X)

		self.usedby = [
			('flingy.dat', ['Sprite']),
		]
		self.setuplistbox()

		self.values = {
			'ImageFile':self.imageentry,
			'HealthBar':self.healthbar,
			'Unknown':self.unknown,
			'IsVisible':self.visible,
			'SelectionCircleImage':self.selcircleentry,
			'SelectionCircleOffset':self.vertpos,
		}

		self.vertpos.trace('w', lambda *_: self.drawpreview())

	def files_updated(self):
		self.dat = self.toplevel.sprites

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
					g = self.toplevel.images.get_value(image_id,'GRPFile')
					if g:
						f = self.toplevel.imagestbl.strings[g-1][:-1]
						image = self.toplevel.grp('Units','unit\\' + f, rle_outline, OUTLINE_SELF)
						if image:
							y = 130+int(self.vertpos.get())
							self.preview.create_image(130, y, image=image[0])
							w = 3*int(self.boxes.get())
							hp = [130-(w/2),y+6+(image[4]-image[3])/2]
							self.preview.create_rectangle(hp[0], hp[1], hp[0]+w, hp[1]+4, fill='#000000')
							hp[0] += 1
							hp[1] += 1
							for _ in range(int(self.boxes.get())):
								self.preview.create_rectangle(hp[0], hp[1], hp[0]+1, hp[1]+2, outline='#008000', fill='#008000')
								hp[0] += 3
				i = self.toplevel.sprites.get_value(self.id,'ImageFile')
				g = self.toplevel.images.get_value(i,'GRPFile')
				if g:
					f = self.toplevel.imagestbl.strings[g-1][:-1]
					if f.startswith('thingy\\tileset\\'):
						p = 'Terrain'
					else:
						p = 'Units'
						if self.toplevel.images.get_value(i, 'DrawFunction') == 9 and self.toplevel.images.get_value(i, 'Remapping') and self.toplevel.images.get_value(i, 'Remapping') < 4:
							p = ['o','b','g'][self.toplevel.images.get_value(i, 'Remapping')-1] + 'fire'
					sprite = self.toplevel.grp(p,'unit\\' + f)
					if sprite:
						self.preview.create_image(130, 130, image=sprite[0])
				self.previewing = i
			else:
				self.previewing = None

	def load_data(self, id=None):
		if not self.dat:
			return
		DATTab.load_data(self, id)
		check = [
			('HealthBar', [self.hpentry,self.hpboxes]),
			('SelectionCircleImage', [self.selentry,self.seldd]),
			('SelectionCircleOffset', [self.vertentry])
		]
		for l,ws in check:
			frmt = self.toplevel.sprites.format[self.toplevel.sprites.labels.index(l)][0]
			state = [NORMAL,DISABLED][self.id < frmt[0] or self.id >= frmt[1]]
			for w in ws:
				w['state'] = state
		self.drawpreview()
	def save_data(self):
		if not self.dat:
			return
		DATTab.save_data(self)
		self.toplevel.data_context.settings.preview.sprite.show = not not self.showpreview.get()
