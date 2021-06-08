
from utils import BASE_DIR, isstr
from Tooltip import Tooltip
from UIKit import *

import os

class Toolbar(Frame):
	# Use `bind_target=<widget>` to adjust where shortcuts are bound, otherwise `self.master` will be used
	def __init__(self, *args, **kwargs):
		self._buttons = {}
		self._tags = {}
		Frame.__init__(self, *args, **kwargs)
		self._bind_target = kwargs.get('bind_target', self.master)

	def add_button(self, icon, callback, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True):
		if isstr(icon):
			try:
				if os.path.exists(icon):
					icon = PhotoImage(file=icon)
				else:
					icon = PhotoImage(file=os.path.join(BASE_DIR, 'PyMS', 'Images', '%s.gif' % icon))
			except:
				icon = None
		button = Button(self, image=icon, width=20, height=20, command=callback, state=NORMAL if enabled else DISABLED)
		button.image = icon
		if shortcut:
			if bind_shortcut:
				self._bind_target.bind(shortcut, lambda *e: callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		button.tooltip = Tooltip(button, tooltip)
		button.pack(side=LEFT)
		if identifier:
			self._buttons[identifier] = button
		if tags:
			if not isinstance(tags, list) and not isinstance(tags, tuple):
				tags = (tags, )
			for tag in tags:
				if not tag in self._tags:
					self._tags[tag] = [button]
				else:
					self._tags[tag].append(button)
		return button

	def set_enabled(self, button_identifier, is_enabled):
		button = self._buttons.get(button_identifier)
		if button:
			button['state'] = NORMAL if is_enabled else DISABLED

	def tag_enabled(self, tag, is_enabled):
		for button in self._tags.get(tag, ()):
			button['state'] = NORMAL if is_enabled else DISABLED

	def add_spacer(self, width):
		return Frame(self, width=width).pack(side=LEFT)

	GAP_SIZE = 2
	def add_gap(self):
		return self.add_spacer(Toolbar.GAP_SIZE)

	SECTION_SIZE = 10
	def add_section(self):
		return self.add_spacer(Toolbar.SECTION_SIZE)
