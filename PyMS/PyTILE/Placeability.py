
from ..FileFormats.Tileset.Tileset import megatile_to_photo

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.IntegerVar import IntegerVar

class Placeability(PyMSDialog):
	def __init__(self, parent, settings, id=0):
		self.settings = settings
		self.id = id
		self.canvass = []
		self.groups = []
		self.tileset = parent.tileset
		self.gettile = parent.gettile
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
							self.canvass[-1].images.append(megatile_to_photo(self.tileset, g[13][x]))
							self.canvass[-1].create_image(x * 33 + 18, 18, image=self.canvass[-1].images[-1], tags=t)
							self.canvass[-1].tag_bind(t, Double.Click_Left, lambda e,p=(x,y): self.select(p))
						self.groups[-1].append(IntegerVar(c,[0,len(self.tileset.cv5.groups)]))
						Entry(f, textvariable=self.groups[-1][-1], width=1, font=Font.fixed(), bd=0).grid(sticky=E+W, column=x, row=y*2+1, padx=x%2)
			elif ty > 0:
				for x in range(self.width):
					t = 'tile%s,%s' % (x,y)
					self.canvass[h-ty].images.append(megatile_to_photo(self.tileset, g[13][x]))
					self.canvass[h-ty].create_image(x * 33 + 18, 18, image=self.canvass[h-ty].images[-1], tags=t)
					self.canvass[h-ty].tag_bind(t, Double.Click_Left, lambda e,p=(x,h-ty): self.select(p))
				ty -= 1
				if not ty:
					break
		f.pack(padx=5,pady=5)

	def select(self, p):
		self.selecting = p
		from .TilePalette import TilePalette
		TilePalette(self, self.settings, 0, self.groups[p[1]][p[0]].get())

	def change(self, t, id):
		self.groups[self.selecting[1]][self.selecting[0]].set(id)
		self.selecting = None

	def cancel(self, e=None):
		self.ok(self)

	def ok(self, e=None):
		edited = False
		for y,l in enumerate(self.groups):
			for x,g in enumerate(l):
				n = x + y * self.width
				value = g.get()
				old_value = self.tileset.dddata.doodads[self.id][n]
				if value != old_value:
					self.tileset.dddata.doodads[self.id][n] = value
					edited = True
		if edited:
			self.parent.mark_edited()
		PyMSDialog.ok(self)
