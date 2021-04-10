
import Tkinter as Tk

class MainWindow(Tk.Tk):
	def startup(self):
		self.lift()
		self.call('wm', 'attributes', '.', '-topmost', True)
		self.after_idle(self.call, 'wm', 'attributes', '.', '-topmost', False)
		self.focus_force()
		# On Mac the main window doesn't get focused, so we use Cocoa to focus it
		try:
			import os
			from Cocoa import NSRunningApplication, NSApplicationActivateIgnoringOtherApps

			app = NSRunningApplication.runningApplicationWithProcessIdentifier_(os.getpid())
			app.activateWithOptions_(NSApplicationActivateIgnoringOtherApps)
		except:
			pass
		self.mainloop()

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

	# Extend `add_command` to:
	#  - Optionally take an `EventPattern` as a `shortcut`, which will drive the `accelerator` and bind the shortcut to the `command`
	#  - Return a wrapper of the command to be able to configure it
	def add_command(self, shortcut=None, shortcut_widget=None, shortcut_event=False, **kwargs):
		if shortcut and kwargs.get('command'):
			kwargs['accelerator'] = shortcut.name()
			shortcut_widget = shortcut_widget or self.master
			command = kwargs['command']
			if not shortcut_event:
				_command = kwargs['command']
				command = lambda *_: _command()
			shortcut_widget.bind(shortcut, command)
		Tk.Menu.add_command(self, **kwargs)
		return Menu.Command(self, self.index(Tk.END))

class Canvas(Tk.Canvas):
	class Item(object):
		def __init__(self, canvas, item_id):
			self.canvas = canvas
			self.item_id = item_id

		def cget(self, option):
			return self.canvas.itemcget(self.item_id, option)
		def __getitem__(self, option):
			return self.cget(option)

		def config(self, **kwargs):
			self.canvas.itemconfig(self.item_id, **kwargs)
		def __setitem__(self, option, value):
			self.config(**{option: value})

		def coords(self, x,y):
			self.canvas.coords(self.item_id, x,y)

	def create_arc(self, x1,y1, x2,y2, *args, **kwargs):
		return Canvas.Item(self, Tk.Canvas.create_arc(self, x1,y1, x2,y2, *args, **kwargs))

	def create_bitmap(self, x,y, bitmap=None, *args, **kwargs):
		kwargs['bitmap'] = bitmap
		return Canvas.Item(self, Tk.Canvas.create_bitmap(self, x,y, *args, **kwargs))

	def create_image(self, x,y, image=None, *args, **kwargs):
		kwargs['image'] = image
		return Canvas.Item(self, Tk.Canvas.create_image(self, x,y, *args, **kwargs))

	def create_line(self, *points, **kwargs):
		return Canvas.Item(self, Tk.Canvas.create_line(self, *points, **kwargs))

	def create_oval(self, x1,y1, x2,y2, *args, **kwargs):
		return Canvas.Item(self, Tk.Canvas.create_oval(self, x1,y1, x2,y2, *args, **kwargs))

	def create_polygon(self, *points, **kwargs):
		return Canvas.Item(self, Tk.Canvas.create_polygon(self, *points, **kwargs))

	def create_rectangle(self, x1,y1, x2,y2, *args, **kwargs):
		return Canvas.Item(self, Tk.Canvas.create_rectangle(self, x1,y1, x2,y2, *args, **kwargs))

	def create_text(self, x1,y1, text=None, *args, **kwargs):
		kwargs['text'] = text
		return Canvas.Item(self, Tk.Canvas.create_text(self, x1,y1, *args, **kwargs))

	def create_window(self, x1,y1, x2,y2, window=None, *args, **kwargs):
		kwargs['window'] = window
		return Canvas.Item(self, Tk.Canvas.create_window(self, x1,y1, x2,y2, *args, **kwargs))

# Return from event callbacks to break further processing of the event
Tk.Event.BREAK = 'break'

def _clipboard_set(obj, text):
	obj.clipboard_clear()
	obj.clipboard_append(text)
Tk.Misc.clipboard_set = _clipboard_set