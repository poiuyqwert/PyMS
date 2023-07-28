
from __future__ import annotations

from .Delegates import MainDelegate

from ..FileFormats import IScriptBIN
from ..FileFormats import Palette
from ..FileFormats import GRP
from ..FileFormats import DAT
from ..FileFormats.MPQ.MPQ import MPQ
from ..FileFormats.Images import RawPalette

from ..Utilities.UIKit import *
from ..Utilities.PyMSDialog import PyMSDialog
from ..Utilities.PyMSError import PyMSError
from ..Utilities import Assets

import os, re
from enum import Enum, Flag
from dataclasses import dataclass

from typing import Callable, cast

class EntryType(Enum):
	iscript = 0
	images_dat = 1
	sprites_dat = 2
	flingy_dat = 3

PREVIEWER_CMDS: dict[EntryType, list[str]] = {
	EntryType.iscript: [],
	EntryType.images_dat: [],
	EntryType.sprites_dat: [],
	EntryType.flingy_dat: []
}
for n,p in IScriptBIN.OPCODES:
	if IScriptBIN.type_frame in p:
		PREVIEWER_CMDS[EntryType.iscript].extend(n)
	if IScriptBIN.type_imageid in p:
		PREVIEWER_CMDS[EntryType.images_dat].extend(n)
	if IScriptBIN.type_spriteid in p:
		PREVIEWER_CMDS[EntryType.sprites_dat].extend(n)
	if IScriptBIN.type_flingyid in p:
		PREVIEWER_CMDS[EntryType.flingy_dat].extend(n)

PALETTES: dict[str, RawPalette] = {}
GRP_CACHE: dict[str, dict[int, dict[str, Image]]] = {}

@dataclass
class Preview:
	image_id: int
	frame: int
	grp: GRP.CacheGRP | None

	def __eq__(self, other) -> bool:
		if not isinstance(other, Preview):
			return False
		return other.image_id == self.image_id and other.frame == self.frame

	def next_frame(self, frame: int) -> Preview:
		return Preview(self.image_id, frame, self.grp)

	def next_entry(self, image_id: int, frame: int) -> Preview:
		return Preview(image_id, frame, self.grp)

class FrameSet(Flag):
	first               = 1 << 0
	prev_frameset       = 1 << 1
	prev_frame          = 1 << 2
	play_prev_framesets = 1 << 3
	play_prev_frames    = 1 << 4
	stop                = 1 << 5
	play_next_frames    = 1 << 6
	play_next_framesets = 1 << 7
	next_frame          = 1 << 8
	next_frameset       = 1 << 9
	last                = 1 << 10

	PLAY = play_prev_framesets | play_prev_frames | play_next_frames | play_next_framesets

class PreviewerDialog(PyMSDialog):
	def __init__(self, parent: Misc, delegate: MainDelegate, text: Text) -> None:
		self.delegate = delegate
		self.text = text
		self.previewing: Preview = Preview(0, 0, None)
		self.previewnext: Preview | None = None
		self.timer: str | None = None
		self.type = IntVar()
		self.curid = IntVar()
		self.curcmd = IntVar()
		self.image = IntVar()
		self.imagecmd = IntVar()
		self.sprites = IntVar()
		self.spritescmd = IntVar()
		self.flingys = IntVar()
		self.flingyscmd = IntVar()
		self.grp_frame = StringVar()
		self.grp_frame.set('Frame: 0 / 0')
		self.speed = 0
		self.play: str | None = None
		PyMSDialog.__init__(self, parent, "Graphics Insert/Preview", grabwait=False, resizable=(False, False))

	def nocur(self) -> None:
		if self.curradio and self.curradio['state'] == NORMAL:
			self.curradio['state'] = DISABLED
			self.curdd['state'] = DISABLED
			self.curcmddd['state'] = DISABLED
		if self.type.get() == EntryType.iscript.value:
			self.type.set(EntryType.images_dat.value)

	def getlist(self, lb: ScrolledListbox, c: int) -> list[str]:
		return ['['.join(lb.get(i).split('[')[:-1]) for i in range(c)]

	def updatecurrentimages(self) -> None:
		r = self.text.tag_prevrange('HeaderStart',INSERT)
		if not r:
			r = self.text.tag_nextrange('HeaderStart',INSERT)
		if not r:
			self.nocur()
			return
		n = re.split('\\s+',self.text.get('%s +1lines linestart' % r[0],'%s +1lines lineend' % r[1]))
		name = n[0]
		try:
			id = int(n[1])
		except:
			self.nocur()
			return
		if name == 'IsId' and id >= 0 and id <= 411:
			if self.curradio and self.curradio['state'] == DISABLED:
				self.curradio['state'] = NORMAL
				self.curdd['state'] = NORMAL
				self.curcmddd['state'] = NORMAL
			cur = []
			for i in range(self.delegate.imagesdat.entry_count()):
				if self.delegate.imagesdat.get_entry(i).iscript_id == id:
					cur.append('['.join(self.delegate.imageslist.get(i).split('[')[:-1]))
			self.curdd.setentries(cur)
			if cur:
				return
		self.nocur()

	def widgetize(self) -> Misc | None:
		left = Frame(self)
		entry_details: list[tuple[EntryType, str, IntVar, IntVar, list[str], WidgetState]] = [
			(EntryType.iscript, "Current IScript's images", self.curid, self.curcmd, [], DISABLED),
			(EntryType.images_dat, 'Images.dat entries', self.image, self.imagecmd, self.getlist(self.delegate.imageslist,self.delegate.imagesdat.entry_count()), NORMAL),
			(EntryType.sprites_dat, 'Sprites.dat entries', self.sprites, self.spritescmd, self.getlist(self.delegate.spriteslist,self.delegate.spritesdat.entry_count()), NORMAL),
			(EntryType.flingy_dat, 'Flingy.dat entries', self.flingys, self.flingyscmd, self.getlist(self.delegate.flingylist,self.delegate.flingydat.entry_count()), NORMAL),
		]
		for entry_type,name,id_variable,cmd_var,entries,state in entry_details:
			Label(left, text=name + ":", anchor=W).pack(fill=X)
			f = Frame(left)
			df = Frame(f)
			def type_select_callback(id_variable: IntVar, entry_type: EntryType) -> Callable[[], None]:
				def select() -> None:
					self.select(id_variable.get(), entry_type)
				return select
			def id_select_callback(entry_type: EntryType) -> Callable[[int], None]:
				def select(id: int) -> None:
					self.select(id, entry_type)
				return select
			if entry_type == EntryType.iscript:
				self.curradio = Radiobutton(f, text='', variable=self.type, command=type_select_callback(id_variable, entry_type), value=entry_type.value, state=state)
				self.curradio.pack(side=LEFT)
				self.curdd = DropDown(df, id_variable, entries, id_select_callback(entry_type), 30, state=state)
				self.curdd.pack()
				self.curcmddd = DropDown(df, cmd_var, PREVIEWER_CMDS[entry_type], width=30, state=state)
				self.curcmddd.pack()
			else:
				Radiobutton(f, text='', variable=self.type, command=type_select_callback(id_variable, entry_type), value=entry_type.value, state=state).pack(side=LEFT)
				DropDown(df, id_variable, entries, id_select_callback(entry_type), 30, state=state).pack()
				DropDown(df, cmd_var, PREVIEWER_CMDS[entry_type], width=30, state=state).pack()
			df.pack(side=LEFT)
			f.pack()
		self.overwrite = IntVar()
		self.overwrite.set(self.delegate.settings.previewer.get('overwrite',0))
		self.closeafter = IntVar()
		self.closeafter.set(self.delegate.settings.previewer.get('closeafter',0))
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
		Label(f, textvariable=self.grp_frame, anchor=W).pack(side=LEFT)
		f.pack(fill=X)
		self.showpreview = IntVar()
		self.showpreview.set(self.delegate.settings.previewer.get('showpreview',1))
		p = Frame(right)
		self.preview = Canvas(p, width=257, height=257, background='#000000', theme_tag='preview') # type: ignore[call-arg]
		self.preview.pack()
		self.scroll = Scrollbar(p, orient=HORIZONTAL, command=self.selectframe)
		self.scroll.set(0,1)
		self.scroll.pack(fill=X)
		p.pack()

		self.toolbar = Toolbar(right)
		self.toolbar.add_button(Assets.get_image('begin'), lambda: self.frameset(FrameSet.first), 'Jump to first frame', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('frw'), lambda: self.frameset(FrameSet.prev_frameset), 'Jump 17 frames Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('rw'), lambda: self.frameset(FrameSet.prev_frame), 'Jump 1 frame Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('frwp'), lambda: self.frameset(FrameSet.play_prev_framesets), 'Play every 17th frame going Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('rwp'), lambda: self.frameset(FrameSet.play_prev_frames), 'Play every frame going Left', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('stop'), lambda: self.frameset(FrameSet.stop), 'Stop playing frames', enabled=False, tags='is_playing'),
		self.toolbar.add_button(Assets.get_image('fwp'), lambda: self.frameset(FrameSet.play_next_frames), 'Play every frame going Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('ffwp'), lambda: self.frameset(FrameSet.play_next_framesets), 'Play every 17th frame going Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('fw'), lambda: self.frameset(FrameSet.next_frame), 'Jump 1 frame Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('ffw'), lambda: self.frameset(FrameSet.next_frameset), 'Jump 17 frames Right', enabled=False, tags='can_preview'),
		self.toolbar.add_button(Assets.get_image('end'), lambda: self.frameset(FrameSet.last), 'Jump to last frame', enabled=False, tags='can_preview')
		self.toolbar.pack(padx=1, pady=3)

		self.prevspeed = IntegerVar(self.delegate.settings.previewer.get('previewspeed', 150), [1,5000])
		self.showpreview = IntVar()
		self.showpreview.set(self.delegate.settings.previewer.get('showpreview',1))
		self.looppreview = IntVar()
		self.looppreview.set(self.delegate.settings.previewer.get('looppreview',1))
		self.prevfrom = IntegerVar(0,[0,0])
		self.prevto = IntegerVar(0,[0,0])

		opts = Frame(right)
		speedview = Frame(opts)
		Checkbutton(speedview, text='Show Preview at Speed:', variable=self.showpreview, command=self.display).pack(side=LEFT)
		Entry(speedview, textvariable=self.prevspeed, font=Font.fixed(), width=4).pack(side=LEFT)
		Label(speedview, text='ms').pack(side=LEFT)
		speedview.grid()
		Checkbutton(opts, text='Loop Preview', variable=self.looppreview).grid(column=1, row=0) # , command=self.drawpreview
		r = Frame(opts)
		Label(r, text='Preview Between: ').pack(side=LEFT)
		self.prevstart = Entry(r, textvariable=self.prevfrom, font=Font.fixed(), width=3, state=DISABLED)
		self.prevstart.pack(side=LEFT)
		Label(r, text=' - ').pack(side=LEFT)
		self.prevend = Entry(r, textvariable=self.prevto, font=Font.fixed(), width=3, state=DISABLED)
		self.prevend.pack(side=LEFT)
		r.grid(row=1, columnspan=2)
		opts.pack(fill=X)
		right.pack(side=LEFT, fill=Y, expand=1)

		if not PALETTES:
			pal = Palette.Palette()
			for palname in ['Units','bfire','gfire','ofire','Terrain','Icons']:
				try:
					
					pal.load_file(self.delegate.settings.palettes.get(palname,Assets.palette_file_path('%s%spal' % (palname,os.extsep))))
				except Exception as e:
					continue
				PALETTES[palname] = pal.palette

		return ok

	def entry_type(self) -> EntryType:
		return EntryType(self.type.get())

	def display(self) -> None:
		self.drawpreview()
		self.action_states()
		self.updateframes()

	def action_states(self) -> None:
		can_preview = not not (self.previewing and self.previewing.grp and self.previewing.grp.frames > 1 and self.showpreview.get())
		self.toolbar.tag_enabled('can_preview', can_preview)

		is_playing = not not self.play
		self.toolbar.tag_enabled('is_playing', is_playing)

	def frameset(self, frame_set: FrameSet) -> None:
		if not self.previewing.grp:
			return
		if frame_set == FrameSet.stop:
			self.stopframe()
		elif frame_set & FrameSet.PLAY:
			if n == FrameSet.play_prev_framesets:
				self.speed = -17
			elif n == FrameSet.play_prev_frames:
				self.speed = -1
			elif n == FrameSet.play_next_frames:
				self.speed = 1
			elif n == FrameSet.play_next_framesets:
				self.speed = 17
			self.play = self.after(int(self.prevspeed.get()), self.playframe)
		else:
			s: int
			if n == FrameSet.first:
				s = 0
			elif n == FrameSet.last:
				s = self.previewing.grp.frames - 1
			elif self.previewing:
				s = self.previewing.frame
				if n == FrameSet.prev_frameset:
					s -= 17
				elif n == FrameSet.prev_frame:
					s -= 1
				elif n == FrameSet.next_frame:
					s += 1
				elif n == FrameSet.next_frameset:
					s += 17
				if s < 0 or s >= self.previewing.grp.frames:
					if not self.looppreview.get():
						return
					while s < 0:
						s += self.previewing.grp.frames
					if s >= self.previewing.grp.frames:
						s %= self.previewing.grp.frames
			else:
				s = 0
			self.previewnext = self.previewing.next_frame(s)
			self.updateframes()
			self.drawpreview()
		# if not n in [3,4,5,6,7]:
		# 	if n in [0,10]:
		# 		s = [self.curgrp.frames-1,0][not n]
		# 	elif n in [1,2,8,9]:
		# 		s = self.previewing[1] + [-17,-1,1,17][n % 5 - 1]
		# 		if s < 0 or s >= self.curgrp[2]:
		# 			if not self.looppreview.get():
		# 				return
		# 			if s < 0:
		# 				s += self.curgrp[2]
		# 			if s >= self.curgrp[2]:
		# 				s %= self.curgrp[2]
		# 	self.previewnext[1] = s
		# 	self.updateframes()
		# 	self.drawpreview()
		# if n in [3,4,6,7]:
		# 	self.speed = [-17,-1,None,1,17][n - 3]
		# 	self.play = self.after(int(self.prevspeed.get()), self.playframe)
		# elif self.speed or self.play:
		# 	self.stopframe()
		self.action_states()

	def stopframe(self) -> None:
		if not self.play:
			return
		self.speed = 0
		self.after_cancel(self.play)
		self.play = None
		self.action_states()

	def playframe(self) -> None:
		prevfrom = self.prevfrom.get()
		prevto = self.prevto.get()
		if not self.speed or prevto <= prevfrom:
			self.stopframe()
			return
		i = self.previewing.frame + self.speed
		frames = prevto-prevfrom+1
		if self.looppreview.get() or (i >= prevfrom and i <= prevto):
			while i < prevfrom or i > prevto:
				if i < prevfrom:
					i += frames
				if i > prevto:
					i -= frames
			self.previewnext = self.previewing.next_frame(i)
			self.updateframes()
			self.drawpreview()
			if self.play:
				self.after_cancel(self.play)
			self.play = self.after(int(self.prevspeed.get()), self.playframe)

	def doid(self) -> None:
		self.stopframe()
		entry_type = self.entry_type()
		if entry_type != EntryType.iscript:
			if entry_type == EntryType.images_dat:
				listbox = self.delegate.imageslist
				id_variable = self.image
			elif entry_type == EntryType.sprites_dat:
				listbox = self.delegate.spriteslist
				id_variable = self.sprites
			else: # if t == EntryType.flingy_dat:
				listbox = self.delegate.flingylist
				id_variable = self.flingys
			i = listbox.get(id_variable.get()).strip().split(' ')[0]
		else:
			i = IScriptBIN.type_frame(1, None, self.previewing.frame)[0]
		if self.overwrite.get():
			s = self.text.index('%s linestart' % INSERT)
			m = re.match('(\\s*)(\\S+)(\\s+)([^\\s#]+)(\\s+.*)?', self.text.get(s,'%s lineend' % INSERT))
			if m and m.group(2) in PREVIEWER_CMDS[entry_type]:
				self.text.delete(s,'%s lineend' % INSERT)
				self.text.insert(s, m.group(1)+m.group(2)+m.group(3)+i+m.group(5))
		else:
			self.text.insert(INSERT, i)
		if self.closeafter.get():
			self.destroy()

	def docmd(self) -> None:
		self.stopframe()
		entry_type = self.entry_type()
		s = self.text.index('%s linestart' % INSERT)
		if entry_type != EntryType.iscript:
			if entry_type == EntryType.images_dat:
				formatter = IScriptBIN.type_imageid
				listbox = self.delegate.imageslist
				id_variable = self.image
				cmd_variable = self.imagecmd
			elif entry_type == EntryType.sprites_dat:
				formatter = IScriptBIN.type_spriteid
				listbox = self.delegate.spriteslist
				id_variable = self.sprites
				cmd_variable = self.spritescmd
			else: # if entry_type == EntryType.flingy_dat
				formatter = IScriptBIN.type_flingyid
				listbox = self.delegate.flingylist
				id_variable = self.flingys
				cmd_variable = self.flingyscmd
			i = formatter(1, self.delegate.get_ibin(), int(listbox.get(id_variable.get()).strip().split(' ')[0]))
		else:
			i = IScriptBIN.type_frame(1, None, self.previewing.frame)
			cmd_variable = self.curcmd
		assert isinstance(i, tuple)
		cmd = PREVIEWER_CMDS[entry_type][cmd_variable.get()]
		longest_opcode = max([len(o[0][0]) for o in IScriptBIN.OPCODES] + [13]) + 1
		t = '\t%s%s\t%s' % (cmd,' ' * (longest_opcode-len(cmd)),i[0])
		p = len(IScriptBIN.OPCODES[IScriptBIN.REV_OPCODES[cmd]][1])
		if p > 1:
			t += ' 0' * (p-1)
		if i[1]:
			t += ' # ' + i[1]
		if self.overwrite.get():
			self.text.delete(s,'%s lineend' % INSERT)
		else:
			t += '\n'
		self.text.insert(s, t)
		if self.closeafter.get():
			self.destroy()

	def updateframes(self) -> None:
		if self.previewing.grp:
			self.grp_frame.set('Frame: %s / %s' % (self.previewing.frame,self.previewing.grp.frames))
			if self.previewing.grp.frames:
				x = self.previewing.frame / self.previewing.grp.frames
				self.scroll.set(x,x+1/float(self.previewing.grp.frames))
			else:
				self.scroll.set(0,1)
		self.action_states()

	def preview_limits(self) -> None:
		if self.previewing.grp:
			self.prevstart.config(state=NORMAL)
			self.prevend.config(state=NORMAL)
			to = max(self.previewing.grp.frames-1,0)
			self.prevfrom.range[1] = to
			self.prevto.range[1] = to
			self.prevfrom.set(0)
			self.prevto.set(to)
		else:
			self.prevstart.config(state=DISABLED)
			self.prevend.config(state=DISABLED)
			self.prevfrom.set(0)
			self.prevto.set(0)

	def grp(self, image_id: int, pal: str, frame: int, *path_components: str) -> Image | None:
		if not MPQ.supported() or not pal in PALETTES:
			return None
		path = Assets.mpq_file_name(*path_components)
		draw = not path in GRP_CACHE or not frame in GRP_CACHE[path] or not pal in GRP_CACHE[path][frame]
		if draw or self.previewing.image_id != image_id or self.previewing.grp is None:
			if self.previewing.grp and self.previewing.image_id == image_id:
				grp = self.previewing.grp
			else:
				try:
					grp = GRP.CacheGRP()
					grp.load_file(self.delegate.mpqhandler.load_file('MPQ:' + path))
				except PyMSError:
					return None
				self.previewing.grp = grp
				self.preview_limits()
			if draw:
				if not path in GRP_CACHE:
					GRP_CACHE[path] = {}
				if not frame in GRP_CACHE:
					GRP_CACHE[path][frame] = {}
				GRP_CACHE[path][frame][pal] = cast(Image, GRP.frame_to_photo(PALETTES[pal], grp, frame, True, False))
		return GRP_CACHE[path][frame][pal]

	def select(self, entry_id: int, entry_type: EntryType, frame: int = 0) -> None:
		if entry_type != self.entry_type():
			return
		self.stopframe()
		if entry_type == EntryType.iscript:
			image_id = int(self.curdd.entries[entry_id].strip().split(' ')[0])
		elif entry_type == EntryType.images_dat:
			image_id = int(self.delegate.imageslist.get(entry_id).strip().split(' ')[0])
		elif entry_type == EntryType.sprites_dat:
			image_id = self.delegate.spritesdat.get_entry(int(self.delegate.spriteslist.get(entry_id).strip().split(' ')[0])).image
		elif entry_type == EntryType.flingy_dat:
			image_id = self.delegate.spritesdat.get_entry(self.delegate.flingydat.get_entry(int(self.delegate.flingylist.get(entry_id).strip().split(' ')[0])).sprite).image
		self.previewnext = self.previewing.next_entry(image_id, frame)
		self.drawpreview()
		self.updateframes()

	def selectframe(self, t: MoveViewBy, p: float, e=None) -> None:
		if not self.previewing.grp:
			return
		self.stopframe()
		a = {'pages':17,'units':1}
		if t == MOVETO:
			self.previewnext = self.previewing.next_frame(int(self.previewing.grp.frames * float(p)))
		elif t == SCROLL:
			self.previewnext = self.previewing.next_frame(min(self.previewing.grp.frames-1,max(0,self.previewing.frame + int(p) * a[e])))
		self.updateframes()
		# if self.timer:
			# self.after_cancel(self.timer)
		# self.timer = self.after(10, self.drawpreview)
		self.drawpreview()

	def drawpreview(self) -> None:
		if self.previewnext == self.previewing:
			return
		elif self.previewnext:
			self.previewing = self.previewnext
		self.preview.delete(ALL)
		if not self.showpreview.get():
			return
		image_id = self.previewing.image_id
		grp_file_index = self.delegate.imagesdat.get_entry(image_id).grp_file
		if not grp_file_index:
			return
		grp_file_path = self.delegate.imagestbl.strings[grp_file_index-1][:-1]
		if grp_file_path.startswith('thingy\\tileset\\'):
			pal = 'Terrain'
		else:
			pal = 'Units'
			draw_function = self.delegate.imagesdat.get_entry(image_id).draw_function
			remapping = self.delegate.imagesdat.get_entry(image_id).remapping
			if draw_function == DAT.DATImage.DrawFunction.use_remapping and remapping is not None and remapping >= DAT.DATImage.Remapping.ofire and remapping <= DAT.DATImage.Remapping.bfire:
				pal = ['o','b','g'][remapping-1] + 'fire'
		sprite = self.grp(image_id, pal, self.previewing.frame, 'unit', grp_file_path)
		if sprite:
			self.preview.create_image(130, 130, image=sprite[0])

	def destroy(self) -> None:
		self.stopframe()
		self.delegate.settings.previewer.overwrite = self.overwrite.get()
		self.delegate.settings.previewer.closeafter = self.closeafter.get()
		self.delegate.settings.previewer.showpreview = self.showpreview.get()
		self.delegate.settings.previewer.previewspeed = self.prevspeed.get()
		self.delegate.settings.previewer.looppreview = self.looppreview.get()
		PyMSDialog.withdraw(self)
