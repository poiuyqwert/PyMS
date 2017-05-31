from utils import *

import sys,os

# DEBUG = Show std out in logs
DEBUG = True
# FSYNC = Use fsync for std err to try and ensure we capture the errors
FSYNC = True

LOGS_FOLDER = os.path.join(BASE_DIR,'Libs','Logs')

class ErrorHandler:
	def __init__(self, toplevel, prog):
		self.toplevel = toplevel
		self.prog = prog
		self.window = None
		self.buffer = ''
		try:
			os.makedirs(LOGS_FOLDER)
			self.file = open(os.path.join(LOGS_FOLDER, '%s.txt' % prog),'w')
		except OSError:
			pass

	def write(self, text, stdout=False):
		if self.file:
			self.file.write(text)
			if FSYNC:
				self.file.flush()
				os.fsync(self.file.fileno())

		if not self.window:
			if stdout:
				self.buffer += text
				return
			else:
				self.window = InternalErrorDialog(self.toplevel, self.prog, self)
				if self.buffer:
					text = self.buffer+'\n'+text
		self.window.text['state'] = NORMAL
		self.window.text.insert(END, text)
		self.window.text['state'] = DISABLED

class OutputHandler:
	def __init__(self, file):
		self.file = file

	def write(self, text):
		self.file.write(text, True)

def setup_trace(toplevel, prog):
	sys.stderr = ErrorHandler(toplevel, prog)
	if DEBUG:
		sys.stdout = OutputHandler(sys.stderr)