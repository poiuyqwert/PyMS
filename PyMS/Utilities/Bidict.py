
from typing import Generic, TypeVar, overload

K = TypeVar('K')
V = TypeVar('V')
class Bidict(Generic[K,V]):
	def __init__(self, _dict: dict[K, V]):
		self._value_map = {key: value for key,value in _dict.items()}
		self._key_map = {value: key for key,value in _dict.items()}

	def key_of(self, value: V) -> K:
		return self._key_map[value]

	def get_key_of(self, value: V, defualt: K | None = None) -> (K | None):
		return self._key_map.get(value, defualt)

	def __setitem__(self, key: K, value: V):
		self._value_map[key] = value
		self._key_map[value] = key

	def __getitem__(self, key: K) -> V:
		return self._value_map[key]

	def __delitem__(self, key: K):
		value = self._value_map[key]
		del self._value_map[key]
		del self._key_map[value]

	def keys(self):
		return self._value_map.keys()

	def values(self):
		return self._value_map.values()

	def items(self):
		return self._value_map.items()

	def __contains__(self, key: K) -> bool:
		return key in self._value_map

	def has_value(self, value: V) -> bool:
		return value in self._key_map
