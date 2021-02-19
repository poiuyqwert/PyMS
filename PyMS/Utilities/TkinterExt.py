
import Tkinter as Tk

class MainWindow(Tk.Tk):
	pass

class Menu(Tk.Menu):
	# Extend `add_command` to:
	#  - Optionally take a `shortcut` which will drive the `accelerator` and bind the shortcut to the `command`
	#  - Return the index of the command
	def add_command(self, cnf={}, shortcut=None, shortcut_widget=None, shortcut_event=False, **kwargs):
		if shortcut and kwargs.get('command'):
			kwargs['accelerator'] = shortcut.name()
			shortcut_widget = shortcut_widget or self.master
			command = kwargs['command']
			if not shortcut_event:
				_command = kwargs['command']
				command = lambda *e: _command()
			shortcut_widget.bind(shortcut, command)
		Tk.Menu.add_command(self, cnf=cnf, **kwargs)
		return self.index(Tk.END)
