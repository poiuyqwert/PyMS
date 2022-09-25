
class Callback(object):
	def __init__(self):
		self.callbacks = []

	def clear(self):
		self.callbacks = []

	def add(self, callback):
		self.callbacks.append(callback)

	def __add__(self, callback):
		self.add(callback)
		return self

	def remove(self, callback):
		if not callback in self.callbacks:
			return
		self.callbacks.remove(callback)

	def __sub__(self, callback):
		self.remove(callback)
		return self

	def set(self, callback):
		self.callbacks = [callback]

	def __call__(self, *args, **kwargs):
		for callback in self.callbacks:
			callback(*args, **kwargs)
