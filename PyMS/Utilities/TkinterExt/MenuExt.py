
from ..TagStateManager import TagStateManager

try:
	import Tkinter as Tk
except:
	import tkinter as Tk

class Menu(Tk.Menu):
	class Item(object):
		def __init__(self, menu, index):
			self.menu = menu
			self.index = index

		def cget(self, option):
			return self.menu.entrycget(self.index, option)
		def __getitem__(self, option):
			return self.cget(option)

		def config(self, **kwargs):
			self.menu.entryconfig(self.index, **kwargs)
		def __setitem__(self, option, value):
			self.config(**{option: value})

	def __init__(self, master=None, cnf={}, **kw):
		self._items = {} # type: dict[str, Menu.Item]
		self._tag_manager = TagStateManager()
		self._cascade_menus = [] # type: list[Menu]
		Tk.Menu.__init__(self, master, cnf, **kw)

	def _detect_underline(self, label, shortcut, kwargs):
		underline = kwargs.get('underline')
		if isinstance(underline, int):
			return
		# Remove `underline` to handle invalid values. It will be replaced if we can determine a proper value
		if 'underline' in kwargs:
			del kwargs['underline']
		find = None 
		if isinstance(underline, str):
			find = underline
		elif shortcut != None:
			keysym = shortcut.get_keysym()
			if not keysym:
				return
			find = keysym.value
		else:
			return
		# If we are finding a single letter, do a case insensitive search for it. Otherwise find the text case sensitive and underline the first letter of the match
		if len(find) == 1:
			find = find.lower()
			label = label.lower()
		if not find in label:
			return
		kwargs['underline'] = label.index(find)

	# Extend `add_command` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to the `command`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not calling the `command` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the command to be able to configure it
	def add_command(self, label, command, shortcut=None, shortcut_widget=None, shortcut_event=False, enabled=True, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		Tk.Menu.add_command(self, label=label, command=command, state=Tk.NORMAL if enabled else Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut:
			def _binding_trigger_command(item, command, event, pass_event):
				if item['state'] == Tk.DISABLED:
					return
				if pass_event:
					command(event)
				else:
					command()
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda event, _item=item, _command=command, pass_event=shortcut_event: _binding_trigger_command(_item, _command, event, pass_event))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_radiobutton` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to set the `variable` to `value`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not setting the `variable` to `value` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the radiobutton to be able to configure it
	def add_radiobutton(self, label, variable, value, shortcut=None, shortcut_widget=None, enabled=True, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		Tk.Menu.add_radiobutton(self, label=label, variable=variable, value=value, state=Tk.NORMAL if enabled else Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut:
			def _binding_trigger_radiobutton(item, variable, value):
				if item['state'] == Tk.DISABLED:
					return
				variable.set(value)
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda _, _item=item, _variable=variable, _value=value: _binding_trigger_radiobutton(_item, _variable, _value))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_checkbutton` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to toggle the `variable` between `onvalue` and `offvalue`
	#  - `underline` can be determined by the `shortcut`, or can be specified as a `str` or index
	#  - The binding will automatically handle not toggling the `variable` if the item is disabled
	#  - Return a `Menu.Item` wrapper of the checkbutton to be able to configure it
	def add_checkbutton(self, label, variable, onvalue=True, offvalue=False, shortcut=None, shortcut_widget=None, enabled=True, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		self._detect_underline(label, shortcut, kwargs)
		Tk.Menu.add_checkbutton(self, label=label, variable=variable, onvalue=onvalue, offvalue=offvalue, state=Tk.NORMAL if enabled else Tk.DISABLED, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut:
			def _binding_trigger_checkbutton(item, variable, onvalue, offvalue):
				if item['state'] == Tk.DISABLED:
					return
				variable.set(onvalue if variable.get() == offvalue else offvalue)
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda _, _item=item, _variable=variable, _onvalue=onvalue, _offvalue=offvalue: _binding_trigger_checkbutton(_item, _variable, _onvalue, _offvalue))
		if tags:
			self._tag_manager.add_item(item, tags)
		return item

	# Extend `add_cascade` to:
	#  - Generate a `Menu` if none is specified and return in
	#  - Remember its children so `tag_enabled` will apply recursively
	def add_cascade(self, label, menu=None, **kwargs): # type: (str, Menu, **Any) -> Menu
		if not menu:
			menu = Menu(self, tearoff=kwargs.get('tearoff', 0))
		Tk.Menu.add_cascade(self, label=label, menu=menu, **kwargs)
		self._cascade_menus.append(menu)
		return menu

	def tag_enabled(self, tag, is_enabled):
		self._tag_manager.tag_enabled(tag, is_enabled)
		for menu in self._cascade_menus:
			menu.tag_enabled(tag, is_enabled)
