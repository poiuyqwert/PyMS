
from utils import is_mac

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

	def set_icon(self, name):
		from .utils import BASE_DIR
		import os
		try:
			self.icon = os.path.join(BASE_DIR, 'PyMS','Images','%s.ico' % name)
			self.wm_iconbitmap(self.icon)
		except:
			self.icon = '@%s' % os.path.join(BASE_DIR, 'PyMS','Images','%s.xbm' % name)
			self.wm_iconbitmap(self.icon)

class Toplevel(Tk.Toplevel):
	def make_active(self):
		if self.state() == 'withdrawn':
			self.deiconify()
		self.lift()
		self.focus_force()
		if not self.grab_status():
			self.grab_set()
			self.grab_release()

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

		def coords(self, x,y, x2=None,y2=None):
			x,y = self.canvas.coordinate_adjust(x, y)
			if x2 != None and y2 != None:
				x2,y2 = self.canvas.coordinate_adjust(x2, y2)
			self.canvas.coords(self.item_id, x,y, x2,y2)

		def __str__(self):
			return str(self.item_id)

	@staticmethod
	def coordinate_adjust_none(x, y):
		return (x, y)

	@staticmethod
	# Adjust the coordinates to work for Mac an Windows
	def coordinate_adjust_os(x, y):
		return (x + (1 if is_mac() else 0), y + (1 if is_mac() else 0))

	def __init__(self, master=None, cnf={}, coordinate_adjust=None, **kw):
		self.coordinate_adjust = coordinate_adjust or Canvas.coordinate_adjust_none
		Tk.Canvas.__init__(self, master, cnf, **kw)

	# TODO: Apply coordinate adjust
	# def addtag_closest(self, newtag, x, y, halo=None, start=None):
    # def addtag_enclosed(self, newtag, x1, y1, x2, y2):
    # def addtag_overlapping(self, newtag, x1, y1, x2, y2):
	# def bbox(self, *args):
	# def canvasx(self, screenx, gridspacing=None):
    # def canvasy(self, screeny, gridspacing=None):
	# def coords(self, *args):
	# def find_closest(self, x, y, halo=None, start=None):
    # def find_enclosed(self, x1, y1, x2, y2):
    # def find_overlapping(self, x1, y1, x2, y2):
	# def scan_mark(self, x, y):
    # def scan_dragto(self, x, y, gain=10):

	def create_arc(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_arc(self, x1,y1, x2,y2, *args, **kwargs))

	def create_bitmap(self, x,y, bitmap=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['bitmap'] = bitmap
		return Canvas.Item(self, Tk.Canvas.create_bitmap(self, x,y, *args, **kwargs))

	def create_image(self, x,y, image=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['image'] = image
		return Canvas.Item(self, Tk.Canvas.create_image(self, x,y, *args, **kwargs))

	def create_line(self, *points, **kwargs):
		points = (self.coordinate_adjust(x,y) for x,y in points)
		return Canvas.Item(self, Tk.Canvas.create_line(self, *points, **kwargs))

	def create_oval(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_oval(self, x1,y1, x2,y2, *args, **kwargs))

	def create_polygon(self, *points, **kwargs):
		points = (self.coordinate_adjust(x,y) for x,y in points)
		return Canvas.Item(self, Tk.Canvas.create_polygon(self, *points, **kwargs))

	def create_rectangle(self, x1,y1, x2,y2, *args, **kwargs):
		x1,y1 = self.coordinate_adjust(x1,y1)
		x2,y2 = self.coordinate_adjust(x2,y2)
		return Canvas.Item(self, Tk.Canvas.create_rectangle(self, x1,y1, x2,y2, *args, **kwargs))

	def create_text(self, x,y, text=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['text'] = text
		return Canvas.Item(self, Tk.Canvas.create_text(self, x,y, *args, **kwargs))

	def create_window(self, x,y, window=None, *args, **kwargs):
		x,y = self.coordinate_adjust(x,y)
		kwargs['window'] = window
		return Canvas.Item(self, Tk.Canvas.create_window(self, x,y, *args, **kwargs))

	def coords(self, item_id, x,y, x2=None,y2=None):
			x,y = self.coordinate_adjust(x, y)
			if x2 != None and y2 != None:
				x2,y2 = self.coordinate_adjust(x2, y2)
			Tk.Canvas.coords(self, item_id, x,y, x2,y2)

# Return from event callbacks to break further processing of the event
Tk.Event.BREAK = 'break'
# Return from event callbacks to leave current processing but continue processing other bindings
Tk.Event.CONTINUE = 'continue'

def _clipboard_set(obj, text):
	obj.clipboard_clear()
	obj.clipboard_append(text)
Tk.Misc.clipboard_set = _clipboard_set

class Colors:
	SystemHighlight = 'SystemHighlight'