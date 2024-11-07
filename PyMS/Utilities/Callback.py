
from typing import ParamSpec, Generic, Callable, Self

P = ParamSpec('P')

class Callback(Generic[P]):
	def __init__(self) -> None:
		self.callbacks: list[Callable[P, None]] = []

	def clear(self) -> None:
		self.callbacks.clear()

	def add(self, callback: Callable[P, None]) -> None:
		self.callbacks.append(callback)

	def __add__(self, callback: Callable[P, None]) -> Self:
		self.add(callback)
		return self

	def remove(self, callback: Callable[P, None]) -> None:
		if not callback in self.callbacks:
			return
		self.callbacks.remove(callback)

	def __sub__(self, callback: Callable[P, None]) -> Self:
		self.remove(callback)
		return self

	def set(self, callback: Callable[P, None]) -> None:
		self.callbacks = [callback]

	def __call__(self, *args: P.args, **kwargs: P.kwargs) -> None:
		for callback in self.callbacks:
			callback(*args, **kwargs)
