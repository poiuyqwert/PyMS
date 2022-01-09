
from Tkconstants import DISABLED
import Tkinter as Tk

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
		self._tags = {}
		Tk.Menu.__init__(self, master, cnf, **kw)

	# Extend `add_command` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to the `command`
	#  - Return a wrapper of the command to be able to configure it
	def add_command(self, shortcut=None, shortcut_widget=None, shortcut_event=False, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		Tk.Menu.add_command(self, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut and 'command' in kwargs:
			def _binding_trigger_command(item, command, event, pass_event):
				if item['state'] == DISABLED:
					return
				if pass_event:
					command(event)
				else:
					command()
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda event, _item=item, command=kwargs['command'], pass_event=shortcut_event: _binding_trigger_command(_item, command, event, pass_event))
		if tags:
			if not isinstance(tags, list) and not isinstance(tags, tuple):
				tags = (tags, )
			for tag in tags:
				if not tag in self._tags:
					self._tags[tag] = [item]
				else:
					self._tags[tag].append(item)
		return item

	def add_radiobutton(self, shortcut=None, shortcut_widget=None, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		Tk.Menu.add_radiobutton(self, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut and 'variable' in kwargs and 'value' in kwargs:
			def _binding_trigger_radiobutton(item, variable, value):
				if item['state'] == DISABLED:
					return
				variable.set(value)
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda _, _item=item, variable=kwargs['variable'], value=kwargs['value']: _binding_trigger_radiobutton(_item, variable, value))
		if tags:
			if not isinstance(tags, list) and not isinstance(tags, tuple):
				tags = (tags, )
			for tag in tags:
				if not tag in self._tags:
					self._tags[tag] = [item]
				else:
					self._tags[tag].append(item)
		return item

	def add_checkbutton(self, shortcut=None, shortcut_widget=None, tags=None, bind_shortcut=True, **kwargs):
		if shortcut:
			kwargs['accelerator'] = shortcut.name()
		Tk.Menu.add_checkbutton(self, **kwargs)
		item = Menu.Item(self, self.index(Tk.END))
		if shortcut and bind_shortcut and 'variable' in kwargs and 'onvalue' in kwargs and 'offvalue' in kwargs:
			def _binding_trigger_checkbutton(item, variable, onvalue, offvalue):
				if item['state'] == DISABLED:
					return
				variable.set(onvalue if variable.get() == offvalue else offvalue)
			shortcut_widget = shortcut_widget or self.master
			shortcut_widget.bind(shortcut, lambda _, _item=item, variable=kwargs['variable'], onvalue=kwargs['onvalue'], offvalue=kwargs['offvalue']: _binding_trigger_checkbutton(_item, variable, onvalue, offvalue))
		if tags:
			if not isinstance(tags, list) and not isinstance(tags, tuple):
				tags = (tags, )
			for tag in tags:
				if not tag in self._tags:
					self._tags[tag] = [item]
				else:
					self._tags[tag].append(item)
		return item

	def tag_enabled(self, tag, is_enabled):
		for item in self._tags.get(tag, ()):
			item['state'] = Tk.NORMAL if is_enabled else Tk.DISABLED
