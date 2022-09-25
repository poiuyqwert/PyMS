
from Callback import Callback

class State(object):
	@staticmethod
	def _get(field):
		attr = '_' + field
		def _get(self): # type: (State) -> Any
			return getattr(self, attr)
		return _get

	@staticmethod
	def _set(field):
		attr = '_' + field
		def _set(self, value): # type: (State, Any) -> None
			if getattr(self, attr) == value:
				return
			setattr(self, attr, value)
			self.__field_updated(field)
		return _set

	@staticmethod
	def property(field):
		return property(State._get(field), State._set(field))

	def __init__(self):
		self.__callbacks = {} # type: dict[str | None, Callback]

	def __field_updated(self, field): # type: (str) -> None
		callback = self.__callbacks.get(field)
		if callback:
			callback()
		callback = self.__callbacks.get(None)
		if callback:
			callback()

	def observe(self, callback, *fields): # type: (Callable[None,None], *str) -> None
		if not fields:
			if not None in self.__callbacks:
				self.__callbacks[None] = Callback()
			self.__callbacks[None] += callback
			return
		for field in fields:
			if not field in self.__callbacks:
				self.__callbacks[field] = Callback()
			self.__callbacks[field] += callback

	def remove_observer(self, callback, *fields): # type: (Callable[None,None], *str) -> None
		if not fields:
			fields = self.__callbacks.keys()
		for field in fields:
			if not field in self.__callbacks:
				continue
			self.__callbacks[field] -= callback

def main():
	class MyState(State):
		class Field:
			file = 'file'
			file_path = 'file_path'

		def __init__(self):
			State.__init__(self)
			self._file = None # type: str
			self._file_path = None

		file = State.property(Field.file) # type: str
		file_path = State.property(Field.file_path) # type: str

	state = MyState()
	print(state.file)
	state.file = 'test'
	print(state.file)

	def update_title():
		print('Update title')
	state.observe(update_title, MyState.Field.file)
	state.file = 'test2'
	state.remove_observer(update_title, MyState.Field.file_path)
	state.file = 'test'
	state.remove_observer(update_title, MyState.Field.file)
	state.file = 'test2'

	state.observe(update_title)
	state.file = 'test'
	state.file_path = 'test'
	state.remove_observer(update_title)
	state.file_path = 'test2'

if __name__ == '__main__':
	main()