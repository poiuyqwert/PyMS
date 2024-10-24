
from __future__ import annotations

from .SettingsTab import SettingsTab

from ...FileFormats.MPQ.MPQ import MPQ

from .. import Assets
from ..PyMSConfig import PYMS_CONFIG
from ..UIKit import *
from .. import Config
from ..EditedState import EditedState
from ..MPQHandler import MPQHandler

import os

from typing import Callable

class MPQSettingsTab(SettingsTab):
	def __init__(self, parent: Notebook, edited_state: EditedState, mpq_hander: MPQHandler, mpqs_config: Config.List[str], mpqs_select_config: Config.SelectFile) -> None:
		self.edited_state = edited_state
		self.mpq_handler = mpq_hander
		self.mpqs_config = mpqs_config
		self.mpqs_select_config = mpqs_select_config

		SettingsTab.__init__(self, parent)
		Label(self, text='MPQ Settings:', font=Font.default().bolded(), anchor=W).pack(fill=X)
		Label(self, text="Files will be read from the highest priority MPQ that contains them.\nThe higher an MPQ is on the list the higher its priority.", anchor=W, justify=LEFT).pack(fill=X)

		self.listbox = ScrolledListbox(self, width=35, height=1)
		self.listbox.pack(fill=BOTH, padx=1, pady=1, expand=1)
		for mpq in self.mpqs_config.data:
			self.listbox.insert(END,mpq)
		if self.listbox.size():
			self.listbox.select_set(0)

		self.toolbar = Toolbar(self)
		self.toolbar.add_button(Assets.get_image('add'), self.add, 'Add MPQ', Key.Insert),
		self.toolbar.add_button(Assets.get_image('remove'), self.remove, 'Remove MPQ', Key.Delete, enabled=False, tags='has_selection'),
		self.toolbar.add_button(Assets.get_image('opendefault'), self.adddefault, "Add default StarCraft MPQ's", Shift.Insert),
		self.toolbar.add_spacer(10, flexible=True)
		def move_callback(dir: int) -> Callable[[], None]:
			def move() -> None:
				self.movempq(dir=dir)
			return move
		self.toolbar.add_button(Assets.get_image('up'), move_callback(0), 'Move MPQ Up', Shift.Up, enabled=False, tags='has_selection'),
		self.toolbar.add_button(Assets.get_image('down'), move_callback(1), 'Move MPQ Down', Shift.Down, enabled=False, tags='has_selection'),
		self.toolbar.pack(fill=X, padx=51, pady=1)

		self.action_states()

	def activate(self) -> None:
		self.listbox.focus_set()

	def action_states(self) -> None:
		has_selection = not not self.listbox.curselection()
		self.toolbar.tag_enabled('has_selection', has_selection)

	def movempq(self, key: Event | None = None, dir: int = 0) -> None:
		i = int(self.listbox.curselection()[0])
		if i == [0,self.listbox.size()-1][dir]: # type: ignore[operator]
			return
		s = self.listbox.get(i)
		n = i + [-1,1][dir]
		self.mpqs_config.data[i] = self.mpqs_config.data[n]
		self.mpqs_config.data[n] = s
		self.listbox.delete(i)
		self.listbox.insert(n, s)
		self.listbox.select_clear(0, END)
		self.listbox.select_set(n)
		self.listbox.see(n)
		self.edited_state.mark_edited()

	def add(self, key: Event | None = None, add: list[str] | None = None) -> None:
		n: str | int = 0
		s: int = 0
		if add is None:
			add = self.mpqs_select_config.select_open_multiple(self)
		else:
			n = END
			s = self.listbox.size() # type: ignore[assignment]
		if not add:
			return
		for i in add:
			if not i in self.mpqs_config.data:
				mpq = MPQ.of(i)
				try:
					mpq.open()
					mpq.close()
				except:
					continue
				if n == END:
					self.mpqs_config.data.append(i)
				else:
					self.mpqs_config.data.insert(int(n),i)
				self.listbox.insert(n,i)
		self.listbox.select_clear(0,END)
		self.listbox.select_set(s)
		self.listbox.see(s)
		self.action_states()
		self.edited_state.mark_edited()

	def remove(self, key: Event | None = None) -> None:
		i = int(self.listbox.curselection()[0])
		del self.mpqs_config.data[i]
		self.listbox.delete(i)
		if self.listbox.size():
			i = min(i,self.listbox.size()-1) # type: ignore[operator]
			self.listbox.select_set(i)
			self.listbox.see(i)
		self.action_states()
		self.edited_state.mark_edited()

	def adddefault(self, key: Event | None = None) -> None:
		scdir = PYMS_CONFIG.scdir.path
		PYMS_CONFIG.store_state()
		if scdir is None or not os.path.isdir(scdir):
			scdir = PYMS_CONFIG.scdir.select_open(self)
		if scdir and os.path.isdir(scdir):
			a = []
			for f in ['Patch_rt','BrooDat','StarDat']:
				p = os.path.join(scdir, '%s%smpq' % (f,os.extsep))
				if os.path.exists(p) and not p in self.mpqs_config.data:
					a.append(p)
			if len(a) != 3:
				PYMS_CONFIG.restore_state()
			if a:
				self.add(add=a)

	def save(self):
		if self.edited_state.is_edited:
			self.mpq_handler.refresh()
		super().save()
