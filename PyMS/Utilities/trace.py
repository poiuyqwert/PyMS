
from . import Assets
from .InternalErrorDialog import InternalErrorDialog
from .UIKit import MainWindow, Toplevel

import sys, os, traceback

try:
	os.makedirs(Assets.logs_dir)
except:
	pass

class Tracer(object):
	class STDStream(object):
		def __init__(self, tracer, stream): # type: (Tracer, TextIO) -> Tracer.STDStream
			self.tracer = tracer
			self.stream = stream

		def write(self, text): # (str) -> None
			self.stream.write(text)
			self.tracer.write(text, self)

		def flush(self):
			pass

	def __init__(self, program_name, main_window): # type: (str, MainWindow) -> Tracer
		self.stdout = Tracer.STDStream(self, sys.stdout)
		self.stderr =Tracer.STDStream(self, sys.stderr)
		self.program_name = program_name
		self.main_window = main_window
		self.window = None # type: InternalErrorDialog
		self.creating_window = False
		self.buffer = ''
		try:
			self.file = open(Assets.log_file_path('%s.txt' % program_name),'w')
		except OSError:
			pass

	def _find_presenter(self): # type: () -> (MainWindow | Toplevel)
		presenter = self.main_window
		children = presenter.winfo_children()
		while len(children) and isinstance(children[-1], Toplevel):
			presenter = children[-1]
			children = presenter.winfo_children()
		return presenter

	def _present(self):
		if self.creating_window:
			return
		if self.window == None:
			self.creating_window = True
			def present():
				presenter = self._find_presenter()
				if hasattr(presenter, '_pyms__window_blocking') and presenter._pyms__window_blocking:
					self.main_window.after(1000, present)
					return
				self.window = InternalErrorDialog(presenter, self.program_name, self.buffer)
				self.buffer = ''
				self.creating_window = False
				self.window.grab_wait()
				self.window = None
			self.main_window.after(0, present)
		self.flush()

	def write(self, text, source=None): # type: (str, STDStream | None) -> None
		if not self.file:
			return
		self.file.write(text)
		if self.window:
			self.window.add_text(text)
		else:
			self.buffer += text
			if source == self.stderr:
				self._present()

	def flush(self):
		if not self.file:
			return
		self.file.flush()

def setup_trace(program_name, main_window):
	if isinstance(sys.stdout, Tracer):
		return
	tracer = Tracer(program_name, main_window)
	sys.stdout = tracer.stdout
	sys.stderr = tracer.stderr
