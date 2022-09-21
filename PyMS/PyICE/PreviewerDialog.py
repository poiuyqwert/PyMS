
from ..FileFormats import IScriptBIN
from ..FileFormats import Palette
from ..FileFormats import GRP
from ..FileFormats.MPQ.MPQ import MPQ

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.DropDown import DropDown
from ..Utilities.IntegerVar import IntegerVar
from ..Utilities.PyMSError import PyMSError
from ..Utilities import Assets
from ..Utilities.Toolbar import Toolbar

import os

PREVIEWER_CMDS = [[],[],[],[]]
for n,p in IScriptBIN.OPCODES:
	if IScriptBIN.type_frame in p:
		PREVIEWER_CMDS[0].extend(n)
	if IScriptBIN.type_imageid in p:
		PREVIEWER_CMDS[1].extend(n)
	if IScriptBIN.type_spriteid in p:
		PREVIEWER_CMDS[2].extend(n)
	if IScriptBIN.type_flingyid in p:
		PREVIEWER_CMDS[3].extend(n)

PALETTES = {}
GRP_CACHE = {}

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
			for i in range(self.toplevel.imagesdat.entry_count()):
				if self.toplevel.imagesdat.get_entry(i).iscript_id == n[1]:
					cur.append('['.join(self.toplevel.imageslist.get(i).split('[')[:-1]))
			self.curdd.setentries(cur)
			if cur:
				return
		self.nocur()

	def widgetize(self):
		left = Frame(self)
		c = [
			(0, "Current IScript's images", self.curid, self.curcmd, [], DISABLED),
			(1, 'Images.dat entries', self.image, self.imagecmd, self.getlist(self.toplevel.imageslist,self.toplevel.imagesdat.entry_count()), NORMAL),
			(2, 'Sprites.dat entries', self.sprites, self.spritescmd, self.getlist(self.toplevel.spriteslist,self.toplevel.spritesdat.entry_count()), NORMAL),
			(3, 'Flingy.dat entries', self.flingys, self.flingyscmd, self.getlist(self.toplevel.flingylist,self.toplevel.flingydat.entry_count()), NORMAL),
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
		self.overwrite.set(self.toplevel.settings.previewer.get('overwrite',0))
		self.closeafter = IntVar()
		self.closeafter.set(self.toplevel.settings.previewer.get('closeafter',0))
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
		self.showpreview.set(self.toplevel.settings.previewer.get('showpreview',1))
		p = Frame(right)
		self.preview = Canvas(p, width=257, height=257, background='#000000')
		self.preview.pack()
		self.scroll = Scrollbar(p, orient=HORIZONTAL, command=self.selectframe)
		self.scroll.set(0,1)
		self.scroll.pack(fill=X)
		p.pack()

		self.toolbar = Toolbar(right)
		self.toolbar.add_button(Assets.get_image('begin'), lambda: self.frameset(0), 'Jump to first frame', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('frw'), lambda: self.frameset(1), 'Jump 17 frames Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('rw'), lambda: self.frameset(2), 'Jump 1 frame Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('frwp'), lambda: self.frameset(3), 'Play every 17th frame going Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('rwp'), lambda: self.frameset(4), 'Play every frame going Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('stop'), lambda: self.frameset(5), 'Stop playing frames', enabled=False, tags='is_playing'),
		self.toolbar.add_button(Assets.get_image('fwp'), lambda: self.frameset(6), 'Play every frame going Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('ffwp'), lambda: self.frameset(7), 'Play every 17th frame going Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('fw'), lambda: self.frameset(8), 'Jump 1 frame Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('ffw'), lambda: self.frameset(9), 'Jump 17 frames Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('end'), lambda: self.frameset(10), 'Jump to last frame', enabled=False, tags='can_preview')
		self.toolbar.pack(padx=1, pady=3)

		self.prevspeed = IntegerVar(self.toplevel.settings.previewer.get('previewspeed', 150), [1,5000])
		self.showpreview = IntVar()
		self.showpreview.set(self.toplevel.settings.previewer.get('showpreview',1))
		self.looppreview = IntVar()
		self.looppreview.set(self.toplevel.settings.previewer.get('looppreview',1))
		self.prevfrom = IntegerVar(0,[0,0])
		self.prevto = IntegerVar(0,[0,0])

		opts = Frame(right)
		speedview = Frame(opts)
		Checkbutton(speedview, text='Show Preview at Speed:', variable=self.showpreview, command=self.display).pack(side=LEFT)
		Entry(speedview, textvariable=self.prevspeed, font=Font.fixed(), width=4).pack(side=LEFT)
		Label(speedview, text='ms').pack(side=LEFT)
		speedview.grid()
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(column=1, row=0) # , command=self.drawpreview
		s = Frame(opts)
		Label(s, text='Preview Between: ').pack(side=LEFT)
		self.prevstart = Entry(s, textvariable=self.prevfrom, font=Font.fixed(), width=3, state=DISABLED)
		self.prevstart.pack(side=LEFT)
		Label(s, text=' - ').pack(side=LEFT)
		self.prevend = Entry(s, textvariable=self.prevto, font=Font.fixed(), width=3, state=DISABLED)
		self.prevend.pack(side=LEFT)
		s.grid(row=1, columnspan=2)
		opts.pack(fill=X)
		right.pack(side=LEFT, fill=Y, expand=1)

		if not PALETTES:
			pal = Palette.Palette()
			for palname in ['Units','bfire','gfire','ofire','Terrain','Icons']:
				try:
					
					pal.load_file(self.toplevel.settings.palettes.get(palname,Assets.palette_file_path('%s%spal' % (palname,os.extsep))))
				except Exception as e:
					continue
				PALETTES[palname] = pal.palette

		return ok

	def display(self):
		self.drawpreview()
		self.action_states()
		self.updateframes()

	def action_states(self):
		can_preview = not not (self.curgrp and self.curgrp[2] > 1 and self.showpreview.get())
		self.toolbar.tag_enabled('can_preview', can_preview)

		is_playing = not not self.play
		self.toolbar.tag_enabled('is_playing', is_playing)

	# TODO: Make this better
	def frameset(self, n):
		if not n in [3,4,5,6,7]:
			if n in [0,10]:
				s = [self.curgrp[2]-1,0][not n]
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
			self.speed = [-17,-1,None,1,17][n - 3]
			self.play = self.after(int(self.prevspeed.get()), self.playframe)
		elif self.speed or self.play:
			self.stopframe()
		self.action_states()

	def stopframe(self):
		if self.play:
			self.speed = None
			self.after_cancel(self.play)
			self.play = None
			self.action_states()

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
			c = [IScriptBIN.type_imageid,IScriptBIN.type_spriteid,IScriptBIN.type_flingyid][t-1]
			lb = [self.toplevel.imageslist,self.toplevel.spriteslist,self.toplevel.flingylist][t-1]
			i = c(1, self.toplevel, int(lb.get([self.image,self.sprites,self.flingys][t-1].get()).strip().split(' ')[0]))
		else:
			i = IScriptBIN.type_frame(1, None, self.previewing[1])
		c = PREVIEWER_CMDS[t][[self.curcmd,self.imagecmd,self.spritescmd,self.flingyscmd][t].get()]
		longest_opcode = max([len(o[0][0]) for o in IScriptBIN.OPCODES] + [13]) + 1
		t = '\t%s%s\t%s' % (c,' ' * (longest_opcode-len(c)),i[0])
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
		if MPQ.supported() and pal in PALETTES:
			p = Assets.mpq_file_path(*path)
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
					except PyMSError:
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
			i = self.toplevel.spritesdat.get_entry(int(self.toplevel.spriteslist.get(s).strip().split(' ')[0])).image
		elif t == 3:
			i = self.toplevel.spritesdat.get_entry(self.toplevel.flingydat.get_entry(int(self.toplevel.flingylist.get(s).strip().split(' ')[0])).sprite).image
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
				g = self.toplevel.imagesdat.get_entry(i).grp_file
				if g:
					f = self.toplevel.imagestbl.strings[g-1][:-1]
					if f.startswith('thingy\\tileset\\'):
						p = 'Terrain'
					else:
						p = 'Units'
						if self.toplevel.imagesdat.get_entry(i).draw_function == 9 and self.toplevel.imagesdat.get_entry(i).remapping and self.toplevel.imagesdat.get_entry(i).remapping < 4:
							p = ['o','b','g'][self.toplevel.imagesdat.get_entry(i).remapping-1] + 'fire'
					sprite = self.grp(i,p,self.previewing[1],'unit',f)
					if sprite:
						self.preview.create_image(130, 130, image=sprite[0])
			else:
				self.previewing = None

	def destroy(self):
		self.stopframe()
		self.toplevel.settings.previewer.overwrite = self.overwrite.get()
		self.toplevel.settings.previewer.closeafter = self.closeafter.get()
		self.toplevel.settings.previewer.showpreview = self.showpreview.get()
		self.toplevel.settings.previewer.previewspeed = self.prevspeed.get()
		self.toplevel.settings.previewerlooppreview = self.looppreview.get()
		PyMSDialog.withdraw(self)
