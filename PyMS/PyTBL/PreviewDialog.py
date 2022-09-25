
from ..FileFormats import GRP
from ..FileFormats import TBL
from ..FileFormats import FNT

from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.UIKit import *

class PreviewDialog(PyMSDialog):
	letter_space = 1
	space_space = 4

	def __init__(self, parent):
		self.icons = {}
		self.hotkey = IntVar()
		self.hotkey.set(parent.settings.preview.get('hotkey',1))
		self.endatnull = IntVar()
		self.endatnull.set(parent.settings.preview.get('endatnull',1))
		PyMSDialog.__init__(self, parent, 'Text Previewer', resizable=(False,False))

	def geticon(self, n, f):
		if not n in self.icons:
			i = GRP.frame_to_photo(self.parent.unitpal.palette, self.parent.icons, f)
			self.icons[n] = (i[0],(i[2]+1,i[4],0,0))
		return self.icons[n]

	def preview(self, e=None):
		self.canvas.delete(ALL)
		self.characters = {}
		text = TBL.compile_string(self.parent.text.get('1.0',END)[:-1])
		if text:
			color = 2
			display = []
			hotkey = ord(text[1])
			if self.hotkey.get() and hotkey < 6:
				text = text[2:]
				if self.endatnull.get() and '\x00' in text:
					text = text[:text.index('\x00')]
				if hotkey == 1:
					text += '\n \x02200  100  2'
				elif hotkey == 2:
					text += '\n\x02Next Level: 1\n 100  100'
				elif hotkey == 3:
					text += '\n \x0275'
				elif hotkey in [4,5]:
					text += '\n \x02150  50'
				fnt = self.parent.font8
			else:
				if self.endatnull.get() and '\x00' in text:
					text = text[:text.index('\x00')]
				fnt = self.parent.font10
			width = 200
			for l in re.split('[\x0A\x0C]',text):
				w = 0
				display.append([])
				for c in l:
					a = ord(c)
					if a >= fnt.start and a < fnt.start + len(fnt.letters):
						a -= fnt.start
						if ord(c) == 32 and not fnt.sizes[a][0]:
							fnt.sizes[a][0] = self.space_space
						w += fnt.sizes[a][0] + self.letter_space
						if not c in self.characters:
							self.characters[c] = {}
						if not color in self.characters[c]:
							self.characters[c][color] = (FNT.letter_to_photo(self.parent.tfontgam, fnt.letters[a], color), fnt.sizes[a])
						display[-1].append(self.characters[c][color])
					elif a in FNT.COLOR_CODES_INGAME and not color in FNT.COLOR_OVERPOWER:
						color = a
				if w > width:
					width = w
			if self.hotkey.get() and hotkey and hotkey < 6:
				if hotkey == 1:
					display[-1][0] = self.geticon('mins',0)
					display[-1][5] = self.geticon('gas',1)
					display[-1][10] = self.geticon('supply',4)
				elif hotkey == 2:
					display[-1][0] = self.geticon('mins',0)
					display[-1][5] = self.geticon('gas',1)
				elif hotkey == 3:
					display[-1][0] = self.geticon('energy',7)
				elif hotkey in [4,5]:
					display[-1][0] = self.geticon('mins',0)
					display[-1][6] = self.geticon('gas',1)
			self.canvas.config(width=width+10, height=fnt.height*len(display)+10)
			y = 7
			for letters in display:
				x = 7
				for l in letters:
					self.canvas.create_image(x - l[1][2], y, image=l[0], anchor=NW)
					x += l[1][0] + self.letter_space
				y += fnt.height

	def widgetize(self):
		self.canvas = Canvas(self, width=200, height=16, background='#000000', bd=2, relief=SUNKEN)
		self.canvas.pack(padx=5, pady=5)
		f = Frame(self)
		Checkbutton(f, text='Hotkey String', variable=self.hotkey, command=self.preview).pack(side=LEFT)
		Checkbutton(f, text='End at Null', variable=self.endatnull, command=self.preview).pack(side=LEFT)
		f.pack()
		self.preview()
		ok = Button(self, text='Ok', width=10, command=self.ok)
		ok.pack(pady=3)
		return ok

	def ok(self):
		self.parent.settings.preview['hotkey'] = self.hotkey.get()
		self.parent.settings.preview['endatnull'] = self.endatnull.get()
		PyMSDialog.ok(self)
