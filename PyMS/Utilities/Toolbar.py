
from .utils import BASE_DIR, isstr
from .Tooltip import Tooltip
from .UIKit import *
from .TagStateManager import TagStateManager

class Toolbar(Frame):
	# Use `bind_target=<widget>` to adjust where shortcuts are bound, otherwise `self.master` will be used
	def __init__(self, *args, **kwargs):
		self._buttons = {} # type: dict[str, Widget]
		self._tag_manager = TagStateManager()
		self._bind_target = None # type: Widget
		if 'bind_target' in kwargs:
			self._bind_target = kwargs['bind_target']
			del kwargs['bind_target']
		Frame.__init__(self, *args, **kwargs)
		if not self._bind_target:
			self._bind_target = self.master
		self._row = None # type: Frame
		self.add_row()

	def add_row(self):
		self._row = Frame(self)
		self._row.pack(side=TOP, fill=X, pady=(0,2))

	def _add_button(self, button, tooltip, identifier, tags):
		Tooltip(button, tooltip)
		button.pack(side=LEFT)
		if identifier:
			self._buttons[identifier] = button
		if tags:
			self._tag_manager.add_item(button, tags)

	def add_button(self, icon, callback, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True):
		button = Button(self._row, image=icon, width=20, height=20, command=callback, state=NORMAL if enabled else DISABLED)
		button._image = icon
		if shortcut:
			if bind_shortcut:
				def _binding_trigger_command(button, callback):
					if button['state'] == DISABLED or not button.winfo_viewable():
						return
					callback()
				self._bind_target.bind(shortcut, lambda _, _button=button, _callback=callback: _binding_trigger_command(_button, _callback))
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_radiobutton(self, icon, variable, value, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True):
		button = Radiobutton(self._row, image=icon, width=20, height=20, variable=variable, value=value, indicatoron=0, state=NORMAL if enabled else DISABLED)
		button._image = icon
		if shortcut:
			if bind_shortcut:
				def _binding_trigger_radiobutton(button, variable, value):
					if button['state'] == DISABLED or not button.winfo_viewable():
						return
					variable.set(value)
				self._bind_target.bind(shortcut, lambda _, _button=button, _variable=variable, _value=value: _binding_trigger_radiobutton(_button, _variable, _value))
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_checkbutton(self, icon, variable, tooltip, shortcut=None, enabled=True, identifier=None, tags=None, add_shortcut_to_tooltip=True, bind_shortcut=True, onvalue=True, offvalue=False):
		button = Checkbutton(self._row, image=icon, width=20, height=20, variable=variable, onvalue=onvalue, offvalue=offvalue, indicatoron=0, state=NORMAL if enabled else DISABLED)
		button._image = icon
		if shortcut:
			if bind_shortcut:
				def _binding_trigger_checkbutton(button, variable, onvalue, offvalue):
					if button['state'] == DISABLED or not button.winfo_viewable():
						return
					variable.set(onvalue if variable.get() == offvalue else offvalue)
				self._bind_target.bind(shortcut, lambda _, _button=button, _variable=variable, _onvalue=onvalue, _offvalue=offvalue: _binding_trigger_checkbutton(_button, _variable, _onvalue, _offvalue))
			if add_shortcut_to_tooltip:
				tooltip += ' (%s)' % shortcut.description()
		self._add_button(button, tooltip, identifier, tags)
		return button

	def add_spacer(self, width, flexible=False):
		return Frame(self._row, width=width).pack(side=LEFT, fill=X, expand=flexible)

	GAP_SIZE = 2
	def add_gap(self):
		return self.add_spacer(Toolbar.GAP_SIZE)

	SECTION_SIZE = 10
	def add_section(self):
		return self.add_spacer(Toolbar.SECTION_SIZE)

	def update_icon(self, identifier, icon):
		button = self._buttons.get(identifier)
		if not button:
			return
		button['image'] = icon
		button._image = icon

	def set_enabled(self, identifier, is_enabled):
		button = self._buttons.get(identifier)
		if button:
			button['state'] = NORMAL if is_enabled else DISABLED

	def tag_enabled(self, tag, is_enabled):
		self._tag_manager.tag_enabled(tag, is_enabled)
