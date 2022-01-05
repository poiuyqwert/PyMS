
import Tkinter as Tk

class Menu(Tk.Menu):
	class Command(object):
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
		if shortcut and kwargs.get('command'):
			kwargs['accelerator'] = shortcut.name()
			command = kwargs['command']
			if not shortcut_event:
				_command = kwargs['command']
				command = lambda *_: _command()
			if bind_shortcut:
				shortcut_widget = shortcut_widget or self.master
				shortcut_widget.bind(shortcut, command)
		Tk.Menu.add_command(self, **kwargs)
		command = Menu.Command(self, self.index(Tk.END))
		if tags:
			if not isinstance(tags, list) and not isinstance(tags, tuple):
				tags = (tags, )
			for tag in tags:
				if not tag in self._tags:
					self._tags[tag] = [command]
				else:
					self._tags[tag].append(command)
		return command

	def tag_enabled(self, tag, is_enabled):
		for command in self._tags.get(tag, ()):
			command['state'] = Tk.NORMAL if is_enabled else Tk.DISABLED
