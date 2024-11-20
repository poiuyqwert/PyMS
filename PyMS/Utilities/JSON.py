
from __future__ import annotations

from .PyMSError import PyMSError

from typing import TypeAlias, Sequence, runtime_checkable, Protocol, Self, Type, TypeVar, Callable

Value: TypeAlias = 'int | float | str | bool | None | Object | Array'
Object = dict[str, Value]
Array = Sequence[Value]

@runtime_checkable
class Codable(Protocol):
	@classmethod
	def from_json(self, json: Object) -> Self:
		...

	def to_json(self) -> Object:
		...

C = TypeVar('C', bound=Codable)
Discriminator = Callable[[Object], Type[C]]

T = TypeVar('T')
def get(json: Object, key: str, type: Type[T]) -> T:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	value = json.get(key)
	if isinstance(type, Codable):
		if not isinstance(value, dict):
			raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
		return type.from_json(value)
	if not isinstance(value, type):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
	return value

def get_obj(json: Object, key: str, discriminator: Discriminator[C]) -> C:
	obj_json = get(json, key, dict)
	type = discriminator(obj_json)
	return get(json, key, type)

def get_array(json: Object, key: str, type: Type[T]) -> list[T]:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	value = json.get(key)
	if not isinstance(value, list):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
	for index in range(len(value)):
		if isinstance(type, Codable):
			try:
				value[index] = type.from_json(value[index])
			except:
				raise PyMSError('JSON', f'Invalid JSON format (array `{key}` contains invalid value at index {index})')
		elif not isinstance(value[index], type):
			raise PyMSError('JSON', f'Invalid JSON format (array `{key}` contains invalid value at index {index})')
	return value

def get_array_obj(json: Object, key: str, discriminator: Discriminator[C]) -> list[C]:
	type = discriminator(json)
	return get_array(json, key, type)
