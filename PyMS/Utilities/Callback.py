
from typing import Callable, Self, Any

class Callback(object):
	def __init__(self): # type: () -> None
		self.callbacks = [] # type: list[Callable]

	def clear(self): # type: () -> None
		self.callbacks.clear()

	def add(self, callback): # type: (Callable) -> None
		self.callbacks.append(callback)

	def __add__(self, callback): # type: (Callable) -> Self
		self.add(callback)
		return self

	def remove(self, callback): # type: (Callable) -> None
		if not callback in self.callbacks:
			return
		self.callbacks.remove(callback)

	def __sub__(self, callback): # type: (Callable) -> Self
		self.remove(callback)
		return self

	def set(self, callback): # type: (Callable) -> None
		self.callbacks = [callback]

	def __call__(self, *args, **kwargs): # type: (Any, Any) -> None
		for callback in self.callbacks:
			callback(*args, **kwargs)
