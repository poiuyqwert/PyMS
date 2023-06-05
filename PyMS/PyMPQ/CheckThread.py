
import os, time
from _thread import start_new_thread

from typing import Callable, Any

class CheckThread:
	delay = 1

	def __init__(self, callback, path): # type: (Callable[[list[str]], None], str) -> None
		self.callback = callback
		self.path = path
		self.cont = True
		self.thread = None # type: int | None

	def check_update(self, _): # type: (Any) -> None
		m = {} # type: dict[str, float]
		def check_dir(path, main=False): # type: (str, bool) -> (list[str] | None)
			u = [] # type: list[str]
			for r,ds,fs in os.walk(path, topdown=False):
				#print(r,ds,fs)
				if main and not fs and not ds:
					return None
				for f in fs:
					p = os.path.join(r,f)
					s = os.stat(p).st_mtime
					#print('\t',p,s,m)
					if p in m and s > m[p]:
						u.append(p)
					m[p] = s
				for d in ds:
					files = check_dir(os.path.join(r,d))
					if files:
						u.extend(files)
			#print(u)
			return u
		while self.cont:
			if not os.path.exists(self.path):
				break
			#print('-----')
			u = check_dir(self.path, True)
			if u is None:
				break
			elif u:
				# u.append('test')
				self.callback([f.replace(self.path,'') for f in u])
				# self.parent.after(1, self.parent.update_files, [f.replace(self.path,'') for f in u])
			time.sleep(self.delay)
		self.thread = None

	def start(self): # type: () -> None
		if self.thread is None:
			self.thread = start_new_thread(self.check_update,(0,))
		else:
			self.cont = True

	def end(self): # type: () -> None
		if self.thread is not None:
			self.cont = False

	def is_running(self): # type: () -> bool
		return self.thread is not None and self.cont
