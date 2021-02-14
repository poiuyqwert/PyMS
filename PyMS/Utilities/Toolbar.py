
from utils import BASE_DIR, isstr
from Tooltip import Tooltip

from Tkinter import *
import os

class Toolbar(Frame):
	# Use `bind_target=<widget>` to adjust where shortcuts are bound, otherwise `self.master` will be used
	def __init__(self, *args, **kwargs):
		self._buttons = {}
		Frame.__init__(self, *args, **kwargs)
		self._bind_target = kwargs.get('bind_target', self.master)

	def add_button(self, icon, callback, tooltip, shortcut=None, enabled=True, identifier=None, add_shortcut_to_tooltip=True):
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
			self._bind_target.bind(shortcut, lambda *e: callback())
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		button.tooltip = Tooltip(button, tooltip)
		button.pack(side=LEFT)
		if identifier:
			self._buttons[identifier] = button
		return button

	def set_enabled(self, button_identifier, is_enabled):
		button = self._buttons.get(button_identifier)
		if button:
			button['state'] = NORMAL if is_enabled else DISABLED

	def add_spacer(self, width):
		return Frame(self, width=width).pack(side=LEFT)

	GAP_SIZE = 2
	def add_gap(self):
		return self.add_spacer(Toolbar.GAP_SIZE)

	SECTION_SIZE = 10
	def add_section(self):
		return self.add_spacer(Toolbar.SECTION_SIZE)
