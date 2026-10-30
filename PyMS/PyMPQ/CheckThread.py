
import os, threading

from typing import Callable

class CheckThread:
	delay = 1

	def __init__(self, callback: Callable[[list[str]], None], path: str) -> None:
		self.callback = callback
		self.path = path
		self.thread: threading.Thread | None = None
		self.stop_event = threading.Event()

	def check_update(self) -> None:
		m: dict[str, float] = {}
		def check_dir(path: str, main: bool = False) -> list[str] | None:
			u: list[str] = []
			for r,ds,fs in os.walk(path, topdown=False):
				if main and not fs and not ds:
					return None
				for f in fs:
					p = os.path.join(r,f)
					s = os.stat(p).st_mtime
					if p in m and s > m[p]:
						u.append(p)
					m[p] = s
				for d in ds:
					files = check_dir(os.path.join(r,d))
					if files:
						u.extend(files)
			return u
		while not self.stop_event.is_set():
			if not os.path.exists(self.path):
				break
			u = check_dir(self.path, True)
			if u is None:
				break
			if u:
				self.callback([f.replace(self.path,'') for f in u])
			self.stop_event.wait(CheckThread.delay)

	def start(self) -> None:
		if self.is_running():
			return
		self.stop_event.clear()
		self.thread = threading.Thread(target=self.check_update, name='PyMPQ CheckThread', daemon=True)
		self.thread.start()

	def end(self) -> None:
		if self.thread is None:
			return
		self.stop_event.set()
		self.thread.join()
		self.thread = None

	def is_running(self) -> bool:
		return self.thread is not None and self.thread.is_alive()
