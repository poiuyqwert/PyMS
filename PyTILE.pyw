from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs import GRP, Tilesets, TBL

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
from math import ceil,floor
import optparse, os, webbrowser, sys

VERSION = (1,3)
LONG_VERSION = 'v%s.%s' % VERSION
TILE_CACHE = {}

def tip(o, t, h):
	o.tooltip = Tooltip(o, t + ':\n  ' + h, mouse=True)
PAL = [0]

class MegaEditor(PyMSDialog):
	def __init__(self, parent, id):
		self.tileset = parent.tileset
		self.megatile = [id,0]
		self.gettile = parent.gettile
		self.select_file = parent.select_file
		self.dosave = False
		PyMSDialog.__init__(self, parent, 'MegaTile Editor [%s]' % id)

	def widgetize(self):
		self.minitile = IntegerVar(0,[0,len(self.tileset.vr4.images)-1],callback=lambda id: self.change(id))
		self.flipped = IntVar()
		self.heightdd = IntVar()
		self.walkable = IntVar()
		self.blockview = IntVar()
		self.ramp = IntVar()

		d = Frame(self)
		self.minitiles = Canvas(d, width=101, height=101, background='#000000')
		self.minitiles.pack(padx=2, pady=2)
		self.minitiles.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='border')
		e = Frame(d)
		Label(e, text='MiniTile:').pack(side=LEFT)
		Entry(e, textvariable=self.minitile, font=couriernew, width=5).pack(side=LEFT, padx=2)
		i = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))
		b = Button(e, image=i, width=20, height=20, command=self.choose)
		b.image = i
		b.pack(side=LEFT, padx=2)
		e.pack(fill=X)
		e = Frame(d)
		i = PhotoImage(file=os.path.join(BASE_DIR,'Images','edit.gif'))
		b = Button(e, image=i, width=20, height=20, command=self.editor)
		b.image = i
		b.pack(side=RIGHT, padx=2)
		Checkbutton(e, text='Flipped', variable=self.flipped).pack(side=RIGHT, padx=2)
		e.pack(fill=X, pady=3)
		d.pack(side=LEFT)
		d = Frame(self)
		c = Frame(d)
		DropDown(c, self.heightdd, ['Low','Med','High'], width=4).pack(side=LEFT, padx=5)
		c.pack(fill=X)
		for t,v in [('Walkable',self.walkable),('Block View',self.blockview),('Ramp?',self.ramp)]:
			c = Frame(d)
			Checkbutton(c, text=t, variable=v).pack(side=LEFT)
			c.pack(fill=X)
		Button(d, text='Apply to all', width=10, command=lambda i=0: self.applyallminiflags(i)).pack(padx=3)
		Button(d, text='Ok', width=10, command=self.ok).pack(side=BOTTOM, padx=3)
		d.pack(side=LEFT, fill=Y, pady=5)
		self.updateminis()
		self.miniload()
		self.minisel()

	def editor(self):
		MiniEditor(self, self.minitile)

	def updateminis(self):
		self.minitiles.images = []
		for n,m in enumerate(self.tileset.vx4.graphics[self.megatile[0]]):
			t = 'tile%s' % n
			self.minitiles.delete(t)
			self.minitiles.images.append(self.gettile(m))
			self.minitiles.create_image(15 + 25 * (n % 4), 15 + 25 * (n / 4), image=self.minitiles.images[-1], tags=t)
			self.minitiles.tag_bind(t, '<Button-1>', lambda e,n=n: self.miniload(n))
			self.minitiles.tag_bind(t, '<Double-Button-1>', lambda e,i=2: self.parent.choose(i))

	def minisel(self):
		x,y = 2 + 25 * (self.megatile[1] % 4),2 + 25 * (self.megatile[1] / 4)
		self.minitiles.coords('border', x, y, x + 25, y + 25)

	def miniload(self, n=None):
		if self.dosave:
			self.minisave()
		else:
			self.dosave = True
		if n == None:
			n = self.megatile[1]
		else:
			self.megatile[1] = n
		mega = self.megatile[0]
		g = self.tileset.vx4.graphics[mega][n]
		if self.minitile.get() != g[0]:
			self.minitile.check = False
			self.minitile.set(g[0])
		self.flipped.set(g[1])
		f = self.tileset.vf4.flags[mega][n]
		if f & 4:
			self.heightdd.set(2)
		elif f & 2:
			self.heightdd.set(1)
		else:
			self.heightdd.set(0)
		self.walkable.set(f & 1)
		self.blockview.set(f & 8 == 8)
		self.ramp.set(f & 16 == 16)
		self.minisel()

	def minisave(self):
		mega = self.megatile[0]
		self.tileset.vx4.graphics[mega][self.megatile[1]][1] = self.flipped.get()
		self.tileset.vf4.flags[mega][self.megatile[1]] = [0,2,4][self.heightdd.get()] + self.walkable.get() + 8 * self.blockview.get() + 16 * self.ramp.get()

	def change(self, id):
		self.tileset.vx4.graphics[self.megatile[0]][self.megatile[1]][0] = id
		self.updateminis()

	def applyallminiflags(self, i):
		pass

	def choose(self):
		TilePalette(self, 2, self.tileset.vx4.graphics[self.megatile[0]][self.megatile[1]][0])

	def ok(self):
		self.minisave()
		del TILE_CACHE[self.megatile[0]]
		try:
			self.parent.updategroup()
		except:
			self.parent.drawtiles()
		PyMSDialog.ok(self)

class Placeability(PyMSDialog):
	def __init__(self, parent, id=0):
		self.id = id
		self.canvass = []
		self.groups = []
		self.tileset = parent.tileset
		self.gettile = parent.gettile
		self.select_file = parent.select_file
		self.selecting = None
		self.width = 0
		PyMSDialog.__init__(self, parent, 'Doodad Placeability [%s]' % id, resizable=(False,False))

	def widgetize(self):
		f = Frame(self)
		ty = -1
		for n,g in enumerate(self.tileset.cv5.groups[1024:]):
			if g[9] == self.id and ty == -1:
				self.width,h,ty = g[10],g[11],g[11]-1
				if n + h > len(self.tileset.cv5.groups):
					h = len(self.tileset.cv5.groups) - n - 1
					ty = h-1
				for y in range(h):
					self.groups.append([])
					self.canvass.append(Canvas(f, width=self.width * 33-1, height=32))
					self.canvass[-1].grid(sticky=E+W, column=0, row=y*2, columnspan=self.width)
					self.canvass[-1].images = []
					for x in range(self.width):
						c = self.tileset.dddata.doodads[self.id][x + y * self.width]
						if not y:
							t = 'tile%s,%s' % (x,y)
							self.canvass[-1].images.append(Tilesets.megatile_to_photo(self.tileset, g[13][x]))
							self.canvass[-1].create_image(x * 33 + 18, 18, image=self.canvass[-1].images[-1], tags=t)
							self.canvass[-1].tag_bind(t, '<Double-Button-1>', lambda e,p=(x,y): self.select(p))
						self.groups[-1].append(IntegerVar(c,[0,len(self.tileset.cv5.groups)]))
						Entry(f, textvariable=self.groups[-1][-1], width=1, font=couriernew, bd=0).grid(sticky=E+W, column=x, row=y*2+1, padx=x%2)
			elif ty > 0:
				for x in range(self.width):
					c = self.tileset.dddata.doodads[self.id][x + (h-ty) * self.width]
					self.canvass[h-ty].images.append(Tilesets.megatile_to_photo(self.tileset, g[13][x]))
					self.canvass[h-ty].create_image(x * 33 + 18, 18, image=self.canvass[h-ty].images[-1])
					self.canvass[h-ty].tag_bind(t, '<Double-Button-1>', lambda e,p=(x,h-ty): self.select(p))
				ty -= 1
				if not ty:
					break
		f.pack(padx=5,pady=5)

	def select(self, p):
		self.selecting = p
		TilePalette(self, 0, self.groups[p[1]][p[0]].get())

	def change(self, t, id):
		self.groups[self.selecting[1]][self.selecting[0]].set(id)
		self.selecting = None

	def cancel(self, e=None):
		self.ok(self)

	def ok(self, e=None):
		self.tileset.dddata.doodads[self.id] = [0] * 256
		for y,l in enumerate(self.groups):
			for x,g in enumerate(l):
				self.tileset.dddata.doodads[self.id][x + y * self.width] = g.get()
		PyMSDialog.ok(self)

class MiniEditor(PyMSDialog):
	def __init__(self, parent, colors=[0,255], id=None):
		self.colors = colors
		self.click = None
		self.select = False
		self.id = id
		if id == None:
			PyMSDialog.__init__(self, parent, 'MiniTile Editor [%s]' % parent.tileset.vx4.graphics[parent.megatile[0]][parent.megatile[1]][0], resizable=(False,False))
		else:
			PyMSDialog.__init__(self, parent, 'MiniTile Editor [%s]' % id, resizable=(False,False))

	def widgetize(self):
		self.canvas = Canvas(self, width=202, height=114)
		self.canvas.pack(padx=3,pady=3)
		self.canvas.bind('<ButtonRelease-1>', self.release)
		self.canvas.bind('<Motion>', self.motion)
		if self.id == None:
			m = self.parent.tileset.vx4.graphics[self.parent.megatile[0]][self.parent.megatile[1]][0]
			d = self.parent.tileset.vr4.images[m]
		else:
			d = self.parent.tileset.vr4.images[self.id]
		self.indexs = []
		for y,p in enumerate(d):
			self.indexs.append(list(p))
			for x,i in enumerate(p):
				cx,cy,c = x * 10 + 2, y * 10 + 2, '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[i])
				t = 'tile%s,%s' % (x,y)
				self.canvas.create_rectangle(cx, cy, cx+10, cy+10, fill=c, outline=c, tags=t)
				self.canvas.tag_bind(t, '<Button-1>', lambda e,p=(x,y),c=0: self.color(p,c))
				self.canvas.tag_bind(t, '<Button-3>', lambda e,p=(x,y),c=1: self.color(p,c))
				cx,cy = x + 32,y + 90
				self.canvas.create_rectangle(cx, cy, cx+2, cy+2, fill=c, outline=c, tags='scale%s,%s' % (x,y))
		self.canvas.create_rectangle(90, 2, 202, 114, fill='#000000', outline='#000000')
		for n,i in enumerate(self.parent.tileset.wpe.palette):
			cx,cy,c = (n % 16) * 7 + 91, (n / 16) * 7 + 3, '#%02x%02x%02x' % tuple(i)
			t = 'pal%s' % n
			self.canvas.create_rectangle(cx, cy, cx+5, cy+5, fill=c, outline=c, tags=t)
			c = '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[self.colors[1]])
			self.canvas.tag_bind(t, '<Button-1>', lambda e,p=n,c=0: self.pencolor(p,c))
			self.canvas.tag_bind(t, '<Button-3>', lambda e,p=n,c=1: self.pencolor(p,c))
		self.canvas.create_rectangle(10, 98, 26, 114, fill=c, outline=c, tags='bg')
		c = '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[self.colors[0]])
		self.canvas.create_rectangle(2, 90, 18, 106, fill=c, outline=c, tags='fg')
		self.eyedropper = PhotoImage(file=os.path.join(BASE_DIR,'Images','eyedropper.gif'))
		self.canvas.create_image(56, 101, image=self.eyedropper, tags='eyedropper')
		self.canvas.tag_bind('eyedropper', '<Button-1>', self.dropper)
		b = Frame(self)
		ok = Button(b, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=2)
		Button(b, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		b.pack(pady=3)
		return ok

	def dropper(self, e=None):
		if self.select:
			self.canvas.delete('dropbd')
		else:
			self.canvas.create_rectangle(45, 90, 66, 111, outline='#000000', tags='dropbd')
		self.select = not self.select

	def release(self, e):
		self.click = None

	def motion(self, e):
		o = self.canvas.find_overlapping(e.x,e.y,e.x,e.y)
		if self.click != None and o and len(o) == 1:
			t = self.canvas.gettags(o[0])
			if t and len(t) == 1 and t[0].startswith('tile'):
				self.color(tuple(int(n) for n in t[0][4:].split(',')),self.click)

	def color(self, p, c):
		if self.select:
			self.colors[c] = self.indexs[p[1]][p[0]]
			r = '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[self.colors[c]])
			self.canvas.itemconfig(['fg','bg'][c], fill=r, outline=r)
			self.dropper()
		else:
			self.indexs[p[1]][p[0]] = self.colors[c]
			r = '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[self.colors[c]])
			self.canvas.itemconfig('tile%s,%s' % p, fill=r, outline=r)
			self.canvas.itemconfig('scale%s,%s' % p, fill=r, outline=r)
			self.click = c

	def pencolor(self, p, c):
		self.colors[c] = p
		r = '#%02x%02x%02x' % tuple(self.parent.tileset.wpe.palette[p])
		self.canvas.itemconfig(['fg','bg'][c], fill=r, outline=r)

	def cancel(self):
		PyMSDialog.cancel(self)

	def ok(self):
		m = self.parent.tileset.vx4.graphics[self.parent.megatile[0]][self.parent.megatile[1]][0]
		self.parent.tileset.vr4.images[m] = self.indexs
		if self.id == None:
			self.parent.updategroup()
		else:
			del TILE_CACHE[-self.id]
			self.parent.drawtiles()
		PyMSDialog.ok(self)

class TilePalette(PyMSDialog):
	def __init__(self, parent, type=0, sel=0):
		PAL[0] += 1
		self.ttext = '%s Palette [%%s]' % ['Group','MegaTile','MiniTile Image'][type]
		self.type = type
		self.sel = sel
		self.top = 0
		self.lasttop = -1
		self.tileset = parent.tileset
		self.megatile = parent.megatile
		self.gettile = parent.gettile
		self.select_file = parent.select_file
		PyMSDialog.__init__(self, parent, self.ttext % self.sel, resizable=(False,False))

	def update_top(self):
		if self.type == 0:
			self.top = max(min(self.sel,len(self.parent.tileset.cv5.groups)-8),0)
		elif self.type == 1:
			self.top = max(min(int(floor(self.sel / 16.0)),int(ceil(len(self.parent.tileset.vf4.flags) / 16.0) - 8)),0)
		else:
			self.top = max(min(int(floor(self.sel / 16.0)),int(ceil(len(self.parent.tileset.vr4.images) / 16.0) - 8)),0)

	def drawsel(self):
		if self.type == 0 and self.top <= self.sel <= self.top+8:
			y = 2 + 33 * (self.sel - self.top)
			self.canvas.coords('border', 2, y, 515, y + 33)
			return
		elif self.type == 1 and self.top*16 <= self.sel <= (self.top+8)*16:
			x,y = 2 + 33 * ((self.sel - self.top*16) % 16),2 + 33 * ((self.sel - self.top*16) / 16)
			self.canvas.coords('border', x, y, x + 33, y + 33)
			return
		elif self.type == 2 and self.top*16 <= self.sel <= (self.top+8)*16:
			x,y = 2 + 25 * ((self.sel - self.top*16) % 16),2 + 25 * ((self.sel - self.top*16) / 16)
			self.canvas.coords('border', x, y, x + 25, y + 25)
			return
		self.canvas.coords('border', 0, 0, 0, 0)

	def setsel(self, g):
		self.sel = g
		self.title(self.ttext % g)
		self.drawsel()

	def drawtiles(self):
		if self.top != self.lasttop:
			self.lasttop = self.top
			self.canvas.delete(ALL)
			self.canvas.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='border')
			self.canvas.images = []
			if self.type == 0:
				for q,g in enumerate(range(self.top,min(len(self.tileset.cv5.groups),self.top+8))):
					for n,m in enumerate(self.tileset.cv5.groups[g][13]):
						t = 'tile%s' % (n+16*q)
						self.canvas.images.append(self.gettile(m))
						self.canvas.create_image(19 + 32 * n, 19 + 33 * q, image=self.canvas.images[-1], tags=t)
						self.canvas.tag_bind(t, '<Button-1>', lambda e,g=g: self.setsel(g))
						self.canvas.tag_bind(t, '<Double-Button-1>', lambda e,g=g: self.choose(g))
			elif self.type == 1:
				for n,m in enumerate(range(self.top*16,min(len(self.tileset.vx4.graphics),(self.top+8)*16))):
					t = 'tile%s' % n
					self.canvas.images.append(self.gettile(m))
					self.canvas.create_image(19 + 33 * (n % 16), 19 + 33 * (n / 16), image=self.canvas.images[-1], tags=t)
					self.canvas.tag_bind(t, '<Button-1>', lambda e,g=m: self.setsel(g))
					self.canvas.tag_bind(t, '<Double-Button-1>', lambda e,g=m: self.choose(g))
			elif self.type == 2:
				for n,m in enumerate(range(self.top*16,min(len(self.tileset.vr4.images),(self.top+8)*16))):
					t = 'tile%s' % n
					self.canvas.images.append(self.gettile((m,0)))
					self.canvas.create_image(15 + 25 * (n % 16), 15 + 25 * (n / 16), image=self.canvas.images[-1], tags=t)
					self.canvas.tag_bind(t, '<Button-1>', lambda e,g=m: self.setsel(g))
					self.canvas.tag_bind(t, '<Double-Button-1>', lambda e,g=m: self.choose(g))
			self.drawsel()

	def widgetize(self):
		self.update_top()
		buttons = [
			('add', self.add, 'Add (Insert)', NORMAL, 'Insert'),
			('remove', self.remove, 'Remove (Delete)', DISABLED, 'Delete'),
			10,
			('export', self.export, 'Export Group (Ctrl+E)', NORMAL, 'Ctrl+E'),
			('import', self.iimport, 'Import Groups (Ctrl+I)', NORMAL, 'Ctrl+I'),
		]
		if self.type:
			buttons.extend([10,('edit', self.edit, 'Edit %sTile (Enter)' % ['Mega','Mini'][self.type-1], [DISABLED,NORMAL][win_reg], 'Return')])
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(fill=X)
		w = [32,33,25][self.type]
		h = [w,33][not self.type]
		c = Frame(self)
		self.canvas = Canvas(c, width=1 + w * 16 + 1 * (not self.type), height=1 + h * 8, background='#000000')
		self.canvas.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='border')
		self.canvas.pack(side=LEFT)
		self.scroll = Scrollbar(c, command=self.scrolling)
		self.updatescroll()
		self.scroll.pack(side=LEFT, fill=Y, expand=1)
		c.pack()
		self.drawtiles()
		self.bind('<MouseWheel>', lambda e: self.scrolling('scroll',-1 if e.delta > 0 else 1,'units'))
		self.bind('<Down>', lambda e: self.scrolling('scroll',1,'units'))
		self.bind('<Up>', lambda e: self.scrolling('scroll',-1,'units'))
		self.bind('<Next>', lambda e: self.scrolling('scroll',1,'page'))
		self.bind('<Prior>', lambda e: self.scrolling('scroll',-1,'page'))

	def add(self):
		if self.type == 0:
			self.tileset.cv5.groups.append([0] * 13 + [[0] * 16])
			self.setsel(len(self.tileset.cv5.groups)-1)
			self.top = max(min(self.sel,len(self.tileset.cv5.groups)-8),0)
		elif self.type == 1:
			self.tileset.vf4.flags.append([0]*32)
			self.tileset.vx4.graphics.append([[0,0] for _ in range(16)])
			self.setsel(len(self.tileset.vf4.flags)-1)
			self.top = max(min(int(ceil(self.sel / 16.0)),int(ceil(len(self.tileset.vf4.flags) / 16.0) - 8)),0)
		else:
			self.tileset.vr4.images.append([[0] * 8 for _ in range(8)] )
			self.setsel(len(self.tileset.vr4.images)-1)
			self.top = max(min(int(ceil(self.sel / 16.0)),int(ceil(len(self.tileset.vr4.images) / 16.0) - 8)),0)
		self.updatescroll()
		self.drawtiles()
		self.parent.update_ranges()

	def export(self):
		b = self.select_file('Export Group', False, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')], self)
		if not b:
			return
		s = None
		if self.type < 2:
			s = self.select_file('Export Group Settings (Cancel to export only the BMP)', False, '.txt', [('Text File','*.txt'),('All Files','*')], self)
		self.tileset.decompile(b,self.type,self.sel,s)

	def iimport(self):
		b = self.select_file('Import Group', True, '.bmp', [('256 Color BMP','*.bmp'),('All Files','*')], self)
		if not b:
			return
		s = None
		if self.type < 2:
			s = self.select_file('Import Group Settings (Cancel to import only the BMP)', True, '.txt', [('Text File','*.txt'),('All Files','*')], self)
		sel = self.sel
		if self.type == 0:
			start_size = len(self.parent.tileset.cv5.groups)
		elif self.type == 1:
			start_size = len(self.parent.tileset.vf4.flags)
		else:
			start_size = len(self.parent.tileset.vr4.images)
		try:
			self.tileset.interpret(b,self.type,s)
		except PyMSError, e:
			ErrorDialog(self, e)
		else:
			if self.type == 0:
				end_size = len(self.parent.tileset.cv5.groups)
			elif self.type == 1:
				end_size = len(self.parent.tileset.vf4.flags)
			else:
				end_size = len(self.parent.tileset.vr4.images)
			if end_size > start_size:
				self.sel = start_size
				self.update_top()
				self.updatescroll()
			self.drawtiles()
			self.parent.update_ranges()

	def remove(self):
		pass

	def edit(self, e=None):
		if self.type == 1:
			MegaEditor(self, id=self.sel)
		elif self.type == 2:
			MiniEditor(self, id=self.sel)

	def updatescroll(self):
		if self.type == 0:
			groups = float(len(self.tileset.cv5.groups)-8)
		elif self.type == 1:
			groups = float(ceil(len(self.tileset.vx4.graphics) / 16.0) - 8)
		elif self.type == 2:
			groups = float(ceil(len(self.tileset.vr4.images) / 16.0) - 8)
		if groups <= 8:
			self.scroll.set(0,1)
		else:
			x = (1-8/groups)*(self.top / groups)
			self.scroll.set(x,x+8/groups)

	def scrolling(self, t, p, e=None):
		a = {'page':8,'units':1}
		if self.type == 0:
			groups = len(self.tileset.cv5.groups)-8
		elif self.type == 1:
			groups = int(ceil(len(self.tileset.vx4.graphics) / 16.0) - 8)
		elif self.type == 2:
			groups = int(ceil(len(self.tileset.vr4.images) / 16.0) - 8)
		p = min(1,float(p) / (1-8/float(groups)))
		if t == 'moveto':
			self.top = int(groups * float(p))
		elif t == 'scroll':
			self.top = min(groups,max(0,self.top + int(p) * a[e]))
		self.updatescroll()
		self.drawtiles()
		return "break"

	def choose(self, id):
		self.parent.change(self.type, id)
		self.ok()

	def ok(self):
		if hasattr(self.parent,'selecting'):
			self.parent.selecting = None
		else:
			try:
				self.parent.updategroup()
			except:
				try:
					self.parent.updateminis()
				except:
					pass
		PAL[0] -= 1
		if not PAL[0]:
			TILE_CACHE = {}
		PyMSDialog.ok(self)

class PyTILE(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyTILE')

		#Window
		Tk.__init__(self)
		self.title('PyTILE %s' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR,'Images','PyTILE.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyTILE.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyTILE')
		self.resizable(False, False)

		self.stat_txt = TBL.TBL()
		self.stat_txt_file = ''
		filen = self.settings.get('stat_txt',os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez', 'stat_txt.tbl'))
		while True:
			try:
				self.stat_txt.load_file(filen)
				break
			except:
				filen = self.select_file('Open stat_txt.tbl', True, '.tbl', [('StarCraft TBL files','*.tbl'),('All Files','*')])
				if not filen:
					sys.exit()

		self.dosave = [False,False]
		self.tileset = None
		self.file = None
		self.edited = False
		self.group = [0,0]
		self.megatile = None

		#Toolbar
		buttons = [
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('register', self.register, 'Set as default *.cv5 editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyTILE', NORMAL, ''),
			10,
			('exit', self.exit, 'Exit (Alt+F4)', NORMAL, 'Alt+F4'),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
				a = btn[4]
				if a:
					if not a.startswith('F'):
						self.bind('<%s%s>' % (a[:-1].replace('Ctrl','Control').replace('+','-'), a[-1].lower()), btn[1])
					else:
						self.bind('<%s>' % a, btn[1])
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, padx=1, pady=1, fill=X)

		self.disable = []
		self.minitile = IntegerVar(0,[0,32767],callback=lambda id: self.change(2, id))
		self.flipped = IntVar()
		self.heightdd = IntVar()
		self.walkable = IntVar()
		self.blockview = IntVar()
		self.ramp = IntVar()

		self.megatilee = IntegerVar(0,[0,4095],callback=lambda id: self.change(1, id))
		self.index = IntegerVar(0,[0,65535])
		self.flags = IntegerVar(0,[0,15])
		self.groundheight = IntegerVar(0,[0,15])
		self.buildable = IntegerVar(0,[0,15])
		self.buildable2 = IntegerVar(0,[0,15])
		self.edgeleft = IntegerVar(0,[0,65535])
		self.edgeright = IntegerVar(0,[0,65535])
		self.edgeup = IntegerVar(0,[0,65535])
		self.edgedown = IntegerVar(0,[0,65535])
		self.hasup = IntegerVar(0,[0,65535])
		self.hasdown = IntegerVar(0,[0,65535])
		self.unknown9 = IntegerVar(0,[0,65535])
		self.unknown11 = IntegerVar(0,[0,65535])
		self.doodad = False

		self.findimage = PhotoImage(file=os.path.join(BASE_DIR,'Images','find.gif'))

		self.groupid = LabelFrame(self, text='MegaTile Group')
		g = Frame(self.groupid)
		c = Frame(g)
		self.megatiles = Canvas(c, width=529, height=34, background='#000000')
		self.megatiles.pack()
		self.scroll = Scrollbar(c, orient=HORIZONTAL, command=self.scrolling)
		self.scroll.set(0,1)
		self.scroll.pack(fill=X, expand=1, padx=2)
		c.pack(side=LEFT,padx=2)
		self.megatiles.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='border')
		self.disable.append(Button(g, image=self.findimage, width=20, height=20, command=lambda i=0: self.choose(i), state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=2)
		g.pack(padx=5)
		f = Frame(self.groupid)
		left = Frame(f)
		l = LabelFrame(left, text='MiniTiles')
		d = Frame(l)
		self.minitiles = Canvas(d, width=101, height=101, background='#000000')
		self.minitiles.pack(padx=2, pady=2)
		self.minitiles.create_rectangle(0, 0, 0, 0, outline='#FFFFFF', tags='border')
		e = Frame(d)
		Label(e, text='MiniTile:').pack(side=LEFT)
		self.disable.append(Entry(e, textvariable=self.minitile, font=couriernew, width=5, state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=2)
		self.disable.append(Button(e, image=self.findimage, width=20, height=20, command=lambda i=2: self.choose(i), state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=2)
		e.pack(fill=X)
		e = Frame(d)
		i = PhotoImage(file=os.path.join(BASE_DIR,'Images','edit.gif'))
		self.disable.append(Button(e, image=i, width=20, height=20, command=self.editor, state=DISABLED))
		self.disable[-1].image = i
		self.disable[-1].pack(side=RIGHT, padx=2)
		self.disable.append(Checkbutton(e, text='Flipped', variable=self.flipped, state=DISABLED))
		self.disable[-1].pack(side=RIGHT, padx=2)
		e.pack(fill=X, pady=3)
		d.pack(side=LEFT)
		d = Frame(l)
		c = Frame(d)
		self.disable.append(DropDown(c, self.heightdd, ['Low','Med','High'], width=4, state=DISABLED))
		self.disable[-1].pack(side=LEFT, padx=5)
		c.pack(fill=X)
		for t,v in [('Walkable',self.walkable),('Block View',self.blockview),('Ramp?',self.ramp)]:
			c = Frame(d)
			self.disable.append(Checkbutton(c, text=t, variable=v, state=DISABLED))
			self.disable[-1].pack(side=LEFT)
			c.pack(fill=X)
		a = LabelFrame(d, text='Apply to all')
		self.disable.append(Button(a, text='MiniTiles', width=10, command=lambda i=0: self.applyallminiflags(i), state=DISABLED))
		self.disable[-1].pack(padx=3, pady=2)
		self.disable.append(Button(a, text='MegaTiles', width=10, command=lambda i=1: self.applyallminiflags(i), state=DISABLED))
		self.disable[-1].pack(padx=3, pady=2)
		a.pack(side=BOTTOM, padx=2, pady=2)
		d.pack(side=LEFT, fill=Y)
		l.pack(padx=5, pady=5)
		left.pack(side=LEFT)
		right = Frame(f)
		self.tiles = Frame(right)
		data = [
			[
				('Index',self.index,5,'Group Index? Seems to always be 1 for doodads. Not completely understood'),
				('MegaTile',self.megatilee,4,'MegaTile ID for selected tile in the group. Either input a value,\n  or hit the find button to browse for a MegaTile.')
			],
			[
				('Flags',self.flags,2,'Unknown property:\n    0 = ?\n    1 = Edge?\n    4 = Cliff?'),
				('Ground Height',self.groundheight,2,'Shows ground height. Does not seem to be completely valid.\n  May be used by StarEdit/deprecated?'),
				('Edge Left?',self.edgeleft,5,'Unknown. Seems to be related to surrounding tiles & ISOM. (Left?)'),
				('Edge Right?',self.edgeright,5,'Unknown. Seems to be related to surrounding tiles & ISOM. (Right?)'),
				('Edge Up?',self.edgeup,5,'Unknown. Seems to be related to surrounding tiles & ISOM. (Up?)'),
				('Edge Down?',self.edgedown,5,'Unknown. Seems to be related to surrounding tiles & ISOM. (Down?)')
			],
			[
				('Buildable',self.buildable,2,'Sets the default buildable property:\n    0 = Buildable\n    4 = Creep\n    8 = Unbuildable'),
				('Buildable 2',self.buildable2,2,'Buildable Flag for Beacons/Start Location:\n    0 = Default\n    8 = Buildable'),
				('Has Up',self.hasup,5,'Edge piece has rows above it. (Recently noticed; not fully understood.)\n    1 = Basic edge piece.\n    2 = Right edge piece.\n    3 = Left edge piece.'),
				('Has Down',self.hasdown,5,'Edge piece has rows below it. (Recently noticed; not fully understood.)\n    1 = Basic edge piece.\n    2 = Right edge piece.\n    3 = Left edge piece.'),
				('Unknown 9',self.unknown9,5,'Unknown'),
				('Unknown 11',self.unknown11,5,'Unknown')
			],
		]
		for c,a in enumerate(data):
			for r,row in enumerate(a):
				t,v,w,desc = row
				l = Label(self.tiles, text=t + ':', anchor=E)
				if t == 'MegaTile':
					l.grid(sticky=W+E, column=c*2, row=5)
					tip(l, t, desc)
					e = Frame(self.tiles)
					self.disable.append(Entry(e, textvariable=v, font=couriernew, width=w, state=DISABLED))
					self.disable[-1].pack(side=LEFT)
					self.disable.append(Button(e, image=self.findimage, width=20, height=20, command=lambda i=1: self.choose(i), state=DISABLED))
					self.disable[-1].pack(side=LEFT, padx=2)
					e.grid(sticky=W, column=c*2+1, row=5)
					tip(e, t, desc)
				else:
					l.grid(sticky=W+E, column=c*2, row=r)
					tip(l, t, desc)
					self.disable.append(Entry(self.tiles, textvariable=v, font=couriernew, width=w, state=DISABLED))
					self.disable[-1].grid(sticky=W, column=c*2+1, row=r)
					tip(self.disable[-1], t, desc)
		self.tiles.pack(side=TOP)
		self.doodads = Frame(right)
		data = [
			[
				('Index',self.index,5,'Group Index? Seems to always be 1 for doodads. Not completely understood'),
				('MegaTile',self.megatilee,4,'MegaTile ID for selected tile in the group. Either input a value,\n  or hit the find button to browse for a MegaTile.')
			],
			[
				('Unknown 1',self.flags,2,'Unknown:\n    0 = ?\n    1 = ?'),
				('Ground Height',self.groundheight,2,'Shows ground height. Does not seem to be completely valid.\n  May be used by StarEdit/deprecated?'),
				(None,self.edgeleft,None,'Doodad group string from stat_txt.tbl'),
				('Doodad #',self.edgeright,5,'Doodad ID used used for dddata.bi'),
				('Doodad Width',self.edgeup,5,'Total width of the doodad in MegaTiles'),
				('Doodad Height',self.edgedown,5,'Total height of the doodad in MegaTiles')
			],
			[
				('Buildable',self.buildable,2,'Sets the default buildable property:\n    0 = Buildable\n    4 = Creep\n    8 = Unbuildable'),
				('Has Overlay',self.buildable2,2,'Flag that determins if a doodad has a sprite overlay:\n    0 = None\n    1 = Sprites.dat Reference\n    2 = Units.dat Reference\n    4 = Overlay is Flipped'),
				('Overlay ID',self.hasup,5,'Sprite or Unit ID (depending on the Has Overlay flag) of the doodad overlay.'),
				('Unknown 6',self.hasdown,5,'Unknown'),
				('Unknown 8',self.unknown9,5,'Unknown'),
				('Unknown 12',self.unknown11,5,'Unknown')
			],
		]
		for c,a in enumerate(data):
			for r,row in enumerate(a):
				t,v,w,desc = row
				if t == None:
					l = Label(self.doodads, text='Group:', anchor=E)
					l.grid(sticky=W+E, column=0, row=2)
					tip(l, 'Doodad Group', desc)
					self.doodaddd = DropDown(self.doodads, v, [TBL.decompile_string(s) for s in self.stat_txt.strings])
					self.doodaddd.grid(sticky=W+E, column=1, row=r, columnspan=3)
				else:
					l = Label(self.doodads, text=t + ':', anchor=E)
					if t == 'MegaTile':
						l.grid(sticky=W+E, column=c*2, row=5)
						tip(l, t, desc)
						e = Frame(self.doodads)
						self.disable.append(Entry(e, textvariable=v, font=couriernew, width=w, state=DISABLED))
						self.disable[-1].pack(side=LEFT)
						self.disable.append(Button(e, image=self.findimage, width=20, height=20, command=lambda i=1: self.choose(i), state=DISABLED))
						self.disable[-1].pack(side=LEFT, padx=2)
						e.grid(sticky=W, column=c*2+1, row=5)
					else:
						l.grid(sticky=W+E, column=c*2, row=r)
						tip(l, t, desc)
						self.disable.append(Entry(self.doodads, textvariable=v, font=couriernew, width=w, state=DISABLED))
						self.disable[-1].grid(sticky=W, column=c*2+1, row=r)
						tip(self.disable[-1], t, desc)
		self.disable.append(Button(self.doodads, text='Placeability', command=self.placeability))
		self.disable[-1].grid(sticky=W+E, column=2, row=7, pady=5)
		right.pack(side=LEFT, fill=Y, pady=8)
		f.pack(fill=X)
		self.groupid.pack(padx=5, pady=5)

		#Statusbar
		self.status = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, width=75, anchor=W).pack(side=LEFT, padx=1)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load a Tileset.')
		statusbar.pack(side=BOTTOM, fill=X)

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self,))

	def unsaved(self):
		if self.tileset and self.edited:
			file = self.file
			if not file:
				file = 'Unnamed.cv5'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % file, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					self.saveas()

	def select_file(self, title, open=True, ext='.cv5', filetypes=[('Complete Tileset','*.cv5'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](title=title, defaultextension=ext, filetypes=filetypes, initialdir=path, parent=parent)
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def action_states(self):
		file = [NORMAL,DISABLED][not self.tileset]
		for btn in ['save','saveas','close']:
			self.buttons[btn]['state'] = file
		for w in self.disable:
			w['state'] = file

	def gettile(self, id, cache=False):
		to_photo = [Tilesets.megatile_to_photo,Tilesets.minitile_to_photo][isinstance(id,tuple) or isinstance(id,list)]
		if cache:
			if not id in TILE_CACHE:
				TILE_CACHE[id] = to_photo(self.tileset, id)
			return TILE_CACHE[id]
		return to_photo(self.tileset, id)

	def applyallminiflags(self, i):
		megas = self.tileset.cv5.groups[self.group[0]][13]
		if i == 0:
			megas = [megas[self.group[1]]]
		for mega in megas:
			for n in range(16):
				self.tileset.vf4.flags[mega][n] = self.heightdd.get() * 2 + self.walkable.get() + 8 * self.blockview.get() + 16 * self.ramp.get()

	def groupsel(self):
		x = 2 + 33 * self.group[1]
		self.megatiles.coords('border', x, 2, x + 33, 35)

	def updategroup(self):
		d = ['',' - Doodad'][self.group[0] >= 1024]
		self.groupid['text'] = 'MegaTile Group [%s%s]' % (self.group[0],d)
		self.megatiles.images = []
		for n,m in enumerate(self.tileset.cv5.groups[self.group[0]][13]):
			t = 'tile%s' % n
			self.megatiles.delete(t)
			self.megatiles.images.append(self.gettile(m))
			self.megatiles.create_image(19 + 33 * n, 19, image=self.megatiles.images[-1], tags=t)
			self.megatiles.tag_bind(t, '<Button-1>', lambda e,n=n: self.megaload(n))
			self.megatiles.tag_bind(t, '<Double-Button-1>', lambda e,i=1: self.choose(i))
		if self.megatile == None:
			self.megatile = [self.tileset.cv5.groups[self.group[0]][13][0],0]
		self.megaload()

	def megaload(self, n=None):
		if self.dosave[0]:
			self.megasave()
		else:
			self.dosave[0] = True
		if self.dosave[1]:
			self.minisave()
			self.dosave[1] = False
		if n == None:
			n = self.group[1]
		else:
			self.group[1] = n
		group = self.tileset.cv5.groups[self.group[0]]
		mega = group[13][n]
		self.megatile[0] = mega
		if self.megatilee.get() != mega:
			self.megatilee.check = False
			self.megatilee.set(mega)
		self.index.set(group[0])
		if self.group[0] >= 1024:
			if not self.doodad:
				self.tiles.pack_forget()
				self.doodads.pack(side=TOP)
				self.doodad = True
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.hasup,self.hasdown,self.edgeleft,self.unknown9,self.edgeright,self.edgeup,self.edgedown,self.unknown11]
		else:
			if self.doodad:
				self.doodads.pack_forget()
				self.tiles.pack(side=TOP)
				self.doodad = False
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]
		for n,v in enumerate(o):
			if self.group[0] >= 1024 and n == 6:
				v.set(group[n+1]-1)
			else:
				v.set(group[n+1])
		self.groupsel()
		self.updateminitiles()
		self.miniload()

	def megasave(self):
		group = self.tileset.cv5.groups[self.group[0]]
		group[0] = self.index.get()
		if self.group[0] >= 1024:
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.hasup,self.hasdown,self.edgeleft,self.unknown9,self.edgeright,self.edgeup,self.edgedown,self.unknown11]
		else:
			o = [self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]
		for n,v in enumerate(o):
			if self.group[0] >= 1024 and n == 6:
				group[n+1] = v.get()+1
			else:
				group[n+1] = v.get()
		self.edited = True
		self.editstatus['state'] = NORMAL

	def minisel(self):
		x,y = 2 + 25 * (self.megatile[1] % 4),2 + 25 * (self.megatile[1] / 4)
		self.minitiles.coords('border', x, y, x + 25, y + 25)

	def updateminitiles(self):
		self.minitiles.images = []
		for n,m in enumerate(self.tileset.vx4.graphics[self.megatile[0]]):
			t = 'tile%s' % n
			self.minitiles.delete(t)
			self.minitiles.images.append(self.gettile(m))
			self.minitiles.create_image(15 + 25 * (n % 4), 15 + 25 * (n / 4), image=self.minitiles.images[-1], tags=t)
			self.minitiles.tag_bind(t, '<Button-1>', lambda e,n=n: self.miniload(n))
			self.minitiles.tag_bind(t, '<Double-Button-1>', lambda e,i=2: self.choose(i))

	def miniload(self, n=None):
		if self.dosave[1]:
			self.minisave()
		else:
			self.dosave[1] = True
		if n == None:
			n = self.megatile[1]
		else:
			self.megatile[1] = n
		mega = self.tileset.cv5.groups[self.group[0]][13][self.group[1]]
		g = self.tileset.vx4.graphics[mega][n]
		if self.minitile.get() != g[0]:
			self.minitile.check = False
			self.minitile.set(g[0])
		self.flipped.set(g[1])
		f = self.tileset.vf4.flags[mega][n]
		if f & 4:
			self.heightdd.set(2)
		elif f & 2:
			self.heightdd.set(1)
		else:
			self.heightdd.set(0)
		self.walkable.set(f & 1)
		self.blockview.set(f & 8 == 8)
		self.ramp.set(f & 16 == 16)
		self.minisel()

	def minisave(self):
		mega = self.tileset.cv5.groups[self.group[0]][13][self.group[1]]
		self.tileset.vx4.graphics[mega][self.megatile[1]][1] = self.flipped.get()
		self.tileset.vf4.flags[mega][self.megatile[1]] = [0,2,4][self.heightdd.get()] + self.walkable.get() + 8 * self.blockview.get() + 16 * self.ramp.get()
		self.edited = True
		self.editstatus['state'] = NORMAL

	def choose(self, i):
		self.minisave()
		self.megasave()
		TilePalette(self, i, [
			self.group[0],
			self.tileset.cv5.groups[self.group[0]][13][self.group[1]],
			self.tileset.vx4.graphics[self.tileset.cv5.groups[self.group[0]][13][self.group[1]]][self.megatile[1]][0]
		][i])

	def updatescroll(self):
		groups = 0
		if self.tileset:
			groups = float(len(self.tileset.cv5.groups)-1)
		if groups <= 1:
			self.scroll.set(0,1)
		else:
			x = (1-8/groups)*(self.group[0] / groups)
			self.scroll.set(x,x+(8/groups))

	def scrolling(self, t, p, e=None):
		if self.dosave[0]:
			self.megasave()
			self.dosave[0] = False
		if self.dosave[1]:
			self.minisave()
			self.dosave[1] = False
		a = {'page':8,'units':1}
		groups = len(self.tileset.cv5.groups)-1
		p = min(100,float(p) / (1-8/float(groups)))
		if t == 'moveto':
			self.group[0] = int(groups * float(p))
		elif t == 'scroll':
			self.group[0] = min(groups,max(0,self.group[0] + int(p) * a[e]))
		self.updatescroll()
		self.updategroup()

	def change(self, type, id):
		if not self.tileset:
			return
		if type == 0:
			self.megasave()
			self.dosave[0] = False
			self.group[0] = id
			self.updategroup()
		elif type == 1:
			self.tileset.cv5.groups[self.group[0]][13][self.group[1]] = id
			self.updategroup()
		elif type == 2:
			self.tileset.vx4.graphics[self.tileset.cv5.groups[self.group[0]][13][self.group[1]]][self.megatile[1]][0] = id
			self.updategroup()
		self.edited = True
		self.editstatus['state'] = NORMAL
		self.updatescroll()

	def placeability(self):
		Placeability(self, self.edgeright.get())

	def editor(self):
		MiniEditor(self)

	def update_ranges(self):
		self.megatilee.setrange([0,len(self.tileset.vf4.flags)-1])
		self.minitile.setrange([0,len(self.tileset.vr4.images)-1])

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open Complete Tileset')
				if not file:
					return
			tileset = Tilesets.Tileset()
			try:
				tileset.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.tileset = tileset
			self.file = file
			self.edited = False
			self.status.set('Load successful!')
			self.editstatus['state'] = DISABLED
			self.action_states()
			self.update_ranges()
			self.dosave = [False,False]
			self.group = [0,0]
			self.megatile = None
			self.updategroup()
			self.updatescroll()

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.tileset.save_file(self.file)
			self.status.set('Save Successful!')
			self.edited = False
			self.editstatus['state'] = DISABLED
		except PyMSError, e:
			ErrorDialog(self, e)

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save Tileset As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.edited = False
			self.tileset = None
			self.file = None
			self.edited = False
			self.group = [0,0]
			self.megatile = None
			self.status.set('Load or create a Tileset.')
			self.editstatus['state'] = DISABLED
			self.groupid['text'] = 'MegaTile Group'
			if self.doodad:
				self.doodads.pack_forget()
				self.tiles.pack(side=TOP)
				self.doodad = False
			for v in [self.minitile,self.flipped,self.heightdd,self.walkable,self.blockview,self.ramp,self.index,self.megatilee,self.buildable,self.flags,self.buildable2,self.groundheight,self.edgeleft,self.edgeup,self.edgeright,self.edgedown,self.unknown9,self.hasup,self.unknown11,self.hasdown]:
				v.set(0)
			for n in range(16):
				t = 'tile%s' % n
				self.megatiles.delete(t)
				self.minitiles.delete(t)
			self.megatiles.images = []
			self.minitiles.images = []
			self.megatiles.coords('border', 0, 0, 0, 0)
			self.minitiles.coords('border', 0, 0, 0, 0)
			self.action_states()
			self.updatescroll()

	def register(self, e=None):
		try:
			register_registry('PyTILE','','cv5',os.path.join(BASE_DIR, 'PyTILE.pyw'),os.path.join(BASE_DIR,'Images','PyTILE.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open('file:///%s' % os.path.join(BASE_DIR, 'Docs', 'PyTILE.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyTILE', LONG_VERSION, [('FaRTy1billion','Tileset file specs and HawtTiles.')])

	def exit(self, e=None):
		if not self.unsaved():
			try:
				f = file(os.path.join(BASE_DIR,'Settings','PyTILE.txt'),'w')
				f.write(pprint(self.settings))
				f.close()
			except:
				pass
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pytile.py','pytile.pyw','pytile.exe']):
		gui = PyTILE()
		gui.mainloop()
	else:
		p = optparse.OptionParser(usage='usage: PyTILE [options]', version='PyTILE %s' % LONG_VERSION)
		# p.add_option('-v', '--vf4', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='')
		# p.add_option('-p', '--palette', metavar='FILE', help='Choose a palette for GRP to BMP conversion [default: %default]', default='Units.pal')
		# p.add_option('-g', '--grptobmps', action='store_true', dest='convert', help="Converting from GRP to BMP's [default]", default=True)
		# p.add_option('-b', '--bmpstogrp', action='store_false', dest='convert', help="Converting from BMP's to GRP")
		# p.add_option('-u', '--uncompressed', action='store_true', help="Used to signify if the GRP is uncompressed (both to and from BMP) [default: Compressed]", default=False)
		# p.add_option('-o', '--onebmp', action='store_true', help='Used to signify that you want to convert a GRP to one BMP file. [default: Multiple]', default=False)
		# p.add_option('-f', '--frames', type='int', help='Used to signify you are using a single BMP with alll frames, and how many frames there are.', default=0)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyTILE(opt.gui)
			gui.mainloop()

if __name__ == '__main__':
	main()