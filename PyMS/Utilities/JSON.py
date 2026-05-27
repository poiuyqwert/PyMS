
from __future__ import annotations

from .PyMSError import PyMSError

from typing import TypeAlias, Sequence, runtime_checkable, Protocol, Self, Type, TypeVar, Callable

Value: TypeAlias = 'int | float | str | bool | None | Object | Array'
Object = dict[str, Value]
Array = Sequence[Value]

@runtime_checkable
class Codable(Protocol):
	@classmethod
	def from_json(cls, json: Object) -> Self:
		...

	def to_json(self) -> Object:
		...

C = TypeVar('C', bound=Codable)
Discriminator = Callable[[Object], Type[C]]

T = TypeVar('T')
def get(json: Object, key: str, val_type: Type[T]) -> T:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	value = json.get(key)
	if isinstance(val_type, type) and issubclass(val_type, Codable):
		if not isinstance(value, dict):
			raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
		return val_type.from_json(value) # type: ignore
	if not isinstance(value, val_type):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
	return value

def get_obj(json: Object, key: str, discriminator: Discriminator[C]) -> C:
	obj_json = get(json, key, dict)
	val_type = discriminator(obj_json)
	return get(json, key, val_type)

def get_array(json: Object, key: str, val_type: Type[T]) -> list[T]:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	array = json.get(key)
	if not isinstance(array, list):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
	is_codable = isinstance(val_type, type) and issubclass(val_type, Codable)
	result: list[T] = []
	for index,value in enumerate(array):
		if is_codable:
			try:
				value = val_type.from_json(value) # type: ignore
			except Exception as exc:
				raise PyMSError('JSON', f'Invalid JSON format (array `{key}` contains invalid value at index {index})') from exc
		elif not isinstance(value, val_type):
			raise PyMSError('JSON', f'Invalid JSON format (array `{key}` contains invalid value at index {index})')
		result.append(value)
	return result

def get_array_obj(json: Object, key: str, discriminator: Discriminator[C]) -> list[C]:
	val_type = discriminator(json)
	return get_array(json, key, val_type)
