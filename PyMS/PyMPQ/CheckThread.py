
import os, time
from thread import start_new_thread

class CheckThread:
	delay = 1

	def __init__(self, parent, path):
		self.parent = parent
		self.path = path
		self.cont = True
		self.thread = None

	def check_update(self, _):
		m = {}
		def check_dir(path, main=False):
			u = []
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
					u.extend(check_dir(os.path.join(r,d)))
			#print(u)
			return u
		while self.cont:
			if not os.path.exists(self.path):
				break
			#print('-----')
			u = check_dir(self.path, True)
			if u == None:
				break
			elif u:
				# u.append('test')
				self.parent.after(1, self.parent.update_files, map(lambda f: f.replace(self.path,''),u))
			time.sleep(self.delay)
		self.thread = None

	def start(self):
		if self.thread == None:
			self.thread = start_new_thread(self.check_update,(0,))
		else:
			self.cont = True

	def end(self):
		if self.thread != None:
			self.cont = False

	def is_running(self):
		return self.thread != None and self.cont
