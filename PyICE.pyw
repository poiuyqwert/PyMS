from Libs.utils import *
from Libs.setutils import *
from Libs.trace import setup_trace
from Libs.SpecialLists import TreeList
from Libs import IScriptBIN, AIBIN, TBL, DAT, PAL, GRP

#import sys
#sys.stdout = open('stdieo.txt','w')

from Tkinter import *
from tkMessageBox import *
import tkFileDialog,tkColorChooser

from thread import start_new_thread
import optparse, os, re, webbrowser, sys, json
try:
	from winsound import *
	SOUND = True
except:
	SOUND = False

LONG_VERSION = 'v%s' % VERSIONS['PyICE']

PALETTES = {}
GRP_CACHE = {}
PREVIEWER_CMDS = [[],[],[],[]]
LONG_OPCODE = max([len(o[0][0]) for o in IScriptBIN.OPCODES] + [13]) + 1
for n,p in IScriptBIN.OPCODES:
	if IScriptBIN.type_frame in p:
		PREVIEWER_CMDS[0].extend(n)
	if IScriptBIN.type_imageid in p:
		PREVIEWER_CMDS[1].extend(n)
	if IScriptBIN.type_spriteid in p:
		PREVIEWER_CMDS[2].extend(n)
	if IScriptBIN.type_flingy in p:
		PREVIEWER_CMDS[3].extend(n)

class SoundDialog(PyMSDialog):
	def __init__(self, parent, id=0):
		self.toplevel = parent.parent
		self.id = IntVar()
		self.id.set(id)
		PyMSDialog.__init__(self, parent, "Sound Insert/Preview")

	def widgetize(self):
		f = Frame(self)
		self.dd = DropDown(f, self.id, ['%03s %s' % (n,TBL.decompile_string(self.toplevel.sfxdatatbl.strings[self.toplevel.soundsdat.get_value(n,'SoundFile')-1][:-1])) for n in range(DAT.SoundsDAT.count)], width=30)
		self.dd.pack(side=LEFT, padx=1)
		i = PhotoImage(file=os.path.join(BASE_DIR,'Images','fwp.gif'))
		b = Button(f, image=i, width=20, height=20, command=self.play, state=[DISABLED,NORMAL][SOUND and not FOLDER])
		b.image = i
		b.pack(side=LEFT, padx=1)
		f.pack(padx=5,pady=5)

		self.overwrite = IntVar()
		self.closeafter = IntVar()

		btns = Frame(self)
		lf = LabelFrame(btns, text='Insert/Overwrite')
		b = Frame(lf)
		Checkbutton(b, text='Overwrite', variable=self.overwrite).pack(side=LEFT)
		Checkbutton(b, text='Close after', variable=self.closeafter).pack(side=LEFT)
		b.pack()
		b = Frame(lf)
		Button(b, text='ID', width=10, command=self.doid).pack(side=LEFT)
		Button(b, text='Command', width=10, command=self.docmd).pack(side=LEFT)
		b.pack(padx=5, pady=5)
		lf.pack(side=LEFT)
		r = Frame(btns)
		ok = Button(r, text='Ok', width=10, command=self.ok)
		ok.pack(side=BOTTOM)
		r.pack(side=RIGHT, fill=Y)
		btns.pack(fill=X, padx=5, pady=5)

		return ok

	def play(self):
		f = self.parent.parent.mpqhandler.get_file('MPQ:sound\\' + self.toplevel.sfxdatatbl.strings[self.toplevel.soundsdat.get_value(self.id.get(),'SoundFile')-1][:-1])
		if f:
			start_new_thread(PlaySound, (f.read(), SND_MEMORY))

	def doid(self):
		if self.overwrite.get():
			s = self.parent.text.index('%s linestart' % INSERT)
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.parent.text.get(s,'%s lineend' % INSERT))
			if m and m.group(2) == 'playsnd':
				self.parent.text.delete(s,'%s lineend' % INSERT)
				self.parent.text.insert(s, m.group(1)+m.group(2)+m.group(3)+str(self.id.get())+m.group(5))
		else:
			self.parent.text.insert(INSERT, self.id.get())
		if self.closeafter.get():
			self.destroy()

	def docmd(self):
		s = self.parent.text.index('%s linestart' % INSERT)
		i = IScriptBIN.type_soundid(1, self.toplevel.ibin, self.id.get())
		t = '\tplaysnd%s\t%s' % (' ' * (LONG_OPCODE-7),i[0])
		if i[1]:
			t += ' # ' + i[1]
		if self.overwrite.get():
			self.parent.text.delete(s,'%s lineend' % INSERT)
		else:
			t += '\n'
		self.parent.text.insert(s, t)
		if self.closeafter.get():
			self.destroy()

class PreviewerDialog(PyMSDialog):
	def __init__(self, parent):
		self.previewing = None
		self.previewnext = None
		self.curgrp = None
		self.timer = None
		self.parent = parent
		self.toplevel = parent.parent
		self.type = IntVar()
		self.curid = IntVar()
		self.curcmd = IntVar()
		self.image = IntVar()
		self.imagecmd = IntVar()
		self.sprites = IntVar()
		self.spritescmd = IntVar()
		self.flingys = IntVar()
		self.flingyscmd = IntVar()
		self.frame = StringVar()
		self.frame.set('Frame: 0 / 0')
		self.speed = 0
		self.play = None
		PyMSDialog.__init__(self, parent, "Graphics Insert/Preview", grabwait=False, resizable=(False, False))

	def nocur(self):
		if self.curradio and self.curradio['state'] == NORMAL:
			self.curradio['state'] = DISABLED
			self.curdd['state'] = DISABLED
			self.curcmddd['state'] = DISABLED
		if self.type.get() == 0:
			self.type.set(1)

	def getlist(self, lb, c):
		return ['['.join(lb.get(i).split('[')[:-1]) for i in range(c)]

	def updatecurrentimages(self):
		r = self.parent.text.tag_prevrange('HeaderStart',INSERT)
		if not r:
			r = self.parent.text.tag_nextrange('HeaderStart',INSERT)
		if not r:
			self.nocur()
			return
		n = re.split('\\s+',self.parent.text.get('%s +1lines linestart' % r[0],'%s +1lines lineend' % r[1]))
		try:
			n[1] = int(n[1])
		except:
			self.nocur()
			return
		if n[0] == 'IsId' and n[1] >= 0 and n[1] <= 411:
			if self.curradio and self.curradio['state'] == DISABLED:
				self.curradio['state'] = NORMAL
				self.curdd['state'] = NORMAL
				self.curcmddd['state'] = NORMAL
			cur = []
			for i in range(DAT.ImagesDAT.count):
				if self.toplevel.imagesdat.get_value(i, 'IscriptID') == n[1]:
					cur.append('['.join(self.toplevel.imageslist.get(i).split('[')[:-1]))
			self.curdd.setentries(cur)
			if cur:
				return
		self.nocur()

	def widgetize(self):
		left = Frame(self)
		c = [
			(0, "Current IScript's images", self.curid, self.curcmd, [], DISABLED),
			(1, 'Images.dat entries', self.image, self.imagecmd, self.getlist(self.toplevel.imageslist,DAT.ImagesDAT.count), NORMAL),
			(2, 'Sprites.dat entries', self.sprites, self.spritescmd, self.getlist(self.toplevel.spriteslist,DAT.SpritesDAT.count), NORMAL),
			(3, 'Flingy.dat entries', self.flingys, self.flingyscmd, self.getlist(self.toplevel.flingylist,DAT.FlingyDAT.count), NORMAL),
		]
		for n,l,v,c,e,s in c:
			Label(left, text=l + ":", anchor=W).pack(fill=X)
			f = Frame(left)
			df = Frame(f)
			if n == 0:
				self.curradio = Radiobutton(f, text='', variable=self.type, command=lambda v=v,t=n: self.select(v.get(),t), value=n, state=s)
				self.curradio.pack(side=LEFT)
				self.curdd = DropDown(df, v, e, lambda s,t=n: self.select(s,t), 30, state=s)
				self.curdd.pack()
				self.curcmddd = DropDown(df, c, PREVIEWER_CMDS[n], width=30, state=s)
				self.curcmddd.pack()
			else:
				Radiobutton(f, text='', variable=self.type, command=lambda v=v,t=n: self.select(v.get(),t), value=n, state=s).pack(side=LEFT)
				DropDown(df, v, e, lambda s,t=n: self.select(s,t), 30, state=s).pack()
				DropDown(df, c, PREVIEWER_CMDS[n], width=30, state=s).pack()
			df.pack(side=LEFT)
			f.pack()
		self.overwrite = IntVar()
		self.overwrite.set(self.toplevel.settings.get('overwrite',0))
		self.closeafter = IntVar()
		self.closeafter.set(self.toplevel.settings.get('closeafter',0))
		btns = Frame(left)
		lf = LabelFrame(btns, text='Insert/Overwrite')
		b = Frame(lf)
		Checkbutton(b, text='Overwrite', variable=self.overwrite).pack(side=LEFT)
		Checkbutton(b, text='Close after', variable=self.closeafter).pack(side=LEFT)
		b.pack()
		b = Frame(lf)
		Button(b, text='ID', width=10, command=self.doid).pack(side=LEFT)
		Button(b, text='Command', width=10, command=self.docmd).pack(side=LEFT)
		b.pack(padx=5, pady=5)
		lf.pack(side=LEFT)
		r = Frame(btns)
		ok = Button(r, text='Ok', width=10, command=self.destroy)
		ok.pack(side=BOTTOM)
		r.pack(fill=BOTH, expand=1)
		btns.pack(side=BOTTOM, fill=X, padx=5, pady=5)
		left.pack(side=LEFT, fill=Y)

		right = Frame(self)
		f = Frame(right)
		Label(f, text='GRP Preview:', anchor=W).pack(side=LEFT, fill=X, expand=1)
		Label(f, textvariable=self.frame, anchor=W).pack(side=LEFT)
		f.pack(fill=X)
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.settings.get('showpreview',1))
		p = Frame(right)
		self.preview = Canvas(p, width=257, height=257, background='#000000')
		self.preview.pack()
		self.scroll = Scrollbar(p, orient=HORIZONTAL, command=self.selectframe)
		self.scroll.set(0,1)
		self.scroll.pack(fill=X)
		p.pack()
		self.buttons = {}
		frameview = Frame(right)
		buttons = [
			('begin', 'Jump to first frame'),
			('frw', 'Jump 17 frames Left'),
			('rw', 'Jump 1 frame Left'),
			('frwp', 'Play every 17th frame going Left'),
			('rwp', 'Play every frame going Left'),
			('stop', 'Stop playing frames'),
			('fwp', 'Play every frame going Right'),
			('ffwp', 'Play every 17th frame going Right'),
			('fw', 'Jump 1 frame Right'),
			('ffw', 'Jump 17 frames Right'),
			('end', 'Jump to last frame')
		]
		for n,btn in enumerate(buttons):
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(frameview, image=image, width=20, height=20, command=lambda i=n: self.frameset(i), state=DISABLED)
				button.image = image
				button.tooltip = Tooltip(button, btn[1])
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(frameview, width=2).pack(side=LEFT)
		frameview.pack(padx=1, pady=3)

		self.prevspeed = IntegerVar(self.toplevel.settings.get('previewspeed', 150), [1,5000])
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.settings.get('showpreview',1))
		self.looppreview = IntVar()
		self.looppreview.set(self.toplevel.settings.get('looppreview',1))
		self.prevfrom = IntegerVar(0,[0,0])
		self.prevto = IntegerVar(0,[0,0])

		opts = Frame(right)
		speedview = Frame(opts)
		Checkbutton(speedview, text='Show Preview at Speed:', variable=self.showpreview, command=self.display).pack(side=LEFT)
		Entry(speedview, textvariable=self.prevspeed, font=couriernew, width=4).pack(side=LEFT)
		Label(speedview, text='ms').pack(side=LEFT)
		speedview.grid()
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(column=1, row=0) # , command=self.drawpreview
		s = Frame(opts)
		Label(s, text='Preview Between: ').pack(side=LEFT)
		self.prevstart = Entry(s, textvariable=self.prevfrom, font=couriernew, width=3, state=DISABLED)
		self.prevstart.pack(side=LEFT)
		Label(s, text=' - ').pack(side=LEFT)
		self.prevend = Entry(s, textvariable=self.prevto, font=couriernew, width=3, state=DISABLED)
		self.prevend.pack(side=LEFT)
		s.grid(row=1, columnspan=2)
		opts.pack(fill=X)
		right.pack(side=LEFT, fill=Y, expand=1)

		return ok

	def display(self):
		self.drawpreview()
		self.action_states()
		self.updateframes()

	def action_states(self):
		btns = [DISABLED,NORMAL][not not (self.curgrp and self.curgrp[2] > 1 and self.showpreview.get())]
		for btn in ['begin','frw','rw','frwp','rwp','fw','ffw','fwp','ffwp','end']:
			self.buttons[btn]['state'] = btns

	def frameset(self, n):
		if not n in [3,4,5,6,7]:
			if n in [0,10]:
				s = [END,0][not n]
			elif n in [1,2,8,9]:
				s = self.previewing[1] + [-17,-1,1,17][n % 5 - 1]
				if s < 0 or s >= self.curgrp[2]:
					if not self.looppreview.get():
						return
					if s < 0:
						s += self.curgrp[2]
					if s >= self.curgrp[2]:
						s %= self.curgrp[2]
			self.previewnext[1] = s
			self.updateframes()
			self.drawpreview()
		if n in [3,4,6,7]:
			self.buttons['stop']['state'] = NORMAL
			self.speed = [-17,-1,None,1,17][n - 3]
			self.play = self.after(int(self.prevspeed.get()), self.playframe)
		elif self.speed or self.play:
			self.stopframe()

	def stopframe(self):
		if self.play:
			self.buttons['stop']['state'] = DISABLED
			self.speed = None
			self.after_cancel(self.play)
			self.play = None

	def playframe(self):
		prevfrom = self.prevfrom.get()
		prevto = self.prevto.get()
		if self.speed and prevto > prevfrom:
			i = self.previewing[1] + self.speed
			frames = prevto-prevfrom+1
			if self.looppreview.get() or (i >= prevfrom and i <= prevto):
				while i < prevfrom or i > prevto:
					if i < prevfrom:
						i += frames
					if i > prevto:
						i -= frames
				self.previewnext[1] = i
				self.updateframes()
				self.drawpreview()
				self.after_cancel(self.play)
				self.play = self.after(int(self.prevspeed.get()), self.playframe)
				return
		self.stopframe()

	def doid(self):
		self.stopframe()
		t = self.type.get()
		if t:
			lb = [self.toplevel.imageslist,self.toplevel.spriteslist,self.toplevel.flingylist][t-1]
			i = lb.get([self.image,self.sprites,self.flingys][t-1].get()).strip().split(' ')[0]
		else:
			i = IScriptBIN.type_frame(1, None, self.previewing[1])[0]
		if self.overwrite.get():
			s = self.parent.text.index('%s linestart' % INSERT)
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.parent.text.get(s,'%s lineend' % INSERT))
			if m and m.group(2) in PREVIEWER_CMDS[t]:
				self.parent.text.delete(s,'%s lineend' % INSERT)
				self.parent.text.insert(s, m.group(1)+m.group(2)+m.group(3)+i+m.group(5))
		else:
			self.parent.text.insert(INSERT, i)
		if self.closeafter.get():
			self.destroy()

	def docmd(self):
		self.stopframe()
		t = self.type.get()
		s = self.parent.text.index('%s linestart' % INSERT)
		if t:
			c = [IScriptBIN.type_imageid,IScriptBIN.type_spriteid,IScriptBIN.type_flingy][t-1]
			lb = [self.toplevel.imageslist,self.toplevel.spriteslist,self.toplevel.flingylist][t-1]
			i = c(1, self.toplevel, int(lb.get([self.image,self.sprites,self.flingys][t-1].get()).strip().split(' ')[0]))
		else:
			i = IScriptBIN.type_frame(1, None, self.previewing[1])
		c = PREVIEWER_CMDS[t][[self.curcmd,self.imagecmd,self.spritescmd,self.flingyscmd][t].get()]
		t = '\t%s%s\t%s' % (c,' ' * (LONG_OPCODE-len(c)),i[0])
		p = len(IScriptBIN.OPCODES[IScriptBIN.REV_OPCODES[c]][1])
		if p > 1:
			t += ' 0' * (p-1)
		if i[1]:
			t += ' # ' + i[1]
		if self.overwrite.get():
			self.parent.text.delete(s,'%s lineend' % INSERT)
		else:
			t += '\n'
		self.parent.text.insert(s, t)
		if self.closeafter.get():
			self.destroy()

	def updateframes(self):
		if self.previewnext and self.curgrp:
			self.frame.set('Frame: %s / %s' % (self.previewnext[1],self.curgrp[2]))
			if self.curgrp[2]:
				x = self.previewnext[1] / float(self.curgrp[2])
				self.scroll.set(x,x+1/float(self.curgrp[2]))
			else:
				self.scroll.set(0,1)
		self.action_states()

	def preview_limits(self):
		if self.curgrp[1]:
			self.prevstart.config(state=NORMAL)
			self.prevend.config(state=NORMAL)
			to = max(self.curgrp[2]-1,0)
			self.prevfrom.range[1] = to
			self.prevto.range[1] = to
			self.prevfrom.set(0)
			self.prevto.set(to)
		else:
			self.prevstart.config(state=DISABLED)
			self.prevend.config(state=DISABLED)
			self.prevfrom.set(0)
			self.prevto.set(0)

	def grp(self, i, pal, frame, *path):
		if not FOLDER and pal in PALETTES:
			p = os.path.join(BASE_DIR,'Libs','MPQ',os.path.join(*path))
			path = '\\'.join(path)
			draw = not path in GRP_CACHE or not frame in GRP_CACHE[path] or not pal in GRP_CACHE[path][frame]
			if draw or (not self.curgrp or i != self.curgrp[0]):
				if self.curgrp and i == self.curgrp[0]:
					grp = self.curgrp[1]
				else:
					p = self.parent.parent.mpqhandler.get_file('MPQ:' + path)
					try:
						grp = GRP.CacheGRP()
						grp.load_file(p)
					except PyMSError, e:
						return None
					self.curgrp = [i,None,0]
					self.curgrp[1] = grp
					self.curgrp[2] = grp.frames
					self.preview_limits()
				if draw:
					if not path in GRP_CACHE:
						GRP_CACHE[path] = {}
					if not frame in GRP_CACHE:
						GRP_CACHE[path][frame] = {}
					GRP_CACHE[path][frame][pal] = GRP.frame_to_photo(PALETTES[pal], grp, frame, True)
			return GRP_CACHE[path][frame][pal]

	def select(self, s, t, f=0):
		if t != self.type.get():
			return
		self.stopframe()
		if t == 0:
			i = int(self.curdd.entries[s].strip().split(' ')[0])
		elif t == 1:
			i = int(self.toplevel.imageslist.get(s).strip().split(' ')[0])
		elif t == 2:
			i = self.toplevel.spritesdat.get_value(int(self.toplevel.spriteslist.get(s).strip().split(' ')[0]), 'ImageFile')
		elif t == 3:
			i = self.toplevel.spritesdat.get_value(self.toplevel.flingydat.get_value(int(self.toplevel.flingylist.get(s).strip().split(' ')[0]), 'Sprite'), 'ImageFile')
		self.previewnext = [i,f]
		self.drawpreview()
		self.updateframes()

	def selectframe(self, t, p, e=None):
		self.stopframe()
		a = {'pages':17,'units':1}
		if t == 'moveto':
			self.previewnext[1] = int(self.curgrp[2] * float(p))
		elif t == 'scroll':
			self.previewnext[1] = min(self.curgrp[2]-1,max(0,self.previewnext[1] + int(p) * a[e]))
		self.updateframes()
		# if self.timer:
			# self.after_cancel(self.timer)
		# self.timer = self.after(10, self.drawpreview)
		self.drawpreview()

	def drawpreview(self):
		if self.previewnext != self.previewing or (self.previewing != None and not self.showpreview.get()) or (self.previewing == None and self.showpreview.get()):
			self.preview.delete(ALL)
			if self.showpreview.get():
				self.previewing = list(self.previewnext)
				i = self.previewing[0]
				g = self.toplevel.imagesdat.get_value(i,'GRPFile')
				if g:
					f = self.toplevel.imagestbl.strings[g-1][:-1]
					if f.startswith('thingy\\tileset\\'):
						p = 'Terrain'
					else:
						p = 'Units'
						if self.toplevel.imagesdat.get_value(i, 'DrawFunction') == 9 and self.toplevel.imagesdat.get_value(i, 'Remapping') and self.toplevel.imagesdat.get_value(i, 'Remapping') < 4:
							p = ['o','b','g'][self.toplevel.imagesdat.get_value(i, 'Remapping')-1] + 'fire'
					sprite = self.grp(i,p,self.previewing[1],'unit',f)
					if sprite:
						self.preview.create_image(130, 130, image=sprite[0])
			else:
				self.previewing = None

	def destroy(self):
		self.stopframe()
		self.toplevel.settings['overwrite'] = self.overwrite.get()
		self.toplevel.settings['closeafter'] = self.closeafter.get()
		self.toplevel.settings['showpreview'] = self.showpreview.get()
		self.toplevel.settings['previewspeed'] = self.prevspeed.get()
		self.toplevel.settings['looppreview'] = self.looppreview.get()
		PyMSDialog.withdraw(self)

class FindReplaceDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find/Replace', grabwait=False, resizable=(True, False))

	def widgetize(self):
		self.find = StringVar()
		self.replacewith = StringVar()
		self.replace = IntVar()
		self.inselection = IntVar()
		self.casesens = IntVar()
		self.regex = IntVar()
		self.multiline = IntVar()
		self.updown = IntVar()
		self.updown.set(1)

		l = Frame(self)
		f = Frame(l)
		s = Frame(f)
		Label(s, text='Find:', anchor=E, width=12).pack(side=LEFT)
		self.findentry = TextDropDown(s, self.find, self.parent.parent.findhistory, 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(fill=X)
		self.findentry.entry.selection_range(0, END)
		self.findentry.focus_set()
		s.pack(fill=X)
		s = Frame(f)
		Label(s, text='Replace With:', anchor=E, width=12).pack(side=LEFT)
		self.replaceentry = TextDropDown(s, self.replacewith, self.parent.parent.replacehistory, 30)
		self.replaceentry.pack(fill=X)
		s.pack(fill=X)
		f.pack(side=TOP, fill=X, pady=2)
		f = Frame(l)
		self.selectcheck = Checkbutton(f, text='In Selection', variable=self.inselection, anchor=W)
		self.selectcheck.pack(fill=X)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens, anchor=W).pack(fill=X)
		Checkbutton(f, text='Regular Expression', variable=self.regex, anchor=W, command=lambda i=1: self.check(i)).pack(fill=X)
		self.multicheck = Checkbutton(f, text='Multi-Line', variable=self.multiline, anchor=W, state=DISABLED, command=lambda i=2: self.check(i))
		self.multicheck.pack(fill=X)
		f.pack(side=LEFT, fill=BOTH)
		f = Frame(l)
		lf = LabelFrame(f, text='Direction')
		self.up = Radiobutton(lf, text='Up', variable=self.updown, value=0, anchor=W)
		self.up.pack(fill=X)
		self.down = Radiobutton(lf, text='Down', variable=self.updown, value=1, anchor=W)
		self.down.pack()
		lf.pack()
		f.pack(side=RIGHT, fill=Y)
		l.pack(side=LEFT, fill=BOTH, pady=2, expand=1)

		l = Frame(self)
		Button(l, text='Find Next', command=self.findnext, default=NORMAL).pack(fill=X, pady=1)
		Button(l, text='Count', command=self.count).pack(fill=X, pady=1)
		self.replacebtn = Button(l, text='Replace', command=lambda i=1: self.findnext(replace=i))
		self.replacebtn.pack(fill=X, pady=1)
		self.repallbtn = Button(l, text='Replace All', command=self.replaceall)
		self.repallbtn.pack(fill=X, pady=1)
		Button(l, text='Close', command=self.ok).pack(fill=X, pady=4)
		l.pack(side=LEFT, fill=Y, padx=2)

		self.bind('<Return>', self.findnext)
		self.bind('<FocusIn>', lambda e,i=3: self.check(i))

		if 'findreplacewindow' in self.parent.parent.settings:
			loadsize(self, self.parent.parent.settings, 'findreplacewindow')

		return self.findentry

	def check(self, i):
		if i == 1:
			if self.regex.get():
				self.multicheck['state'] = NORMAL
			else:
				self.multicheck['state'] = DISABLED
				self.multiline.set(0)
		if i in [1,2]:
			s = [NORMAL,DISABLED][self.multiline.get()]
			self.up['state'] = s
			self.down['state'] = s
			if s == DISABLED:
				self.updown.set(1)
		elif i == 3:
			if self.parent.text.tag_ranges('Selection'):
				self.selectcheck['state'] = NORMAL
			else:
				self.selectcheck['state'] = DISABLED
				self.inselection.set(0)

	def findnext(self, key=None, replace=0):
		f = self.find.get()
		if not f in self.parent.parent.findhistory:
			self.parent.parent.findhistory.append(f)
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			if replace:
				rep = self.replacewith.get()
				if not rep in self.parent.parent.replacehistory:
					self.parent.parent.replacehistory.append(rep)
				item = self.parent.text.tag_ranges('Selection')
				if item and r.match(self.parent.text.get(*item)):
					ins = r.sub(rep, self.parent.text.get(*item))
					self.parent.text.delete(*item)
					self.parent.text.insert(item[0], ins)
					self.parent.text.update_range(item[0])
			if self.multiline.get():
				m = r.search(self.parent.text.get(INSERT, END))
				if m:
					self.parent.text.tag_remove('Selection', '1.0', END)
					s,e = '%s +%sc' % (INSERT, m.start(0)),'%s +%sc' % (INSERT,m.end(0))
					self.parent.text.tag_add('Selection', s, e)
					self.parent.text.mark_set(INSERT, e)
					self.parent.text.see(s)
					self.check(3)
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
			else:
				u = self.updown.get()
				s,lse,rlse,e = ['-','+'][u],['lineend','linestart'][u],['linestart','lineend'][u],[self.parent.text.index('1.0 lineend'),self.parent.text.index(END)][u]
				i = self.parent.text.index(INSERT)
				if i == e:
					return
				if i == self.parent.text.index('%s %s' % (INSERT, rlse)):
					i = self.parent.text.index('%s %s1lines %s' % (INSERT, s, lse))
				n = -1
				while not u or i != e:
					if u:
						m = r.search(self.parent.text.get(i, '%s %s' % (i, rlse)))
					else:
						m = None
						a = r.finditer(self.parent.text.get('%s %s' % (i, rlse), i))
						c = 0
						for x,f in enumerate(a):
							if x == n or n == -1:
								m = f
								c = x
						n = c - 1
					if m:
						self.parent.text.tag_remove('Selection', '1.0', END)
						if u:
							s,e = '%s +%sc' % (i,m.start(0)),'%s +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, e)
						else:
							s,e = '%s linestart +%sc' % (i,m.start(0)),'%s linestart +%sc' % (i,m.end(0))
							self.parent.text.mark_set(INSERT, s)
						self.parent.text.tag_add('Selection', s, e)
						self.parent.text.see(s)
						self.check(3)
						break
					if (not u and n == -1 and self.parent.text.index('%s lineend' % i) == e) or i == e:
						p = self
						if key and key.keycode == 13:
							p = self.parent
						askquestion(parent=p, title='Find', message="Can't find text.", type=OK)
						break
					i = self.parent.text.index('%s %s1lines %s' % (i, s, lse))
				else:
					p = self
					if key and key.keycode == 13:
						p = self.parent
					askquestion(parent=p, title='Find', message="Can't find text.", type=OK)

	def count(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			askquestion(parent=self, title='Count', message='%s matches found.' % len(r.findall(self.parent.text.get('1.0', END))), type=OK)

	def replaceall(self):
		f = self.find.get()
		if f:
			regex = f
			if not self.regex.get():
				regex = re.escape(regex)
			try:
				r = re.compile(regex, [re.I,0][self.casesens.get()] | [0,re.M | re.S][self.multiline.get()])
			except:
				self.resettimer = self.after(1000, self.updatecolor)
				self.findentry['bg'] = '#FFB4B4'
				return
			text = r.subn(self.replacewith.get(), self.parent.text.get('1.0', END))
			if text[1]:
				self.parent.text.delete('1.0', END)
				self.parent.text.insert('1.0', text[0].rstrip('\n'))
				self.parent.text.update_range('1.0')
			askquestion(parent=self, title='Replace Complete', message='%s matches replaced.' % text[1], type=OK)

	def updatecolor(self):
		if self.resettimer:
			self.after_cancel(self.resettimer)
			self.resettimer = None
		self.findentry['bg'] = self.findentry.c

	def destroy(self):
		savesize(self, self.parent.parent.settings, 'findreplacewindow')
		PyMSDialog.withdraw(self)

class CodeColors(PyMSDialog):
	def __init__(self, parent):
		self.cont = False
		self.tags = dict(parent.text.tags)
		self.info = odict()
		self.info['Block'] = 'The color of a "block:" in the code.'
		self.info['Keywords'] = ['Keywords:\n    .headerstart  .headerend  [NONE]','HeaderStart']
		#self.info['Types'] = 'Variable types:\n    ' + '  '.join(AIBIN.types)
		self.info['Commands'] = 'The color of all the commands.'
		self.info['Animations'] = 'The color of all the header labels (IsID, Type, and Animations).'
		self.info['Number'] = 'The color of all numbers.'
		self.info['Comment'] = 'The color of a regular comment.'
		self.info['Operators'] = 'The color of the operators:\n    ( ) , = :'
		self.info['Error'] = 'The color of an error when compiling.'
		self.info['Warning'] = 'The color of a warning when compiling.'
		self.info['Selection'] = 'The color of selected text in the editor.'
		PyMSDialog.__init__(self, parent, 'Color Settings', resizable=(False, False))

	def widgetize(self):
		self.listbox = Listbox(self, font=couriernew, width=20, height=16, exportselection=0, activestyle=DOTBOX)
		self.listbox.bind('<ButtonRelease-1>', self.select)
		for t in self.info.keys():
			self.listbox.insert(END, t)
		self.listbox.select_set(0)
		self.listbox.pack(side=LEFT, fill=Y, padx=2, pady=2)

		self.fg = IntVar()
		self.bg = IntVar()
		self.bold = IntVar()
		self.infotext = StringVar()

		r = Frame(self)
		opt = LabelFrame(r, text='Style:', padx=5, pady=5)
		f = Frame(opt)
		c = Checkbutton(f, text='Foreground', variable=self.fg, width=20, anchor=W)
		c.bind('<ButtonRelease-1>', lambda e,i=0: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Background', variable=self.bg)
		c.bind('<ButtonRelease-1>', lambda e,i=1: self.select(e,i))
		c.grid(sticky=W)
		c = Checkbutton(f, text='Bold', variable=self.bold)
		c.bind('<ButtonRelease-1>', lambda e,i=2: self.select(e,i))
		c.grid(sticky=W)
		self.fgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.fgcanvas.bind('<Button-1>', lambda e,i=0: self.colorselect(e, i))
		self.fgcanvas.grid(column=1, row=0)
		self.bgcanvas = Canvas(f, width=32, height=32, background='#000000')
		self.bgcanvas.bind('<Button-1>', lambda e,i=1: self.colorselect(e, i))
		self.bgcanvas.grid(column=1, row=1)
		f.pack(side=TOP)
		Label(opt, textvariable=self.infotext, height=6, justify=LEFT).pack(side=BOTTOM, fill=X)
		opt.pack(side=TOP, fill=Y, expand=1, padx=2, pady=2)
		f = Frame(r)
		ok = Button(f, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3)
		Button(f, text='Cancel', width=10, command=self.cancel).pack(side=LEFT)
		f.pack(side=BOTTOM, pady=2)
		r.pack(side=LEFT, fill=Y)

		self.select()

		return ok

	def select(self, e=None, n=None):
		i = self.info.getkey(int(self.listbox.curselection()[0]))
		s = self.tags[i.replace(' ', '')]
		if n == None:
			if isinstance(self.info[i], list):
				t = self.info[i][0].split('\n')
			else:
				t = self.info[i].split('\n')
			text = ''
			if len(t) == 2:
				d = '  '
				text = t[0] + '\n'
			else:
				d = ''
			text += fit(d, t[-1], 35, True)[:-1]
			self.infotext.set(text)
			if s['foreground'] == None:
				self.fg.set(0)
				self.fgcanvas['background'] = '#000000'
			else:
				self.fg.set(1)
				self.fgcanvas['background'] = s['foreground']
			if s['background'] == None:
				self.bg.set(0)
				self.bgcanvas['background'] = '#000000'
			else:
				self.bg.set(1)
				self.bgcanvas['background'] = s['background']
			self.bold.set(s['font'] != None)
		else:
			v = [self.fg,self.bg,self.bold][n].get()
			if n == 2:
				s['font'] = [self.parent.text.boldfont,couriernew][v]
			else:
				s[['foreground','background'][n]] = ['#000000',None][v]
				if v:
					[self.fgcanvas,self.bgcanvas][n]['background'] = '#000000'

	def colorselect(self, e, i):
		if [self.fg,self.bg][i].get():
			v = [self.fgcanvas,self.bgcanvas][i]
			g = ['foreground','background'][i]
			c = tkColorChooser.askcolor(parent=self, initialcolor=v['background'], title='Select %s color' % g)
			if c[1]:
				v['background'] = c[1]
				k = self.info.getkey(int(self.listbox.curselection()[0])).replace(' ','')
				self.tags[k][g] = c[1]
				if isinstance(self.info[k], list):
					self.tags[self.info[k][1]][g] = c[1]
			self.focus_set()

	def ok(self):
		self.cont = self.tags
		PyMSDialog.ok(self)

	def cancel(self):
		self.cont = False
		PyMSDialog.ok(self)

class IScriptCodeText(CodeText):
	def __init__(self, parent, ibin, ecallback=None, icallback=None, scallback=None, highlights=None):
		self.ibin = ibin
		self.boldfont = ('Courier New', -11, 'bold')
		if highlights:
			self.highlights = highlights
		else:
			self.highlights = {
				'Block':{'foreground':'#FF00FF','background':None,'font':None},
				'Keywords':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'HeaderStart':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				#'Types':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Animations':{'foreground':'#0000AA','background':None,'font':self.boldfont},
				'Commands':{'foreground':'#0000AA','background':None,'font':None},
				'Number':{'foreground':'#FF0000','background':None,'font':None},
				'Comment':{'foreground':'#008000','background':None,'font':None},
				'Operators':{'foreground':'#0000FF','background':None,'font':self.boldfont},
				'Newline':{'foreground':None,'background':None,'font':None},
				'Error':{'foreground':None,'background':'#FF8C8C','font':None},
				'Warning':{'foreground':None,'background':'#FFC8C8','font':None},
			}
		CodeText.__init__(self, parent, ecallback, icallback, scallback)
		self.text.bind('<Control-q>', self.commentrange)

	def setedit(self):
		if self.ecallback != None:
			self.ecallback()
		self.edited = True

	def commentrange(self, e=None):
		item = self.tag_ranges('Selection')
		if item:
			head,tail = self.index('%s linestart' % item[0]),self.index('%s linestart' % item[1])
			while self.text.compare(head, '<=', tail):
				m = re.match('(\\s*)(#?)(.*)', self.get(head, '%s lineend' % head))
				if m.group(2):
					self.tk.call(self.text.orig, 'delete', '%s +%sc' % (head, len(m.group(1))))
				elif m.group(3):
					self.tk.call(self.text.orig, 'insert', head, '#')
				head = self.index('%s +1line' % head)
			self.update_range(self.index('%s linestart' % item[0]), self.index('%s lineend' % item[1]))

	def setupparser(self):
		comment = '(?P<Comment>#(?!#[gG][rR][pP]:|#[nN][aA][mM][eE]:)[^\\n]*$)'
		block = '^[ \\t]*(?P<Block>[^\x00:(),\\n]+)(?=:)'
		opcodes = []
		for o in IScriptBIN.OPCODES:
			opcodes.extend(o[0])
		cmds = '\\b(?P<Commands>%s)\\b' % '|'.join(opcodes)
		anims = ['IsId','Type']
		for h in IScriptBIN.HEADER:
			anims.extend(h)
		animations = '\\b(?P<Animations>%s)\\b' % '|'.join(anims)
		num = '\\b(?P<Number>\\d+|0x[0-9a-fA-F]+)\\b'
		operators = '(?P<Operators>[():,=])'
		kw = '(?P<Keywords>\\.headerend|##[gG][rR][pP]:|##[nN][aA][mM][eE]:|\\[NONE\\])'
		#types = '\\b(?P<Types>%s)\\b' % '|'.join(AIBIN.types)
		self.basic = re.compile('|'.join((comment, kw, block, cmds, animations, num, operators, '(?P<HeaderStart>\\.headerstart)', '(?P<Newline>\\n)')), re.S | re.M)
		self.tooptips = [AnimationTooltip(self),CommandTooltip(self)]
		self.tags = dict(self.highlights)

	def colorize(self):
		next = '1.0'
		while True:
			item = self.tag_nextrange("Update", next)
			if not item:
				break
			head, tail = item
			self.tag_remove('Newline', head, tail)
			item = self.tag_prevrange('Newline', head)
			if item:
				head = item[1] + ' linestart'
			else:
				head = "1.0"
			chars = ""
			next = head
			lines_to_get = 1
			ok = False
			while not ok:
				mark = next
				next = self.index(mark + '+%d lines linestart' % lines_to_get)
				lines_to_get = min(lines_to_get * 2, 100)
				ok = 'Newline' in self.tag_names(next + '-1c')
				line = self.get(mark, next)
				if not line:
					return
				for tag in self.tags.keys():
					if tag != 'Selection':
						self.tag_remove(tag, mark, next)
				chars = chars + line
				m = self.basic.search(chars)
				while m:
					for key, value in m.groupdict().items():
						if value != None:
							a, b = m.span(key)
							self.tag_add(key, head + '+%dc' % a, head + '+%dc' % b)
					m = self.basic.search(chars, m.end())
				if 'Newline' in self.tag_names(next + '-1c'):
					head = next
					chars = ''
				else:
					ok = False
				if not ok:
					self.tag_add('Update', next)
				self.update()
				if not self.coloring:
					return

class CodeTooltip(Tooltip):
	tag = ''

	def __init__(self, widget):
		Tooltip.__init__(self, widget)

	def setupbinds(self, press):
		if self.tag:
			self.widget.tag_bind(self.tag, '<Enter>', self.enter, '+')
			self.widget.tag_bind(self.tag, '<Leave>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<Motion>', self.motion, '+')
			self.widget.tag_bind(self.tag, '<Button-1>', self.leave, '+')
			self.widget.tag_bind(self.tag, '<ButtonPress>', self.leave)

	def showtip(self):
		if self.tip:
			return
		t = ''
		if self.tag:
			pos = list(self.widget.winfo_pointerxy())
			head,tail = self.widget.tag_prevrange(self.tag,self.widget.index('@%s,%s+1c' % (pos[0] - self.widget.winfo_rootx(),pos[1] - self.widget.winfo_rooty())))
			t = self.widget.get(head,tail)
		try:
			t = self.gettext(t)
			self.tip = Toplevel(self.widget, relief=SOLID, borderwidth=1)
			self.tip.wm_overrideredirect(1)
			frame = Frame(self.tip, background='#FFFFC8', borderwidth=0)
			Label(frame, text=t, justify=LEFT, font=self.font, background='#FFFFC8', relief=FLAT).pack(padx=1, pady=1)
			frame.pack()
			pos = list(self.widget.winfo_pointerxy())
			self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
			self.tip.update_idletasks()
			move = False
			if pos[0] + self.tip.winfo_reqwidth() > self.tip.winfo_screenwidth():
				move = True
				pos[0] = self.tip.winfo_screenwidth() - self.tip.winfo_reqwidth()
			if pos[1] + self.tip.winfo_reqheight() + 22 > self.tip.winfo_screenheight():
				move = True
				pos[1] -= self.tip.winfo_reqheight() + 44
			if move:
				self.tip.wm_geometry('+%d+%d' % (pos[0],pos[1]+22))
		except:
			if self.tip:
				try:
					self.tip.destroy()
				except:
					pass
				self.tip = None
			return

	def gettext(self, t):
		# Overload to specify tooltip text
		return ''

class AnimationTooltip(CodeTooltip):
	tag = 'Animations'

	def gettext(self, anim):
		return 'Animation:\n  %s\n%s' % (anim,fit('    ', IScriptBIN.HEADER_HELP[IScriptBIN.REV_HEADER[anim]], end=True)[:-1])

class CommandTooltip(CodeTooltip):
	tag = 'Commands'

	def gettext(self, cmd):
		text = 'Command:\n  %s(' % cmd
		c = IScriptBIN.REV_OPCODES[cmd]
		params = IScriptBIN.OPCODES[c][1]
		pinfo = ''
		if params:
			pinfo = '\n\n'
			done = []
			for p in params:
				t = p.__doc__
				text += t + ', '
				if not t in done:
					pinfo += fit('  %s: ' % t, IScriptBIN.TYPE_HELP[t], end=True, indent=4)
					done.append(t)
			text = text[:-2]
		text += ')'
		return text + '\n' + fit('    ', IScriptBIN.CMD_HELP[c], end=True)[:-1] + pinfo[:-1]

class GeneratorEditor(Frame):
	def __init__(self, parent, generator):
		self.generator = generator
		Frame.__init__(self, parent)
	def save(self):
		raise
class GeneratorType:
	TYPES = {}
	@staticmethod
	def validate(save):
		raise NotImplementerError(self.__class__.__name__ + '.validate()')
	def __init__(self, save=None):
		pass
	# None for infinite
	def count(self):
		raise NotImplementerError(self.__class__.__name__ + '.count()')
	def value(self, lookup_value):
		raise PyMSError(self.__class__.__name__ + '.value()')
	def description(self):
		raise PyMSError(self.__class__.__name__ + '.description()')
	def save(self):
		return {'type': self.TYPE}
class GeneratorEditorRange(GeneratorEditor):
	RESIZABLE = (False,False)
	def __init__(self, parent, generator):
		GeneratorEditor.__init__(self, parent, generator)

		self.start = IntegerVar(0,[0,None])
		self.start.set(self.generator.start)
		self.stop = IntegerVar(0,[0,None])
		self.stop.set(self.generator.stop)
		self.step = IntegerVar(1,[1,None])
		self.step.set(self.generator.step)

		Label(self, text='From ').pack(side=LEFT)
		Entry(self, textvariable=self.start, width=5).pack(side=LEFT)
		Label(self, text=' to ').pack(side=LEFT)
		Entry(self, textvariable=self.stop, width=5).pack(side=LEFT)
		Label(self, text=', by adding ').pack(side=LEFT)
		Entry(self, textvariable=self.step, width=5).pack(side=LEFT)
	def save(self):
		self.generator.start = self.start.get()
		self.generator.stop = self.stop.get()
		self.generator.step = self.step.get()
class GeneratorTypeRange(GeneratorType):
	TYPE = 'range'
	EDITOR = GeneratorEditorRange
	@staticmethod
	def validate(save):
		return 'start' in save and isinstance(save['start'], int) \
			and 'stop' in save and isinstance(save['stop'], int) \
			and 'step' in save and isinstance(save['step'], int) and save['step'] != 0
	def __init__(self, save={}):
		self.start = save.get('start',0)
		self.stop = save.get('stop',0)
		self.step = save.get('step',1)
	def count(self):
		return len(xrange(self.start,self.stop+1,self.step))
	def value(self, lookup_value):
		n = lookup_value('n')
		r = xrange(self.start,self.stop+1,self.step)
		if n >= len(r):
			return ''
		return r[n]
	def description(self):
		return '%d to %d, by adding %d' % (self.start,self.stop,self.step)
	def save(self):
		save = GeneratorType.save(self)
		save.update({
			'start': self.start,
			'stop': self.stop,
			'step': self.step
		})
		return save
GeneratorType.TYPES[GeneratorTypeRange.TYPE] = GeneratorTypeRange
class GeneratorEditorMath(GeneratorEditor):
	RESIZABLE = (True,False)
	def __init__(self, parent, generator):
		GeneratorEditor.__init__(self, parent, generator)

		self.math = StringVar()
		self.math.set(self.generator.math)

		Label(self, text='Math:', anchor=W).pack(side=TOP, fill=X)
		Entry(self, textvariable=self.math).pack(side=TOP, fill=X)
	def save(self):
		self.generator.math = self.math.get()
class GeneratorTypeMath(GeneratorType):
	TYPE = 'math'
	EDITOR = GeneratorEditorMath
	@staticmethod
	def validate(save):
		return 'math' in save and isstr(save['math'])
	def __init__(self, save={}):
		self.math = save.get('math', '')
	def count(self):
		return None
	def value(self, lookup_value):
		variable_re = re.compile(r'\$([a-zA-Z0-9_]+)')
		math_re = re.compile(r'^[0-9.+-/*() \t]+$')
		math = variable_re.sub(lambda m: str(lookup_value(m.group(1))), self.math)
		if not math_re.match(math):
			raise PyMSError('Generate', "Invalid math expression '%s' (only numbers, +, -, /, *, and whitespace allowed)" % math)
		try:
			return eval(math)
		except Exception, e:
			raise PyMSError('Generate', "Error evaluating math expression '%s'" % math, exception=e)
	def description(self):
		return self.math
	def save(self):
		save = GeneratorType.save(self)
		save['math'] = self.math
		return save
GeneratorType.TYPES[GeneratorTypeMath.TYPE] = GeneratorTypeMath
class GeneratorTypeListRepeater:
	def count(self, list_size):
		raise
	def index(self, list_size, n):
		raise
class GeneratorTypeListRepeaterDont(GeneratorTypeListRepeater):
	TYPE = 'dont'
	NAME = "Don't Repeat"
	def count(self, list_size):
		return list_size
	def index(self, list_count, n):
		if n >= list_count:
			return None
		return n
class GeneratorTypeListRepeaterRepeatOnce(GeneratorTypeListRepeater):
	TYPE = 'once'
	NAME = 'Once'
	def count(self, list_size):
		return list_size * 2
	def index(self, list_size, n):
		if n >= list_size * 2:
			return None
		return n % list_size
class GeneratorTypeListRepeaterRepeatForever(GeneratorTypeListRepeater):
	TYPE = 'forever'
	NAME = 'Forever'
	def count(self, list_size):
		return None
	def index(self, list_size, n):
		return n % list_size
class GeneratorTypeListRepeaterRepeatLast(GeneratorTypeListRepeater):
	TYPE = 'last_forever'
	NAME = 'Last Forever'
	def count(self, list_size):
		return None
	def index(self, list_size, n):
		return min(n, list_size-1)
class GeneratorTypeListRepeaterRepeatInvertedOnce(GeneratorTypeListRepeater):
	TYPE = 'inverted_once'
	NAME = 'Inverted Once'
	def count(self, list_size):
		return list_size * 2 - 2
	def index(self, list_size, n):
		if n >= list_size * 2 - 2:
			return None
		if n >= list_size:
			return list_size-(n - list_size + 2)
		return n % list_size
class GeneratorTypeListRepeaterRepeatInvertedForever(GeneratorTypeListRepeater):
	TYPE = 'inverted_forever'
	NAME = 'Inverted Forever'
	def count(self, list_size):
		return None
	def index(self, list_size, n):
		i = n % (list_size * 2 - 2)
		if i >= list_size:
			return list_size - (i - list_size + 2)
		return i
class GeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd(GeneratorTypeListRepeater):
	TYPE = 'inverted_once_repeat_end'
	NAME = 'Inverted Once (Repeat End)'
	def count(self, list_size):
		return list_size * 2
	def index(self, list_size, n):
		if n >= list_size * 2:
			return None
		if n >= list_size:
			return list_size-(n % list_size + 1)
		return n % list_size
class GeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd(GeneratorTypeListRepeater):
	TYPE = 'inverted_forever_repeat_end'
	NAME = 'Inverted Forever (Repeat Ends)'
	def count(self, list_size):
		return None
	def index(self, list_size, n):
		if (n / list_size) % 2:
			return list_size-(n % list_size + 1)
		return n % list_size
class GeneratorEditorList(GeneratorEditor):
	RESIZABLE = (True,True)
	REPEATERS = (
		GeneratorTypeListRepeaterDont,
		GeneratorTypeListRepeaterRepeatOnce,
		GeneratorTypeListRepeaterRepeatForever,
		GeneratorTypeListRepeaterRepeatLast,
		GeneratorTypeListRepeaterRepeatInvertedOnce,
		GeneratorTypeListRepeaterRepeatInvertedForever,
		GeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd,
		GeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd
	)
	def __init__(self, parent, generator):
		GeneratorEditor.__init__(self, parent, generator)

		Label(self, text='Values:', anchor=W).pack(side=TOP, fill=X)
		textframe = Frame(self, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=NSEW)
		# self.text.bind('<Control-a>', lambda e: self.after(1, self.selectall))
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		textframe.pack(side=TOP, expand=1, fill=BOTH)

		self.repeater = IntVar()

		Label(self, text='Repeat:', anchor=W).pack(side=TOP, fill=X)
		DropDown(self, self.repeater, [r.NAME for r in GeneratorEditorList.REPEATERS], width=20).pack(side=TOP, fill=X)

		self.text.insert(END, '\n'.join(generator.list))
		for n,repeater in enumerate(GeneratorEditorList.REPEATERS):
			if repeater.TYPE == self.generator.repeater.TYPE:
				self.repeater.set(n)
				break
	def save(self):
		self.generator.list = self.text.get(1.0, END).rstrip('\n').split('\n')
		self.generator.repeater = GeneratorEditorList.REPEATERS[self.repeater.get()]()
class GeneratorTypeList(GeneratorType):
	TYPE = 'list'
	EDITOR = GeneratorEditorList
	REPEATERS = {
		GeneratorTypeListRepeaterDont.TYPE: GeneratorTypeListRepeaterDont,
		GeneratorTypeListRepeaterRepeatOnce.TYPE: GeneratorTypeListRepeaterRepeatOnce,
		GeneratorTypeListRepeaterRepeatForever.TYPE: GeneratorTypeListRepeaterRepeatForever,
		GeneratorTypeListRepeaterRepeatLast.TYPE: GeneratorTypeListRepeaterRepeatLast,
		GeneratorTypeListRepeaterRepeatInvertedOnce.TYPE: GeneratorTypeListRepeaterRepeatInvertedOnce,
		GeneratorTypeListRepeaterRepeatInvertedForever.TYPE: GeneratorTypeListRepeaterRepeatInvertedForever,
		GeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd.TYPE: GeneratorTypeListRepeaterRepeatInvertedOnceRepeatEnd,
		GeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd.TYPE: GeneratorTypeListRepeaterRepeatInvertedForeverRepeatEnd
	}
	@staticmethod
	def validate(save):
		if not 'list' in save and isinstance(save['list'], list) \
				or not 'repeater' in save or not save['repeater'] in GeneratorTypeList.REPEATERS:
			return False
		for val in save['list']:
			if not isstr(val):
				return False
		return True
	def __init__(self, save={}):
		self.list = save.get('list', [])
		self.repeater = GeneratorTypeList.REPEATERS.get(save.get('repeater'), GeneratorTypeListRepeaterDont)()
	def count(self):
		return self.repeater.count(len(self.list))
	def value(self, lookup_value):
		n = self.repeater.index(len(self.list), lookup_value('n'))
		if n == None:
			return ''
		value = self.list[n]
		variable_re = re.compile(r'\$([a-zA-Z0-9_]+)')
		return variable_re.sub(lambda m: str(lookup_value(m.group(1))), value)
	def description(self):
		return 'Items from list: %s' % ', '.join(self.list)
	def save(self):
		save = GeneratorType.save(self)
		save['list'] = list(self.list)
		save['repeater'] = self.repeater.TYPE
		return save
GeneratorType.TYPES[GeneratorTypeList.TYPE] = GeneratorTypeList
class GeneratorVariable:
	def __init__(self, generator, name='variable'):
		self.generator = generator
		self.name = name

class GeneratorVariableEditor(PyMSDialog):
	def __init__(self, parent, variable):
		self.variable = variable
		PyMSDialog.__init__(self, parent, 'Variable Editor', grabwait=True, resizable=variable.generator.EDITOR.RESIZABLE)

	def widgetize(self):
		self.name = StringVar()
		self.name.set(self.variable.name)
		def strip_name(*_):
			strip_re = re.compile(r'[^a-zA-Z0-9_]')
			name = self.name.get()
			stripped = strip_re.sub('', name)
			if stripped != name:
				self.name.set(stripped)
		self.name.trace('w', strip_name)

		Label(self, text='Name:', anchor=W).pack(side=TOP, fill=X, padx=3)
		Entry(self, textvariable=self.name).pack(side=TOP, fill=X, padx=3)

		self.editor = self.variable.generator.EDITOR(self, self.variable.generator)
		self.editor.pack(side=TOP, fill=BOTH, expand=1, padx=3, pady=3)

		buts = Frame(self)
		done = Button(buts, text='Done', command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return done

	def setup_complete(self):
		setting = '%s_editor_window' % self.variable.generator.TYPE
		if 'generator' in self.parent.settings and setting in self.parent.settings['generator']:
			loadsize(self, self.parent.settings['generator'], setting)

	def ok(self):
		self.variable.name = self.parent.unique_name(self.name.get(), self.variable)
		self.editor.save()
		self.parent.update_list()
		PyMSDialog.ok(self)

	def dismiss(self):
		if not 'generator' in self.parent.settings:
			self.parent.settings['generator'] = {}
		setting = '%s_editor_window' % self.variable.generator.TYPE
		savesize(self, self.parent.settings['generator'], setting)
		PyMSDialog.dismiss(self)

class NameDialog(PyMSDialog):
	def __init__(self, parent, title='Name', value='', done='Done', callback=None):
		self.callback = callback
		self.name = StringVar()
		self.name.set(value)
		self.done = done
		PyMSDialog.__init__(self, parent, title, grabwait=True, resizable=(True,False))

	def widgetize(self):
		Label(self, text='Name:', width=30, anchor=W).pack(side=TOP, fill=X, padx=3)
		Entry(self, textvariable=self.name).pack(side=TOP, fill=X, padx=3)

		buts = Frame(self)
		done = Button(buts, text=self.done, command=self.ok)
		done.pack(side=LEFT)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		return done

	def ok(self):
		if self.callback and self.callback(self, self.name.get()) == False:
			return
		PyMSDialog.ok(self)

class ManagePresets(PyMSDialog):
	def __init__(self, parent):
		self.settings = parent.settings
		PyMSDialog.__init__(self, parent, 'Manage Presets', grabwait=True)
	def widgetize(self):
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=EXTENDED, activestyle=DOTBOX, width=30, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda e,l=self.listbox,i=0: self.move_select(e,l,i)),
			('<End>', lambda e,l=self.listbox,i=END: self.move_select(e,l,i)),
			('<Up>', lambda e,l=self.listbox,i=-1: self.move_select(e,l,i)),
			('<Left>', lambda e,l=self.listbox,i=-1: self.move_select(e,l,i)),
			('<Down>', lambda e,l=self.listbox,i=1: self.move_select(e,l,i)),
			('<Right>', lambda e,l=self.listbox,i=-1: self.move_select(e,l,i)),
			('<Prior>', lambda e,l=self.listbox,i=-10: self.move_select(e,l,i)),
			('<Next>', lambda e,l=self.listbox,i=10: self.move_select(e,l,i)),
		]
		for b in bind:
			self.bind(*b)
			self.listbox.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.update_states)
		self.listbox.bind('<Double-Button-1>', self.rename)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, padx=3, pady=3, fill=BOTH, expand=1)

		buts = Frame(self)
		buttons = [
			('test', 'Use Preset', LEFT, 0, self.select),
			('remove', 'Remove Preset', LEFT, (5,0), self.remove),
			('up', 'Move Up', LEFT, (5,0), lambda d=-1: self.move(d)),
			('down', 'Move Down', LEFT, (0,5), lambda d=1: self.move(d)),
			('edit', 'Rename Preset', RIGHT, 0, self.rename),
			('import', 'Import Preset', RIGHT, (0,5), self.iimport),
			('export', 'Export Preset', RIGHT, 0, self.export)
		]
		self.buttons = {}
		for icon,tip,side,padx,callback in buttons:
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			button = Button(buts, image=image, width=20, height=20, command=callback)
			button.image = image
			button.tooltip = Tooltip(button, tip)
			button.pack(side=side, padx=padx)
			self.buttons[icon] = button
		buts.pack(side=TOP, fill=X, padx=3)

		done = Button(self, text='Done', command=self.ok)
		done.pack(side=BOTTOM, padx=3, pady=(0,3))

		self.update_list()

		return done

	def remove(self):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings['generator']['presets'][selected]
		cont = askquestion(parent=self, title='Remove Preset?', message="'%s' will be removed and you won't be able to get it back. Continue?" % preset['name'], default=OK, type=OKCANCEL)
		if cont == 'cancel':
			return
		del self.settings['generator']['presets'][selected]
		self.update_list()

	def export(self):
		if not self.listbox.curselection():
			return
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		path = tkFileDialog.asksaveasfilename(parent=self, title='Export Preset', defaultextension='.txt', filetypes=[('Text Files','*.txt'),('All Files','*')], initialdir=path)
		self._pyms__window_blocking = False
		if not path:
			return
		selected = int(self.listbox.curselection()[0])
		preset = self.settings['generator']['presets'][selected]
		try:
			f = AtomicWriter(path, 'w')
			f.write(json.dumps(preset, indent=4))
			f.close()
		except:
			ErrorDialog(self, PyMSError('Export',"Could not write to file '%s'" % path))

	def iimport(self):
		path = self.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		path = tkFileDialog.askopenfilename(parent=self, title='Import Preset', defaultextension='.txt', filetypes=[('Text Files','*.txt'),('All Files','*')], initialdir=path)
		self._pyms__window_blocking = False
		if not path:
			return
		try:
			preset = None
			try:
				with open(path, 'r') as f:
					preset = json.loads(f.read())
			except:
				raise PyMSError('Import',"Could not read preset '%s'" % path, exception=sys.exc_info())
			if not 'name' in preset or not isstr(preset['name']) \
					or not 'code' in preset or not isstr(preset['code']) \
					or not 'variables' in preset or not isinstance(preset['variables'], list):
				raise PyMSError('Import',"Invalid preset format in file '%s'" % path)
			for variable in preset['variables']:
				if not 'name' in variable or not isstr(variable['name']) \
						or not 'generator' in variable or not isinstance(variable['generator'], dict) \
						or not 'type' in variable['generator'] or not variable['generator']['type'] in GeneratorType.TYPES \
						or not GeneratorType.TYPES[variable['generator']['type']].validate(variable['generator']):
					raise PyMSError('Import',"Invalid preset format in file '%s'" % path)
			copy = 1
			while True:
				check = '%s%s' % (preset['name'],'' if copy == 1 else str(copy))
				for p in self.settings['generator']['presets']:
					if check == p['name']:
						copy += 1
						break
				else:
					break
			if copy > 1:
				preset['name'] += str(copy)
			self.settings['generator']['presets'].insert(0, preset)
			self.update_list()
		except PyMSError, e:
			ErrorDialog(self, e)
	
	def rename(self):
		if not self.listbox.curselection():
			return
		selected = int(self.listbox.curselection()[0])
		def do_rename(window, name):
			for n,preset in enumerate(self.settings['generator']['presets']):
				if preset['name'] == name:
					ErrorDialog(self, PyMSError('Renaming','That name already exists'))
					return
			self.settings['generator']['presets'][selected]['name'] = name
			self.update_list()
		name = self.settings['generator']['presets'][selected]['name']
		NameDialog(self, title='Rename Preset', value=name, done='Rename', callback=do_rename)

	def update_states(self, *_):
		selected = None
		if self.listbox.curselection():
			selected = int(self.listbox.curselection()[0])
		for b in ('test','remove','export','edit'):
			self.buttons[b]['state'] = NORMAL if selected != None else DISABLED
		self.buttons['up']['state'] = NORMAL if selected else DISABLED
		self.buttons['down']['state'] = NORMAL if selected != None and selected+1 < len(self.settings['generator']['presets']) else DISABLED

	def update_list(self):
		select = None
		if self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		for preset in self.settings.get('generator',{}).get('presets',[]):
			self.listbox.insert(END, preset['name'])
		if select != None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move_select(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			print listbox.curselection()
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		return "break"

	def move(self, move):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings['generator']['presets'].pop(selected)
		index = selected+move
		self.settings['generator']['presets'].insert(index, preset)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(index)
		self.update_list()

	def select(self):
		selected = int(self.listbox.curselection()[0])
		preset = self.settings['generator']['presets'][selected]
		if self.parent.load_preset(preset, self):
			self.ok()

class CodeGeneratorDialog(PyMSDialog):
	PRESETS = [
		{
			'name': 'Play Frames', 
			'code': """\
	playfram            $frame
	wait                2""", 
			'variables': [
				{
					'name': 'frame',
					'generator': {
						'type': 'range',
						'start': 0, 
						'stop': 20, 
						'step': 1
					}
				}
			]
		}, 
		{
			'name': 'Play Framesets', 
			'code': """\
	playfram            %frameset
	wait                2""", 
			'variables': [
				{
					'name': 'frameset',
					'generator': {
						'type': 'range',
						'start': 0, 
						'stop': 51, 
						'step': 17
					}
				}
			]
		},
		{
            'name': 'Play Framesets (Advanced)', 
            'code': """\
	playfram            %frame
	wait                2""", 
            'variables': [
                {
                    'name': 'frameset',
                    'generator': {
                        'type': 'range',
                        'start': 0, 
                        'stop': 20, 
                        'step': 1
                    }
                }, 
                {
                    'name': 'frame',
                    'generator': {
                        'type': 'math',
                        'math': '$frameset * 17'
                    }
                }
            ]
        },
        {
            'name': 'Hover Bobbing', 
            'code': """\
	setvertpos          $offset
	waitrand            8 10""", 
            'variables': [
                {
                    'name': 'offset',
                    'generator': {
                        'type': 'list',
                        'list': [
                            '0', 
                            '1', 
                            '2'
                        ], 
                        'repeater': 'inverted_once'
                    }
                }
            ]
        }
	]
	def __init__(self, parent):
		self.variables = []
		self.previewing = False
		self.settings = parent.parent.settings
		if not 'generator' in self.settings:
			self.settings['generator'] = {}
		if not 'presets' in self.settings['generator']:
			self.settings['generator']['presets'] = CodeGeneratorDialog.PRESETS
		PyMSDialog.__init__(self, parent, 'Code Generator', grabwait=True)

	def widgetize(self):
		self.hor_pane = PanedWindow(self,orient=HORIZONTAL)
		leftframe = Frame(self.hor_pane)
		Label(leftframe, text='Variables:', anchor=W).pack(side=TOP, fill=X)
		listframe = Frame(leftframe, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, selectmode=EXTENDED, activestyle=DOTBOX, width=15, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
		bind = [
			('<MouseWheel>', self.scroll),
			('<Home>', lambda e,l=self.listbox,i=0: self.move(e,l,i)),
			('<End>', lambda e,l=self.listbox,i=END: self.move(e,l,i)),
			('<Up>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Left>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Down>', lambda e,l=self.listbox,i=1: self.move(e,l,i)),
			('<Right>', lambda e,l=self.listbox,i=-1: self.move(e,l,i)),
			('<Prior>', lambda e,l=self.listbox,i=-10: self.move(e,l,i)),
			('<Next>', lambda e,l=self.listbox,i=10: self.move(e,l,i)),
		]
		for b in bind:
			self.bind(*b)
			self.listbox.bind(*b)
		self.listbox.bind('<ButtonRelease-1>', self.update_states)
		self.listbox.bind('<Double-Button-1>', self.edit)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(side=TOP, padx=1, pady=1, fill=BOTH, expand=1)
		def add_variable(generator_class, name):
			id = len(self.variables)
			self.variables.append(GeneratorVariable(generator_class(), self.unique_name(name)))
			self.update_list(id)
			self.edit()
		def add_pressed():
			menu = Menu(self, tearoff=0)
			menu.add_command(label="Range", command=lambda: add_variable(GeneratorTypeRange, 'range'))
			menu.add_command(label="Math", command=lambda: add_variable(GeneratorTypeMath, 'math'))
			menu.add_command(label="List", command=lambda: add_variable(GeneratorTypeList, 'list'))
			menu.post(*self.winfo_pointerxy())
		def load_preset_pressed():
			menu = Menu(self, tearoff=0)
			presets = self.settings.get('generator', {}).get('presets',[])
			for n,preset in enumerate(presets):
				if n == 5:
					menu.add_command(label='More...', command=self.manage_presets)
					break
				else:
					menu.add_command(label=preset['name'], command=lambda n=n: self.load_preset(n))
			menu.add_separator()
			menu.add_command(label='Manage Presets', command=self.manage_presets)
			menu.post(*self.winfo_pointerxy())
		buts = Frame(leftframe)
		buttons = [
			('add', 'Add Variable', LEFT, 0, add_pressed),
			('remove', 'Remove Variable', LEFT, 0, self.remove),
			('save', 'Save Preset', LEFT, (5,0), self.save_preset),
			('open', 'Load Preset', LEFT, 0, load_preset_pressed),
			('edit', 'Edit Variable', RIGHT, 0, self.edit),
		]
		self.buttons = {}
		for icon,tip,side,padx,callback in buttons:
			image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % icon))
			button = Button(buts, image=image, width=20, height=20, command=callback)
			button.image = image
			button.tooltip = Tooltip(button, tip)
			button.pack(side=side, padx=padx)
			self.buttons[icon] = button
		buts.pack(side=BOTTOM, fill=X)
		self.hor_pane.add(leftframe, sticky=NSEW)

		self.ver_pane = PanedWindow(self.hor_pane,orient=VERTICAL)
		f = Frame(self.ver_pane)
		Label(f, text='Code:', anchor=W).pack(side=TOP, fill=X)
		textframe = Frame(f, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(textframe, orient=HORIZONTAL)
		vscroll = Scrollbar(textframe)
		self.text = Text(textframe, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.text.grid(sticky=NSEW)
		# self.text.bind('<Control-a>', lambda e: self.after(1, self.selectall))
		hscroll.config(command=self.text.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.text.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		textframe.grid_rowconfigure(0, weight=1)
		textframe.grid_columnconfigure(0, weight=1)
		textframe.pack(side=BOTTOM, expand=1, fill=BOTH)
		self.ver_pane.add(f, sticky=NSEW)
		colors = Frame(self.ver_pane, bd=2, relief=SUNKEN)
		hscroll = Scrollbar(colors, orient=HORIZONTAL)
		vscroll = Scrollbar(colors)
		self.code = Text(colors, height=1, bd=0, undo=1, maxundo=100, wrap=NONE, highlightthickness=0, xscrollcommand=hscroll.set, yscrollcommand=vscroll.set, exportselection=0)
		self.code.grid(sticky=NSEW)
		self.code.orig = self.text._w + '_orig'
		self.tk.call('rename', self.code._w, self.code.orig)
		self.tk.createcommand(self.code._w, self.code_dispatch)
		hscroll.config(command=self.code.xview)
		hscroll.grid(sticky=EW)
		vscroll.config(command=self.code.yview)
		vscroll.grid(sticky=NS, row=0, column=1)
		colors.grid_rowconfigure(0, weight=1)
		colors.grid_columnconfigure(0, weight=1)
		self.ver_pane.add(colors, sticky=NSEW)
		self.hor_pane.add(self.ver_pane, sticky=NSEW)
		self.hor_pane.pack(fill=BOTH, expand=1, padx=3, pady=(0,3))

		def select_all(text):
			text.tag_remove(SEL, '1.0', END)
			text.tag_add(SEL, '1.0', END)
			text.mark_set(INSERT, '1.0')
		self.bind('<Control-a>', lambda *_: select_all(self.code))

		buts = Frame(self)
		self.insert_button = Button(buts, text='Insert', command=self.insert)
		self.insert_button.pack(side=LEFT)
		self.preview_button = Button(buts, text='Preview', command=self.preview)
		self.preview_button.pack(side=LEFT, padx=10)
		Button(buts, text='Cancel', command=self.cancel).pack(side=RIGHT)
		buts.pack(side=BOTTOM, fill=X, padx=3, pady=(0,3))

		self.update_states()

		return self.insert_button

	def setup_complete(self):
		settings = self.settings.get('generator', {})
		if 'window' in settings:
			loadsize(self, settings, 'window')
		def update_panes():
			if 'variables_list' in settings:
				self.hor_pane.sash_place(0, *settings['variables_list'])
			if 'code_box' in settings:
				self.ver_pane.sash_place(0, *settings['code_box'])
		self.after(200, update_panes)

	def code_dispatch(self, operation, *args):
		if operation in ['insert','delete'] and not self.previewing:
			return 'break'
		try:
			return self.tk.call((self.code.orig, operation) + args)
		except TclError:
			return ''

	def update_states(self, *_):
		selection = DISABLED if not self.listbox.curselection() else NORMAL
		self.buttons['remove']['state'] = selection
		self.buttons['save']['state'] = NORMAL if (self.variables and self.text.get(1.0,END)) else DISABLED
		self.buttons['open']['state'] = NORMAL if self.settings.get('generator',{}).get('presets',None) else DISABLED
		self.buttons['edit']['state'] = selection

	def remove(self, *_):
		cont = askquestion(parent=self, title='Remove Variable?', message="The variable settings will be lost.", default=YES, type=YESNO)
		if cont == 'no':
			return
		del self.variables[int(self.listbox.curselection()[0])]
		self.update_list()

	def unique_name(self, name, ignore=None):
		n = 1
		unique = name
		if name == 'n':
			n = 2
			name = 'n2'
		for v in self.variables:
			if v == ignore:
				continue
			if v.name == unique:
				n += 1
				unique = '%s%d' % (name,n)
		return unique

	def edit(self, *_):
		if self.listbox.curselection():
			variable = self.variables[int(self.listbox.curselection()[0])]
			GeneratorVariableEditor(self, variable)

	def insert(self, *_):
		code = self.generate()
		if code == None:
			return
		self.parent.text.insert(INSERT, code)
		self.ok()

	def save_preset(self, *_):
		def do_save(window, name):
			replace = None
			for n,preset in enumerate(self.settings.get('generator',{}).get('presets',[])):
				if preset['name'] == name:
					cont = askquestion(parent=window, title='Overwrite Preset?', message="A preset with the name '%s' already exists. Do you want to overwrite it?" % name, default=YES, type=YESNOCANCEL)
					if cont == 'no':
						return
					elif cont == 'cancel':
						return False
					replace = n
					break
			preset = {
				'name': name,
				'code': self.text.get(1.0,END),
				'variables': []
			}
			if preset['code'].endswith('\r\n'):
				preset['code'] = preset['code'][:-2]
			elif preset['code'].endswith('\n'):
				preset['code'] = preset['code'][:-1]
			for v in self.variables:
				preset['variables'].append({
					'name': v.name,
					'generator': v.generator.save()
				})
			if not 'generator' in self.settings:
				self.settings['generator'] = {}
			if not 'presets' in self.settings['generator']:
				self.settings['generator']['presets'] = []
			if replace == None:
				self.settings['generator']['presets'].insert(0, preset)
			else:
				self.settings['generator']['presets'][replace] = preset
		NameDialog(self, title='Save Preset', done='Save', callback=do_save)
	def load_preset(self, preset, window=None):
		if self.variables or self.text.get(1.0, END).strip():
			cont = askquestion(parent=window if window else self, title='Load Preset?', message="Your current variables and code will be lost.", default=YES, type=YESNO)
			if cont == 'no':
				return False
		if isinstance(preset, int):
			preset = self.settings['generator']['presets'][preset]
		self.text.delete(1.0, END)
		self.text.insert(END, preset['code'])
		self.variables = []
		for var in preset['variables']:
			generator = var['generator']
			self.variables.append(GeneratorVariable(GeneratorType.TYPES[generator['type']](generator), var['name']))
		self.update_list()
		return True

	def manage_presets(self):
		ManagePresets(self)

	def preview(self, *_):
		code = self.generate()
		if code != None:
			self.previewing = True
			self.code.delete(1.0, END)
			self.code.insert(END, code)
			self.previewing = False

	def update_list(self, select=None):
		if select == None and self.listbox.curselection():
			select = self.listbox.curselection()[0]
		y = self.listbox.yview()[0]
		self.listbox.delete(0,END)
		for v in self.variables:
			self.listbox.insert(END, '$%s = %s' % (v.name, v.generator.description()))
		if select != None:
			self.listbox.select_set(select)
		self.listbox.yview_moveto(y)
		self.update_states()

	def scroll(self, e):
		if e.delta > 0:
			self.listbox.yview('scroll', -2, 'units')
		else:
			self.listbox.yview('scroll', 2, 'units')

	def move(self, e, listbox, offset):
		index = 0
		if offset == END:
			index = listbox.size()-2
		elif offset not in [0,END] and listbox.curselection():
			print listbox.curselection()
			index = max(min(listbox.size()-1, int(listbox.curselection()[0]) + offset),0)
		listbox.select_clear(0,END)
		listbox.select_set(index)
		listbox.see(index)
		return "break"

	def generate(self):
		variable_re = re.compile(r'([$%])([a-zA-Z0-9_]+)')
		code = self.text.get(1.0, END)
		generated = ''
		count = None
		for v in self.variables:
			c = v.generator.count()
			if c != None:
				if count == None:
					count = c
				else:
					count = max(count,c)
		if count == None:
			ErrorDialog(self, PyMSError('Generate','No finite variables to generate with'))
			return
		def calculate_variable(variable, values, lookup):
			def calculate_variable_named(name, values, lookup):
				if name in values:
					return values[name]
				for v in self.variables:
					if v.name == name:
						return calculate_variable(v, values, lookup)
				return '$' + name
			if not variable.name in values:
				if variable.name in lookup:
					raise PyMSError('Generate', 'Cyclical reference detected: %s' % ' > '.join(lookup + [variable.name]))
				lookup.append(variable.name)
				values[variable.name] = variable.generator.value(lambda n,v=values,l=lookup: calculate_variable_named(n,v,l))
			return values[variable.name]
		def replace_variable(match, values):
			tohex = (match.group(1) == '%')
			name = match.group(2)
			replacement = values.get(name, match.group(0))
			if tohex:
				try:
					replacement = '0x%02X' % int(replacement)
				except:
					pass
			return str(replacement)
		for n in xrange(count):
			values = {'n': n}
			for v in self.variables:
				if not v.name in values:
					try:
						calculate_variable(v, values, [])
					except PyMSError, e:
						ErrorDialog(self, e)
						return
			generated += variable_re.sub(lambda m: replace_variable(m, values), code)
		return generated

	def dismiss(self):
		if not 'generator' in self.settings:
			self.settings['generator'] = {}
		settings = self.settings['generator']
		savesize(self, settings, 'window')
		settings['variables_list'] = self.hor_pane.sash_coord(0)
		settings['code_box'] = self.ver_pane.sash_coord(0)
		PyMSDialog.dismiss(self)

class CodeEditDialog(PyMSDialog):
	def __init__(self, parent, ids):
		self.ids = ids
		self.decompile = ''
		self.file = None
		self.autocomptext = IScriptBIN.TYPE_HELP.keys() + ['.headerstart','.headerend']
		for o in IScriptBIN.OPCODES:
			self.autocomptext.extend(o[0])
		for a in IScriptBIN.HEADER:
			self.autocomptext.extend(a)
		self.completing = False
		self.complete = [None, 0]
		t = ''
		if ids:
			t = ', '.join([str(i) for i in ids[:5]])
			if len(ids) > 5:
				t += '...'
			t += ' - '
		t += 'IScript Editor'
		PyMSDialog.__init__(self, parent, t, grabwait=False)
		self.findwindow = None
		self.previewer = None

	def widgetize(self):
		buttons = [
			('save', self.save, 'Save (Ctrl+S)', '<Control-s>'),
			('test', self.test, 'Test Code (Ctrl+T)', '<Control-t>'),
			4,
			('export', self.export, 'Export Code (Ctrl+E)', '<Control-e>'),
			('saveas', self.exportas, 'Export As... (Ctrl+Alt+A)', '<Control-Alt-a>'),
			('import', self.iimport, 'Import Code (Ctrl+I)', '<Control-i>'),
			10,
			('find', self.find, 'Find/Replace (Ctrl+F)', '<Control-f>'),
			10,
			('colors', self.colors, 'Color Settings (Ctrl+Alt+C)', '<Control-Alt-c>'),
			10,
			('debug', self.generate, 'Generate Code (Ctrl+G)', '<Control-g>'),
			('insert', self.preview, 'Insert/Preview Window (Ctrl+W)', '<Control-w>'),
			('fwp', self.sounds, 'Sound Previewer (Ctrl+Q)', '<Control-q>'),
		]
		self.bind('<Alt-Left>', lambda e,i=0: self.gotosection(e,i))
		self.bind('<Alt-Right>', lambda e,i=1: self.gotosection(e,i))
		self.bind('<Alt-Up>', lambda e,i=2: self.gotosection(e,i))
		self.bind('<Alt-Down>', lambda e,i=3: self.gotosection(e,i))
		bar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				if btn[3] == True:
					button = Checkbutton(bar, image=image, width=20, height=20, indicatoron=0, variable=btn[1])
				else:
					button = Button(bar, image=image, width=20, height=20, command=btn[1])
					self.bind(btn[3], btn[1])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				if button.winfo_reqwidth() > 26:
					button['width'] = 18
				if button.winfo_reqheight() > 26:
					button['height'] = 18
			else:
				Frame(bar, width=btn).pack(side=LEFT)
		bar.pack(fill=X, padx=2, pady=2)

		self.text = IScriptCodeText(self, self.parent.ibin, self.edited, highlights=self.parent.highlights)
		self.text.pack(fill=BOTH, expand=1, padx=1, pady=1)
		self.text.icallback = self.statusupdate
		self.text.scallback = self.statusupdate
		self.text.acallback = self.autocomplete

		self.status = StringVar()
		self.status.set("Origional ID's: " + ', '.join([str(i) for i in self.ids]))
		self.scriptstatus = StringVar()
		self.scriptstatus.set('Line: 1  Column: 0  Selected: 0')

		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.scriptstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		statusbar.pack(side=BOTTOM, fill=X)

		self.after(1, self.load)

		if 'codeeditwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'codeeditwindow', True)

		return self.text

	def gotosection(self, e, i):
		c = [self.text.tag_prevrange, self.text.tag_nextrange][i % 2]
		t = [('Error','Warning'),('HeaderStart','Block')][i > 1]
		a = c(t[0], INSERT)
		b = c(t[1], INSERT)
		s = None
		if a:
			if not b or self.text.compare(a[0], ['>','<'][i % 2], b[0]):
				s = a
			else:
				s = b
		elif b:
			s = b
		if s:
			self.text.see(s[0])
			self.text.mark_set(INSERT, s[0])

	def autocomplete(self):
		i = self.text.tag_ranges('Selection')
		if i and '\n' in self.text.get(*i):
			return False
		self.completing = True
		self.text.taboverride = ' :'
		def docomplete(s, e, v, t):
			ss = '%s+%sc' % (s,len(t))
			se = '%s+%sc' % (s,len(v))
			self.text.delete(s, ss)
			self.text.insert(s, v)
			self.text.tag_remove('Selection', '1.0', END)
			self.text.tag_add('Selection', ss, se)
			if self.complete[0] == None:
				self.complete = [t, 1, s, se]
			else:
				self.complete[1] += 1
				self.complete[3] = se
		if self.complete[0] != None:
			t,f,s,e = self.complete
		else:
			s,e = self.text.index('%s -1c wordstart' % INSERT),self.text.index('%s -1c wordend' % INSERT)
			t,f = self.text.get(s,e),0
		if t and t[0].lower() in 'abcdefghijklmnopqrstuvwxyz_.':
			ac = list(self.autocomptext)
			head = '1.0'
			while True:
				item = self.text.tag_nextrange('Block', head)
				if not item:
					break
				block = self.text.get(*item)
				if not block in ac:
					ac.append(block)
				head = item[1]
			ac.sort()
			r = False
			matches = []
			for v in ac:
				if v and v.lower().startswith(t.lower()):
					matches.append(v)
			if matches:
				if f < len(matches):
					docomplete(s,e,matches[f],t)
					self.text.taboverride = ' (,):'
				elif self.complete[0] != None:
					docomplete(s,e,t,t)
					self.complete[1] = 0
				r = True
			self.after(1, self.completed)
			return r

	def completed(self):
		self.completing = False

	def statusupdate(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		i = self.text.index(INSERT).split('.') + [0]
		item = self.text.tag_ranges('Selection')
		if item:
			i[2] = len(self.text.get(*item))
		self.scriptstatus.set('Line: %s  Column: %s  Selected: %s' % tuple(i))

	def edited(self):
		if not self.completing:
			self.text.taboverride = False
			self.complete = [None, 0]
		self.editstatus['state'] = NORMAL
		if self.file:
			self.title('IScript Editor [*%s*]' % self.file)

	def cancel(self):
		if self.text.edited:
			save = askquestion(parent=self, title='Save Code?', message="Would you like to save the code?", default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return
				self.save()
		self.ok()

	def save(self, e=None):
		self.parent.iimport(file=self, parent=self)
		self.text.edited = False
		self.editstatus['state'] = DISABLED

	def ok(self):
		savesize(self, self.parent.settings, 'codeeditwindow')
		PyMSDialog.ok(self)

	def checkframes(self, grp):
		if os.path.exists(grp):
			p = grp
		else:
			p = self.parent.mpqhandler.get_file('MPQ:unit\\' + grp)
		try:
			grp = GRP.CacheGRP()
			grp.load_file(p)
		except PyMSError, e:
			return None
		return grp.frames

	def test(self, e=None):
		i = IScriptBIN.IScriptBIN(self.parent.weaponsdat, self.parent.flingydat, self.parent.imagesdat, self.parent.spritesdat, self.parent.soundsdat, self.parent.tbl, self.parent.imagestbl, self.parent.sfxdatatbl)
		try:
			warnings = i.interpret(self, checkframes=self.checkframes)
		except PyMSError, e:
			if e.line != None:
				self.text.see('%s.0' % e.line)
				self.text.tag_add('Error', '%s.0' % e.line, '%s.end' % e.line)
			if e.warnings:
				for w in e.warnings:
					if w.line != None:
						self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			ErrorDialog(self, e)
			return
		if warnings:
			c = False
			for w in warnings:
				if w.line != None:
					if not c:
						self.text.see('%s.0' % w.line)
						c = True
					self.text.tag_add('Warning', '%s.0' % w.line, '%s.end' % w.line)
			WarningDialog(self, warnings, True)
		else:
			askquestion(parent=self, title='Test Completed', message='The code compiles with no errors or warnings.', type=OK)

	def export(self, e=None):
		if not self.file:
			self.exportas()
		else:
			f = open(self.file, 'w')
			f.write(self.text.get('1.0', END))
			f.close()
			self.title('IScript Editor [%s]' % self.file)

	def exportas(self, e=None):
		file = self.parent.select_file('Export Code', False, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if not file:
			return
		self.file = file
		self.export()

	def iimport(self, e=None):
		iimport = self.parent.select_file('Import From', True, '.txt', [('Text Files','*.txt'),('All Files','*')], self)
		if iimport:
			try:
				f = open(iimport, 'r')
				self.text.delete('1.0', END)
				self.text.insert('1.0', f.read())
				self.text.edit_reset()
				f.close()
			except:
				ErrorDialog(self, PyMSError('Import','Could not import file "%s"' % iimport))

	def find(self, e=None):
		if not self.findwindow:
			self.findwindow = FindReplaceDialog(self)
			self.bind('<F3>', self.findwindow.findnext)
		elif self.findwindow.state() == 'withdrawn':
			self.findwindow.deiconify()
		self.findwindow.focus_set()

	def colors(self, e=None):
		c = CodeColors(self)
		if c.cont:
			self.text.setup(c.cont)
			self.parent.highlights = c.cont

	def generate(self, *_):
		CodeGeneratorDialog(self)

	def preview(self, e=None):
		if not self.previewer or self.previewer.state() == 'withdrawn':
			if not self.previewer:
				self.previewer = PreviewerDialog(self)
			self.previewer.updatecurrentimages()
			t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
			if t[0] in PREVIEWER_CMDS[0] and self.previewer.curradio['state'] == NORMAL:
				try:
					f = IScriptBIN.type_frame(2, None, t[1])
				except:
					f = 0
				self.previewer.type.set(0)
				self.previewer.curid.set(0)
				self.previewer.curcmd.set(PREVIEWER_CMDS[0].index(t[0]))
				self.previewer.select(0,0,f)
			elif t[0] in PREVIEWER_CMDS[1]:
				try:
					n = IScriptBIN.type_imageid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(1)
				self.previewer.image.set(n)
				self.previewer.imagecmd.set(PREVIEWER_CMDS[1].index(t[0]))
				self.previewer.select(n,1)
			elif t[0] in PREVIEWER_CMDS[2]:
				try:
					n = IScriptBIN.type_spriteid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(2)
				self.previewer.sprites.set(n)
				self.previewer.spritescmd.set(PREVIEWER_CMDS[2].index(t[0]))
				self.previewer.select(n,2)
			elif t[0] in PREVIEWER_CMDS[3]:
				try:
					n = IScriptBIN.type_flingyid(2, None, t[1])
				except:
					n = 0
				self.previewer.type.set(3)
				self.previewer.flingy.set(n)
				self.previewer.flingycmd.set(PREVIEWER_CMDS[3].index(t[0]))
				self.previewer.select(n,3)
			else:
				self.previewer.select(0,self.previewer.type.get())
			self.previewer.deiconify()
			self.after(50, self.previewer.updateframes)
		self.previewer.focus_set()

	def sounds(self):
		t = re.split('\\s+',self.text.get('%s linestart' % INSERT,'%s lineend' % INSERT).split('#',1)[0].strip())
		i = 0
		if t[0] == 'playsnd':
			try:
				i = IScriptBIN.type_soundid(2, None, t[1])
			except:
				pass
		SoundDialog(self, i)

	def load(self):
		try:
			warnings = self.parent.ibin.decompile(self, ids=self.ids)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		if warnings:
			WarningDialog(self, warnings)

	def write(self, text):
		self.decompile += text

	def readlines(self):
		return self.text.get('1.0', END).split('\n')

	def close(self):
		if self.decompile:
			self.text.insert('1.0', self.decompile.strip())
			self.decompile = ''
			self.text.text.mark_set(INSERT, '1.0')
			self.text.text.see(INSERT)
			self.text.edit_reset()
			self.text.edited = False
			self.editstatus['state'] = DISABLED

	def destroy(self):
		if self.findwindow:
			Toplevel.destroy(self.findwindow)
		if self.previewer:
			Toplevel.destroy(self.previewer)
		Toplevel.destroy(self)

class ImportListDialog(PyMSDialog):
	def __init__(self, parent):
		PyMSDialog.__init__(self, parent, 'List Importing')

	def widgetize(self):
		self.bind('<Insert>', self.add)
		self.bind('<Delete>', self.remove)
		self.bind('<Control-i>', self.iimport)
		buttons = [
			('add', self.add, 'Add File (Insert)', NORMAL),
			('remove', self.remove, 'Remove File (Delete)', DISABLED),
			10,
			('import', self.iimport, 'Import Selected Script (Ctrl+I)', DISABLED),
		]
		self.buttons = {}
		toolbar = Frame(self)
		for btn in buttons:
			if isinstance(btn, tuple):
				image = PhotoImage(file=os.path.join(BASE_DIR,'Images','%s.gif' % btn[0]))
				button = Button(toolbar, image=image, width=20, height=20, command=btn[1], state=btn[3])
				button.image = image
				button.tooltip = Tooltip(button, btn[2], couriernew)
				button.pack(side=LEFT)
				self.buttons[btn[0]] = button
			else:
				Frame(toolbar, width=btn).pack(side=LEFT)
		toolbar.pack(side=TOP, fill=X, padx=2, pady=1)

		##Listbox
		listframe = Frame(self, bd=2, relief=SUNKEN)
		scrollbar = Scrollbar(listframe)
		self.listbox = Listbox(listframe, font=couriernew, activestyle=DOTBOX, yscrollcommand=scrollbar.set, width=1, height=1, bd=0, highlightthickness=0, exportselection=0)
		scrollbar.config(command=self.listbox.yview)
		scrollbar.pack(side=RIGHT, fill=Y)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=1)
		listframe.pack(fill=BOTH, expand=1)

		##Buttons
		buttons = Frame(self)
		ok = Button(buttons, text='Ok', width=10, command=self.ok)
		ok.pack(side=LEFT, padx=3, pady=3)
		self.importbtn = Button(buttons, text='Import All', width=10, command=self.iimportall, state=[NORMAL,DISABLED][not self.parent.imports])
		self.importbtn.pack(padx=3, pady=3)
		buttons.pack()

		if self.parent.imports:
			self.update()
			self.listbox.select_set(0)
			self.listbox.see(0)

		self.minsize(200,150)
		if 'listimportwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'listimportwindow', True)
		return ok

	def select_files(self):
		path = self.parent.settings.get('lastpath', BASE_DIR)
		self._pyms__window_blocking = True
		file = tkFileDialog.askopenfilename(parent=self, title='Add Imports', defaultextension='.txt', filetypes=[('Text Files','*.txt'),('All Files','*')], initialdir=path, multiple=True)
		self._pyms__window_blocking = False
		if file:
			self.parent.settings['lastpath'] = os.path.dirname(file[0])
		return file

	def add(self, key=None):
		iimport = self.select_files()
		if iimport:
			for i in iimport:
				if i not in self.parent.imports:
					self.parent.imports.append(i)
			self.update()
			self.listbox.select_clear(0,END)
			self.listbox.select_set(END)
			self.listbox.see(END)

	def remove(self, key=None):
		if key and self.buttons['remove']['state'] == DISABLED:
			return
		index = int(self.listbox.curselection()[0])
		del self.parent.imports[index]
		if self.parent.imports and index == len(self.parent.imports):
			self.listbox.select_set(index-1)
			self.listbox.see(index-1)
		self.update()

	def iimport(self, key=None):
		if key and self.buttons['import']['state'] == DISABLED:
			return
		self.parent.iimport(file=self.listbox.get(self.listbox.curselection()[0]), parent=self)

	def iimportall(self):
		self.parent.iimport(file=self.parent.imports, parent=self)

	def update(self):
		sel = 0
		if self.listbox.size():
			sel = self.listbox.curselection()[0]
			self.listbox.delete(0, END)
		if self.parent.imports:
			self.buttons['remove']['state'] = NORMAL
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = NORMAL
			for file in self.parent.imports:
				self.listbox.insert(END, file)
			self.listbox.select_set(sel)
		else:
			self.buttons['remove']['state'] = DISABLED
			self.buttons['import']['state'] = NORMAL
			self.importbtn['state'] = DISABLED

	def ok(self):
		savesize(self, self.parent.settings, 'listimportwindow')
		PyMSDialog.ok(self)

class ContinueImportDialog(PyMSDialog):
	def __init__(self, parent, id):
		self.id = id
		self.cont = 0
		PyMSDialog.__init__(self, parent, 'Continue Importing?')

	def widgetize(self):
		Label(self, text="The AI Script with ID '%s' already exists, overwrite it?" % self.id).pack(pady=10)
		frame = Frame(self)
		yes = Button(frame, text='Yes', width=10, command=self.yes)
		yes.pack(side=LEFT, padx=3)
		Button(frame, text='Yes to All', width=10, command=self.yestoall).pack(side=LEFT, padx=3)
		Button(frame, text='No', width=10, command=self.ok).pack(side=LEFT, padx=3)
		Button(frame, text='Cancel', width=10, command=self.cancel).pack(side=LEFT, padx=3)
		frame.pack(pady=10, padx=3)
		return yes

	def yes(self):
		self.cont = 1
		self.ok()

	def yestoall(self):
		self.cont = 2
		self.ok()

	def cancel(self):
		self.cont = 3
		self.ok()

class FindDialog(PyMSDialog):
	def __init__(self, parent):
		self.resettimer = None
		PyMSDialog.__init__(self, parent, 'Find', grabwait=False)

	def widgetize(self):
		self.minsize(330,160)

		self.lists = []
		self.find = StringVar()
		self.regex = IntVar()
		self.casesens = IntVar()
		self.ids = IntVar()

		f = Frame(self)
		Label(f, text='Find: ').pack(side=LEFT)
		self.findentry = TextDropDown(f, self.find, self.parent.settings['findhistory'], 30)
		self.findentry.c = self.findentry['bg']
		self.findentry.pack(side=LEFT,fill=X, expand=1)
		f.pack(fill=X)
		f = Frame(self)
		Checkbutton(f, text='Regex', variable=self.regex).pack(side=LEFT)
		Checkbutton(f, text='Case Sensitive', variable=self.casesens).pack(side=LEFT)
		Checkbutton(f, text='Include ID\'s in Search', variable=self.ids).pack(side=LEFT)
		f.pack()

		self.treelist = TreeList(self, EXTENDED, False)
		self.treelist.bind('<Button-1>', self.action_states)
		self.treelist.pack(fill=BOTH, expand=1)

		buttons = Frame(self)
		self.findb = Button(buttons, text='Find', width=12, command=self.search, default=NORMAL)
		self.findb.pack(side=LEFT, padx=3, pady=3)
		self.addselectb = Button(buttons, text='Add Selection', width=12, command=lambda: self.select(0), state=DISABLED)
		self.addselectb.pack(side=LEFT, padx=3, pady=3)
		self.selectb = Button(buttons, text='Select', width=12, command=lambda: self.select(1), state=DISABLED)
		self.selectb.pack(side=LEFT, padx=3, pady=3)
		Button(buttons, text='Cancel', width=12, command=self.cancel).pack(side=LEFT, padx=3, pady=3)
		buttons.pack()
		self.action_states()

		self.bind('<Return>', self.search)

		if 'findwindow' in self.parent.settings:
			loadsize(self, self.parent.settings, 'findwindow', True)

		return self.findentry

	def action_states(self, e=None):
		if not self.treelist.cur_selection() == -1:
			s = [NORMAL,DISABLED][not self.treelist.cur_selection()]
		else:
			s = DISABLED
		for b in [self.addselectb,self.selectb]:
			b['state'] = s

	def updatecolor(self):
		self.findentry.entry['bg'] = self.findentry.c

	def search(self, _=None):
		self.lists = []
		self.treelist.delete(ALL)
		if not self.find.get() in self.parent.settings['findhistory']:
			self.parent.settings['findhistory'].append(self.find.get())
		if self.regex.get():
			regex = self.find.get()
		else:
			regex = '.*%s.*' % re.escape(self.find.get())
		try:
			r = re.compile(regex, [re.I,0][self.casesens.get()])
		except:
			self.findentry.c = self.findentry.entry['bg']
			self.findentry.entry['bg'] = '#FFB4B4'
			self.resettimer = self.after(1000, self.updatecolor)
			return
		d = [
			('IScript Entries',self.parent.iscriptlist),
			('Images',self.parent.imageslist),
			('Sprites',self.parent.spriteslist),
			('Flingys',self.parent.flingylist),
			('Units',self.parent.unitlist)
		]
		for n,l in d:
			added = False
			for x in range(l.size()):
				t = l.get(x)
				if not self.ids.get():
					t = t[4:]
					if n != 'IScript Entries':
						t = '['.join(t.split('[')[:-1])
				if r.match(t):
					if not added:
						self.treelist.insert('-1', n, True)
						self.lists.append(l)
						added = True
					self.treelist.insert('-1.-1', l.get(x))

	def select(self, set):
		c = []
		for i in self.treelist.cur_selection():
			g,s = int(self.treelist.index(i).split('.')[0]),int(self.treelist.get(i)[:3].lstrip())
			if self.lists[g] == self.parent.iscriptlist:
				s = sorted(self.parent.ibin.headers.keys()).index(s)
			if not g in c:
				if set:
					self.lists[g].select_clear(0,END)
				self.lists[g].see(s)
				c.append(g)
			self.lists[g].select_set(s)
		self.ok()

	def ok(self):
		savesize(self, self.parent.settings, 'findwindow')
		PyMSDialog.ok(self)

class PyICE(Tk):
	def __init__(self, guifile=None):
		self.settings = loadsettings('PyICE',
			{
				'stat_txt':'MPQ:rez\\stat_txt.tbl',
				'imagestbl':'MPQ:arr\\images.tbl',
				'sfxdatatbl':'MPQ:arr\\sfxdata.tbl',
				'unitsdat':'MPQ:arr\\units.dat',
				'weaponsdat':'MPQ:arr\\weapons.dat',
				'flingydat':'MPQ:arr\\flingy.dat',
				'spritesdat':'MPQ:arr\\sprites.dat',
				'imagesdat':'MPQ:arr\\images.dat',
				'sfxdatadat':'MPQ:arr\\sfxdata.dat',
				'findhistory':[],
			}
		)

		#Window
		Tk.__init__(self)
		self.title('PyICE %s (No files loaded)' % LONG_VERSION)
		try:
			self.icon = os.path.join(BASE_DIR, 'Images','PyICE.ico')
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'Images','PyICE.xbm')
			self.wm_iconbitmap(self.icon)
		self.protocol('WM_DELETE_WINDOW', self.exit)
		setup_trace(self, 'PyICE')

		self.file = None
		self.ibin = None
		self.edited = False
		self.tbl = None
		self.imagestbl = None
		self.sfxdatatbl = None
		self.unitsdat = None
		self.weaponsdat = None
		self.flingydat = None
		self.spritesdat = None
		self.imagesdat = None
		self.soundsdat = None

		self.highlights = self.settings.get('highlights', None)
		self.findhistory = []
		self.replacehistory = []
		self.imports = []

		#Toolbar
		buttons = [
			('new', self.new, 'New (Ctrl+N)', NORMAL, 'Ctrl+N'),
			('open', self.open, 'Open (Ctrl+O)', NORMAL, 'Ctrl+O'),
			('opendefault', self.open_default, 'Open Default Scripts (Ctrl+D)', NORMAL, 'Ctrl+D'),
			('save', self.save, 'Save (Ctrl+S)', DISABLED, 'Ctrl+S'),
			('saveas', self.saveas, 'Save As (Ctrl+Alt+A)', DISABLED, 'Ctrl+Alt+A'),
			('close', self.close, 'Close (Ctrl+W)', DISABLED, 'Ctrl+W'),
			10,
			('export', self.export, 'Export Entries (Ctrl+Alt+E)', DISABLED, 'Ctrl+Alt+E'),
			('import', self.iimport, 'Import Entries (Ctrl+Alt+I)', DISABLED, 'Ctrl+Alt+I'),
			('listimport', self.listimport, 'Import a List of Files (Ctrl+L)', DISABLED, 'Ctrl+L'),
			2,
			('find', self.find, 'Find Entries (Ctrl+F)', DISABLED, 'Ctrl+F'),
			2,
			('codeedit', self.codeedit, 'Edit IScript entries (Ctrl+E)', DISABLED, 'Ctrl+E'),
			10,
			('asc3topyai', self.tblbin, 'Manage TBL and DAT files (Ctrl+M)', NORMAL, 'Ctrl+M'),
			10,
			('register', self.register, 'Set as default *.bin editor (Windows Only)', [DISABLED,NORMAL][win_reg], ''),
			('help', self.help, 'Help (F1)', NORMAL, 'F1'),
			('about', self.about, 'About PyICE', NORMAL, ''),
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

		#listbox,etc.
		listframes = Frame(self)
		for n,l in enumerate(['IScript Entries','Images','Sprites',"Flingy's",'Units']):
			f = Frame(listframes)
			Label(f, text=l + ':', anchor=W).pack(fill=X)
			listframe = Frame(f, bd=2, relief=SUNKEN)
			scrollbar = Scrollbar(listframe)
			lb = Listbox(listframe, activestyle=DOTBOX, selectmode=MULTIPLE, font=couriernew, width=1, height=1, bd=0, highlightthickness=0, yscrollcommand=scrollbar.set, exportselection=0)
			if n == 0:
				self.iscriptlist = lb
			elif n == 1:
				self.imageslist = lb
			elif n == 2:
				self.spriteslist = lb
			elif n == 3:
				self.flingylist = lb
			else:
				self.unitlist = lb
			bind = [
				('<MouseWheel>', lambda a,l=lb: self.scroll(a,l)),
				('<Home>', lambda a,l=lb,i=0: self.move(a,l,i)),
				('<End>', lambda a,l=lb,i=END: self.move(a,l,i)),
				('<Up>', lambda a,l=lb,i=-1: self.move(a,l,i)),
				('<Left>', lambda a,l=lb,i=-1: self.move(a,l,i)),
				('<Down>', lambda a,l=lb,i=1: self.move(a,l,i)),
				('<Right>', lambda a,l=lb,i=-1: self.move(a,l,i)),
				('<Prior>', lambda a,l=lb,i=-10: self.move(a,l,i)),
				('<Next>', lambda a,l=lb,i=10: self.move(a,l,i)),
			]
			for b in bind:
				listframe.bind(*b)
			lb.bind('<ButtonRelease-1>', lambda e,l=lb: self.lbclick(e,l))
			scrollbar.bind('<Button-1>', lambda e,l=lb: self.lbclick(e,l))
			scrollbar.config(command=lb.yview)
			scrollbar.pack(side=RIGHT, fill=Y)
			lb.pack(side=LEFT, fill=BOTH, expand=1)
			listframe.pack(fill=BOTH, expand=1)
			Button(f, text='Unselect All', command=lambda l=lb: self.unselect(l)).pack(fill=X)
			f.pack(side=LEFT, fill=BOTH, padx=2, expand=1)
		listframes.pack(fill=BOTH, pady=2, expand=1)

		#Statusbar
		self.status = StringVar()
		self.selectstatus = StringVar()
		statusbar = Frame(self)
		Label(statusbar, textvariable=self.status, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		image = PhotoImage(file=os.path.join(BASE_DIR,'Images','save.gif'))
		self.editstatus = Label(statusbar, image=image, bd=0, state=DISABLED)
		self.editstatus.image = image
		self.editstatus.pack(side=LEFT, padx=1, fill=Y)
		Label(statusbar, textvariable=self.selectstatus, bd=1, relief=SUNKEN, anchor=W).pack(side=LEFT, expand=1, padx=1, fill=X)
		self.status.set('Load or create a BIN.')
		self.selectstatus.set("IScript ID's Selected: None")
		statusbar.pack(side=BOTTOM, fill=X)

		pal = PAL.Palette()
		for p in ['Units','bfire','gfire','ofire','Terrain','Icons']:
			try:
				pal.load_file(self.settings.get('%spal' % p,os.path.join(BASE_DIR, 'Palettes', '%s%spal' % (p,os.extsep))))
			except:
				continue
			PALETTES[p] = pal.palette

		self.use_mod_mpq = self.settings.get('usemodmpq',0)

		if 'window' in self.settings:
			loadsize(self, self.settings, 'window', True)

		self.mpqhandler = MPQHandler(self.settings.get('mpqs',[]))
		if (not 'mpqs' in self.settings or not len(self.settings['mpqs'])) and self.mpqhandler.add_defaults():
			self.settings['mpqs'] = self.mpqhandler.mpqs
		e = self.open_files()
		if e:
			self.tblbin(err=e)

		if guifile:
			self.open(file=guifile)

		start_new_thread(check_update, (self, 'PyICE'))

	def open_files(self):
		self.mpqhandler.open_mpqs()
		err = None
		try:
			tbl = TBL.TBL()
			imagestbl = TBL.TBL()
			sfxdatatbl = TBL.TBL()
			unitsdat = DAT.UnitsDAT()
			weaponsdat = DAT.WeaponsDAT()
			flingydat = DAT.FlingyDAT()
			spritesdat = DAT.SpritesDAT()
			imagesdat = DAT.ImagesDAT()
			soundsdat = DAT.SoundsDAT()
			tbl.load_file(self.mpqhandler.get_file(self.settings['stat_txt']))
			imagestbl.load_file(self.mpqhandler.get_file(self.settings['imagestbl']))
			sfxdatatbl.load_file(self.mpqhandler.get_file(self.settings['sfxdatatbl']))
			unitsdat.load_file(self.mpqhandler.get_file(self.settings['unitsdat']))
			weaponsdat.load_file(self.mpqhandler.get_file(self.settings['weaponsdat']))
			flingydat.load_file(self.mpqhandler.get_file(self.settings['flingydat']))
			spritesdat.load_file(self.mpqhandler.get_file(self.settings['spritesdat']))
			imagesdat.load_file(self.mpqhandler.get_file(self.settings['imagesdat']))
			soundsdat.load_file(self.mpqhandler.get_file(self.settings['sfxdatadat']))
		except PyMSError, e:
			err = e
		else:
			self.tbl = tbl
			self.imagestbl = imagestbl
			self.sfxdatatbl = sfxdatatbl
			self.unitsdat = unitsdat
			self.weaponsdat = weaponsdat
			self.flingydat = flingydat
			self.spritesdat = spritesdat
			self.imagesdat = imagesdat
			self.soundsdat = soundsdat
			for d,x,lb in [('Images',4,self.imageslist),('Sprites',3,self.spriteslist),('Flingy',2,self.flingylist),(self.tbl,1,self.unitlist)]:
				lb.delete(0,END)
				if x == 1:
					dat = [TBL.decompile_string(self.tbl.strings[n]) for n in range(DAT.UnitsDAT.count)]
				else:
					dat = DAT.DATA_CACHE[d + '.txt']
				for n,e in enumerate(dat):
					l = '%03s %s' % (n,e)
					if x > -1:
						l += ' [%s]' % self.selid(x,n)
					lb.insert(END, l)
				if not self.ibin:
					lb['state'] = DISABLED
		self.mpqhandler.close_mpqs()
		return err

	def select_file(self, title, open=True, ext='.bin', filetypes=[('IScripts','*.bin'),('All Files','*')], parent=None):
		if parent == None:
			parent = self
		path = self.settings.get('lastpath', BASE_DIR)
		parent._pyms__window_blocking = True
		file = [tkFileDialog.asksaveasfilename,tkFileDialog.askopenfilename][open](parent=parent, title=title, defaultextension=ext, filetypes=filetypes, initialdir=path)
		parent._pyms__window_blocking = False
		if file:
			self.settings['lastpath'] = os.path.dirname(file)
		return file

	def scroll(self, e, lb):
		if e.delta > 0:
			lb.yview('scroll', -2, 'units')
		else:
			lb.yview('scroll', 2, 'units')

	def move(self, e, lb, a):
		if a == END:
			a = lb.size()-2
		elif a not in [0,END]:
			a = max(min(lb.size()-1, int(lb.curselection()[0]) + a),0)
		lb.select_clear(0,END)
		lb.select_set(a)
		lb.see(a)

	def selid(self, n, i):
		i = int(i)
		if n == 0:
			return i
		if n == 1:
			flingy = self.unitsdat.get_value(i, 'Graphics')
		if n <= 2:
			if n == 2:
				flingy = i
			sprite = self.flingydat.get_value(flingy, 'Sprite')
		if n <= 3:
			if n == 3:
				sprite = i
			image = self.spritesdat.get_value(sprite, 'ImageFile')
		if n <= 4:
			if n == 4:
				image = i
			id = self.imagesdat.get_value(image, 'IscriptID')
		return id

	def selected(self):
		ids = []
		for n,lb in enumerate([self.iscriptlist,self.unitlist,self.flingylist,self.spriteslist,self.imageslist]):
			s = lb.curselection()
			for i in s:
				if n == 0:
					id = int(lb.get(i)[:3].lstrip())
				else:
					id = self.selid(n,i)
				if not id in ids:
					ids.append(id)
		return ids

	def unselect(self, l):
		l.select_clear(0, END)
		self.lbclick()

	def lbclick(self, e=None, lb=None):
		ids = self.selected()
		if ids:
			self.selectstatus.set("IScript ID's Selected: %s" % ', '.join([str(i) for i in ids]))
		else:
			self.selectstatus.set("IScript ID's Selected: None")
		self.action_states()
		if lb:
			lb.focus_set()

	def action_states(self):
		file = [NORMAL,DISABLED][not self.ibin]
		for lb in [self.imageslist,self.spriteslist,self.flingylist,self.unitlist]:
			lb['state'] = file
		for btn in ['save','saveas','close','import','listimport','find','codeedit']:
			self.buttons[btn]['state'] = file
		self.buttons['export']['state'] = [NORMAL,DISABLED][not self.ibin or not self.selected()]

	def unsaved(self):
		if self.ibin and self.edited:
			iscript = self.file
			if not iscript:
				iscript = 'iscript.bin'
			save = askquestion(parent=self, title='Save Changes?', message="Save changes to '%s'?" % iscript, default=YES, type=YESNOCANCEL)
			if save != 'no':
				if save == 'cancel':
					return True
				if self.file:
					self.save()
				else:
					return self.saveas()

	def new(self, key=None):
		if not self.unsaved():
			self.iscriptlist.delete(0,END)
			self.ibin = IScriptBIN.IScriptBIN()
			self.file = None
			self.status.set('Editing new BIN.')
			self.title('PyICE %s (Unnamed.bin)' % LONG_VERSION)
			self.action_states()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def setuplist(self):
		self.iscriptlist.delete(0,END)
		for id in self.ibin.headers.keys():
			if id in self.ibin.extrainfo:
				n = self.ibin.extrainfo[id]
			elif id < len(DAT.DATA_CACHE['IscriptIDList.txt']):
				n = DAT.DATA_CACHE['IscriptIDList.txt'][id]
			else:
				n = 'Unnamed Custom Entry'
			self.iscriptlist.insert(END, '%03s %s' % (id,n))

	def open(self, key=None, file=None):
		if not self.unsaved():
			if file == None:
				file = self.select_file('Open BIN')
				if not file:
					return
			ibin = IScriptBIN.IScriptBIN()
			try:
				ibin.load_file(file)
			except PyMSError, e:
				ErrorDialog(self, e)
				return
			self.ibin = ibin
			self.setuplist()
			self.title('PyICE %s (%s)' % (LONG_VERSION,file))
			self.file = file
			self.status.set('Load Successful!')
			self.action_states()
			self.edited = False
			self.editstatus['state'] = DISABLED

	def open_default(self, key=None):
		self.open(key, os.path.join(BASE_DIR, 'Libs', 'MPQ', 'scripts','iscript.bin'))

	def save(self, key=None):
		if key and self.buttons['save']['state'] != NORMAL:
			return
		if self.file == None:
			self.saveas()
			return
		try:
			self.ibin.compile(self.file)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		self.status.set('Save Successful!')
		self.edited = False
		self.editstatus['state'] = DISABLED

	def saveas(self, key=None):
		if key and self.buttons['saveas']['state'] != NORMAL:
			return
		file = self.select_file('Save BIN As', False)
		if not file:
			return True
		self.file = file
		self.save()

	def iimport(self, key=None, file=None, parent=None):
		if not file:
			file = self.select_file('Import TXT', True, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return
		if parent == None:
			parent = self
		ibin = IScriptBIN.IScriptBIN()
		try:
			if self.ibin.code.keynames:
				s = self.ibin.code.getkey(-1) + 10
			else:
				s = 0
			w = ibin.interpret(file, s)
		except PyMSError, e:
			ErrorDialog(self, e)
			return
		if w:
			w = WarningDialog(self, w, True)
			if not w.cont:
				return
		for id in ibin.headers.keys():
			if id in self.ibin.headers:
				for o in self.ibin.headers[id][2]:
					if o != None and o in self.ibin.offsets:
						self.ibin.remove_code(o,id)
			self.ibin.headers[id] = ibin.headers[id]
		for o,i in ibin.offsets.iteritems():
			if o in self.ibin.offsets:
				self.ibin.offsets[o].extend(i)
			else:
				self.ibin.offsets[o] = i
		c = dict(self.ibin.code.dict)
		for o,cmd in ibin.code.iteritems():
			c[o] = cmd
		k = c.keys()
		k.sort()
		self.ibin.code = odict(c,k)
		self.ibin.extrainfo.update(ibin.extrainfo)
		self.setuplist()
		self.status.set('Import Successful!')
		self.action_states()
		self.edited = True
		self.editstatus['state'] = NORMAL

	def export(self, key=None):
		if key and self.buttons['export']['state'] != NORMAL:
			return
		file = self.select_file('Export TXT', False, '*.txt', [('Text Files','*.txt'),('All Files','*')])
		if not file:
			return True
		try:
			self.ibin.decompile(file, ids=self.selected())
			self.status.set('Export Successful!')
		except PyMSError, e:
			ErrorDialog(self, e)

	def listimport(self, key=None):
		if key and self.buttons['listimport']['state'] != NORMAL:
			return
		ImportListDialog(self)

	def close(self, key=None):
		if key and self.buttons['close']['state'] != NORMAL:
			return
		if not self.unsaved():
			self.iscriptlist.delete(0,END)
			self.ibin = None
			self.title('PyICE %s' % LONG_VERSION)
			self.file = None
			self.status.set('Load or create a BIN.')
			self.edited = False
			self.editstatus['state'] = DISABLED
			self.lbclick()

	def find(self, key=None):
		if key and self.buttons['find']['state'] != NORMAL:
			return
		FindDialog(self)

	def codeedit(self, key=None):
		if key and self.buttons['codeedit']['state'] != NORMAL:
			return
		CodeEditDialog(self, self.selected())

	def tblbin(self, key=None, err=None):
		data = [
			('TBL Settings',[
				('stat_txt.tbl', 'Contains Unit names', 'stat_txt', 'TBL'),
				('images.tbl', 'Contains GPR mpq file paths', 'imagestbl', 'TBL'),
				('sfxdata.tbl', 'Contains Sound mpq file paths', 'sfxdatatbl', 'TBL'),
			]),
			('DAT Settings',[
				('units.dat', 'Contains link to flingy.dat entries', 'unitsdat', 'UnitsDAT'),
				('weapons.dat', 'Contains stat_txt.tbl string entry for weapon names', 'weaponsdat', 'WeaponsDAT'),
				('flingy.dat', 'Contains link to sprite.dat entries', 'flingydat', 'FlingyDAT'),
				('sprites.dat', 'Contains link to images.dat entries', 'spritesdat', 'SpritesDAT'),
				('images.dat', 'Contains link to IScript entries and images.tbl string indexs', 'imagesdat', 'ImagesDAT'),
				('sfxdata.dat', 'Contains sfxdata.tbl string entries for mpq file paths', 'sfxdatadat', 'SoundsDAT'),
			])
		]
		SettingsDialog(self, data, (340,495), err)

	def register(self, e=None):
		try:
			register_registry('PyICE','','bin',os.path.join(BASE_DIR, 'PyICE.pyw'),os.path.join(BASE_DIR,'Images','PyICE.ico'))
		except PyMSError, e:
			ErrorDialog(self, e)

	def help(self, e=None):
		webbrowser.open(os.path.join(BASE_DIR, 'Docs', 'PyICE.html'))

	def about(self, key=None):
		AboutDialog(self, 'PyICE', LONG_VERSION)

	def exit(self, e=None):
		if not self.unsaved():
			savesize(self, self.settings)
			self.settings['highlights'] = self.highlights
			self.settings['usemodmpq'] = self.use_mod_mpq
			savesettings('PyICE', self.settings)
			self.destroy()

def main():
	import sys
	if not sys.argv or (len(sys.argv) == 1 and os.path.basename(sys.argv[0]).lower() in ['','pyice.py','pyice.pyw','pyice.exe']):
		gui = PyICE()
		startup(gui)
	else:
		p = optparse.OptionParser(usage='usage: PyICE [options] <inp|iscriptin> [out|iscriptout]', version='PyICE %s' % LONG_VERSION)
		p.add_option('-d', '--decompile', action='store_true', dest='convert', help="Decompile iscripts from iscript.bin [default]", default=True)
		p.add_option('-c', '--compile', action='store_false', dest='convert', help="Compile iscripts to an iscript.bin")
		p.add_option('-a', '--weapons', help="Specify your own weapons.dat file for weapon data lookups [default: Libs\\MPQ\\arr\\weapons.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'weapons.dat'))
		p.add_option('-l', '--flingy', help="Specify your own flingy.dat file for flingy data lookups [default: Libs\\MPQ\\arr\\flingy.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'flingy.dat'))
		p.add_option('-i', '--images', help="Specify your own images.dat file for image data lookups [default: Libs\\MPQ\\arr\\images.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'images.dat'))
		p.add_option('-p', '--sprites', help="Specify your own sprites.dat file for sprite data lookups [default: Libs\\MPQ\\arr\\sprite.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'sprites.dat'))
		p.add_option('-f', '--sfxdata', help="Specify your own sfxdata.dat file for sound data lookups [default: Libs\\MPQ\\arr\\sfxdata.dat]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'sfxdata.dat'))
		p.add_option('-x', '--stattxt', help="Used to signify the stat_txt.tbl file to use [default: Libs\\MPQ\\rez\\stat_txt.tbl]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'rez','stat_txt.tbl'))
		p.add_option('-m', '--imagestbl', help="Used to signify the images.tbl file to use [default: Libs\\MPQ\\arr\\images.tbl]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'images.tbl'))
		p.add_option('-t', '--sfxdatatbl', help="Used to signify the sfxdata.tbl file to use [default: Libs\\MPQ\\arr\\sfxdata.tbl]", default=os.path.join(BASE_DIR, 'Libs', 'MPQ', 'arr', 'sfxdata.tbl'))
		p.add_option('-s', '--scripts', help="A list of iscript ID's to decompile (seperated by commas) [default: All]", default='')
		p.add_option('-b', '--iscript', help="Used to signify the base iscript.bin file to compile on top of", default='')
		p.add_option('-r', '--reference', action='store_true', help="When decompiling, put a reference for commands and parameters [default: Off]", default=False)
		p.add_option('-w', '--hidewarns', action='store_true', help="Hides any warning produced by compiling your code [default: Off]", default=False)
		p.add_option('--gui', help="Opens a file with the GUI", default='')
		opt, args = p.parse_args()
		if opt.gui:
			gui = PyICE(opt.gui)
			startup(gui)
		else:
			if not len(args) in [1,2]:
				p.error('Invalid amount of arguments')
			path = os.path.dirname(args[0])
			if not path:
				path = os.path.abspath('')
			if len(args) == 1:
				if opt.convert:
					ext = 'txt'
				else:
					ext = 'bin'
				args.append('%s%s%s' % (os.path.join(path,os.extsep.join(os.path.basename(args[0]).split(os.extsep)[:-1])), os.extsep, ext))
			warnings = []
			try:
				if opt.convert:
					if opt.scripts:
						ids = []
						for i in opt.scripts.split(','):
							ids.append(i)
					else:
						ids = None
					print "Loading weapons.dat '%s', flingy.dat '%s', images.dat '%s', sprites.dat '%s', sdxdata.dat '%s', stat_txt.tbl '%s', images.tbl '%s', and sfxdata.tbl '%s'" % (opt.weapons,opt.flingy,opt.sprites,opt.images,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					ibin = IScriptBIN.IScriptBIN(opt.weapons,opt.flingy,opt.images,opt.sprites,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					print " - Loading finished successfully\nReading BIN '%s'..." % args[0]
					ibin.load_file(args[0])
					print " - BIN read successfully\nWriting iscript entries to '%s'..." % args[1]
					ibin.decompile(args[1],opt.reference,ids)
					print " - '%s' written succesfully" % args[1]
				else:
					print "Loading weapons.dat '%s', flingy.dat '%s', images.dat '%s', sprites.dat '%s', sdxdata.dat '%s', stat_txt.tbl '%s', images.tbl '%s', and sfxdata.tbl '%s'" % (opt.weapons,opt.flingy,opt.sprites,opt.images,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					ibin = IScriptBIN.IScriptBIN(opt.weapons,opt.flingy,opt.images,opt.sprites,opt.sfxdata,opt.stattxt,opt.imagestbl,opt.sfxdatatbl)
					print " - Loading finished successfully"
					if opt.iscript:
						print "Loading base iscript.bin '%s'..." % os.path.abspath(opt.iscript)
						ibin.load_file(os.path.abspath(opt.iscript))
						print " - iscript.bin read successfully"
					print "Interpreting file '%s'..." % args[0]
					warnings.extend(ibin.interpret(args[0]))
					print " - '%s' read successfully\nCompiling file '%s' to iscript.bin '%s'..." % (args[0], args[0], args[1])
					ibin.compile(args[1])
					print " - iscript.bin '%s' written succesfully" % args[1]
				if not opt.hidewarns:
					for warning in warnings:
						print repr(warning)
			except PyMSError, e:
				if warnings and not opt.hidewarns:
					for warning in warnings:
						print repr(warning)
				print repr(e)

if __name__ == '__main__':
	main()