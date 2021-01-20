
from utils import BASE_DIR
from InternalErrorDialog import InternalErrorDialog

from Tkinter import Toplevel

import sys,os

LOGS_FOLDER = os.path.join(BASE_DIR, 'PyMS','Logs')
try:
	os.makedirs(LOGS_FOLDER)
except:
	pass

STDERR = sys.stderr
STDOUT = sys.stdout
STDOUT_FSYNC = False

class ErrorHandler:
	def __init__(self, toplevel, prog):
		self.toplevel = toplevel
		self.prog = prog
		self.window = None
		self.creating_window = False
		self.buffer = ''
		try:
			self.file = open(os.path.join(LOGS_FOLDER, '%s.txt' % prog),'w')
		except OSError:
			pass

	def find_presenter(self):
		presenter = self.toplevel
		children = presenter.winfo_children()
		while len(children) and isinstance(children[-1], Toplevel):
			presenter = children[-1]
			children = presenter.winfo_children()
		return presenter

	def write(self, text, from_stdout=False):
		if from_stdout:
			STDOUT.write(text)
		else:
			STDERR.write(text)

		if self.file:
			self.file.write(text)
			if from_stdout == False or STDOUT_FSYNC:
				self.file.flush()
				os.fsync(self.file.fileno())

		if not self.window:
			self.buffer += text
			if not from_stdout and not self.creating_window:
				self.creating_window = True
				def present():
					presenter = self.find_presenter()
					if hasattr(presenter, '_pyms__window_blocking') and presenter._pyms__window_blocking:
						self.toplevel.after(1000, present)
						return
					self.window = InternalErrorDialog(presenter, self.prog, self, self.buffer)
					self.buffer = ''
					self.creating_window = False
					self.window.grab_wait()
				self.toplevel.after(0, present)
		else:
			self.window.add_text(text)

	def clear_window(self):
		self.window = None

class OutputHandler:
	def __init__(self, file):
		self.file = file

	def write(self, text):
		self.file.write(text, from_stdout=True)

def setup_trace(toplevel, prog):
	sys.stderr = ErrorHandler(toplevel, prog)
	sys.stdout = OutputHandler(sys.stderr)
