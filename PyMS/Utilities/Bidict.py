
from typing import Generic, TypeVar, Sequence

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

	def __setitem__(self, key: K, value: V) -> None:
		if key in self._value_map:
			del self._key_map[self._value_map[key]]
		if value in self._key_map:
			del self._value_map[self._key_map[value]]
		self._value_map[key] = value
		self._key_map[value] = key

	def __getitem__(self, key: K) -> V:
		return self._value_map[key]

	def __delitem__(self, key: K) -> None:
		value = self._value_map[key]
		del self._value_map[key]
		del self._key_map[value]

	def keys(self) -> Sequence[K]:
		return self._value_map.keys() # type: ignore[return-value]

	def values(self) -> Sequence[V]:
		return self._value_map.values() # type: ignore[return-value]

	def items(self) -> Sequence[tuple[K, V]]:
		return self._value_map.items() # type: ignore[return-value]

	def __contains__(self, key: K) -> bool:
		return key in self._value_map

	def has_value(self, value: V) -> bool:
		return value in self._key_map
