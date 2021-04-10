
class Callback(object):
	def __init__(self):
		self.callbacks = []

	def clear(self):
		self.callbacks = []

	def add(self, callback):
		self.callbacks.append(callback)

	def set(self, callback):
		self.callbacks =  [callback]

	def __call__(self, *args, **kwargs):
		for callback in self.callbacks:
			callback(*args, **kwargs)
