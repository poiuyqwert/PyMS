
from __future__ import annotations

from . import Assets
from .InternalErrorDialog import InternalErrorDialog
from .UIKit import MainWindow, Toplevel, AnyWindow

import sys, os

from typing import TextIO

try:
	os.makedirs(Assets.logs_dir)
except:
	pass

class Tracer(object):
	class STDStream(object):
		def __init__(self, tracer: Tracer, stream: TextIO | None) -> None:
			self.tracer = tracer
			self.stream = stream

		def write(self, text: str) -> None:
			if self.stream:
				try:
					self.stream.write(text)
				except:
					pass
			self.tracer.write(text, self)

		def flush(self) -> None:
			pass

	def __init__(self, program_name: str, main_window: MainWindow) -> None:
		self.stdout = Tracer.STDStream(self, sys.stdout)
		self.stderr = Tracer.STDStream(self, sys.stderr)
		self.program_name = program_name
		self.main_window = main_window
		self.window: InternalErrorDialog | None = None
		self.creating_window = False
		self.buffer = ''
		self.flush_after_id: str | None = None
		try:
			self.file = open(Assets.log_file_path('%s.txt' % program_name), 'w', encoding='utf-8')
		except OSError:
			pass

	def _find_presenter(self) -> AnyWindow:
		presenter = self.main_window
		children = presenter.winfo_children()
		while len(children) and isinstance(children[-1], Toplevel):
			presenter = children[-1]
			children = presenter.winfo_children()
		return presenter

	def _present(self) -> None:
		if self.creating_window:
			return
		if self.window is None:
			self.creating_window = True
			def present() -> None:
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

	def write(self, text: str, source: STDStream | None = None) -> None:
		if self.file:
			self.file.write(text)
			if self.flush_after_id is not None:
				self.main_window.after_cancel(self.flush_after_id)
			self.flush_after_id = self.main_window.after(10, self.flush)
		if self.window:
			self.window.add_text(text)
		else:
			self.buffer += text
			if source == self.stderr:
				self._present()

	def flush(self) -> None:
		if self.flush_after_id is not None:
			self.main_window.after_cancel(self.flush_after_id)
			self.flush_after_id = None
		if not self.file:
			return
		self.file.flush()

	def trace_error(self) -> None:
		import traceback
		self.write(''.join(traceback.format_exception(*sys.exc_info())))

_TRACER: Tracer | None = None
def setup_trace(program_name: str, main_window: MainWindow) -> None:
	global _TRACER
	if _TRACER is not None:
		return
	_TRACER = Tracer(program_name, main_window)
	sys.stdout = _TRACER.stdout
	sys.stderr = _TRACER.stderr

def get_tracer() -> Tracer | None:
	return _TRACER
