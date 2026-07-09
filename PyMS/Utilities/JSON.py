
from __future__ import annotations

from .PyMSError import PyMSError
from . import IO

import json as _json
import enum as _enum

from typing import TypeAlias, Sequence, runtime_checkable, Protocol, Self, Type, TypeVar, Callable, overload, Any, TypeGuard

Primitive: TypeAlias = int | float | str | bool | None
Value: TypeAlias = 'Primitive | Object | Array'
Object = dict[str, Value]
Array = Sequence[Value]

def is_json_primitive(json: Any) -> TypeGuard[Primitive]:
	return isinstance(json, (int, float, str, bool)) or json is None

def is_json_object(json: Any, lazy: bool = False) -> TypeGuard[Object]:
	if not isinstance(json, dict):
		return False
	if lazy:
		return True
	for key, value in json.items():
		if not isinstance(key, str):
			return False
		if not is_json_value(value):
			return False
	return True

def is_json_array(json: Any, lazy: bool = False) -> TypeGuard[Array]:
	if not isinstance(json, Sequence):
		return False
	if lazy:
		return True
	for value in json:
		if not is_json_value(value):
			return False
	return True

def is_json_value(json: Any, lazy: bool = False) -> TypeGuard[Value]:
	return is_json_primitive(json) or is_json_object(json, lazy) or is_json_array(json, lazy)

@runtime_checkable
class Decodable(Protocol):
	@classmethod
	def from_json(cls, json: Object) -> Self:
		...

@runtime_checkable
class Encodable(Protocol):
	def to_json(self) -> Object:
		...

@runtime_checkable
class Codable(Decodable, Encodable, Protocol):
	pass

T = TypeVar('T')
D = TypeVar('D', bound=Decodable)
E = TypeVar('E', bound=Encodable)
C = TypeVar('C', bound=Codable)
Discriminator = Callable[[Object], Type[C]]

def _value(value: Value, key: str, index: int | None, val_type: Type[T]) -> T:
	description: str
	if index is None:
		description = f'invalid `{key}`'
	else:
		description = f'array `{key}` contains invalid value at index {index}'
	if isinstance(val_type, Decodable):
		if not isinstance(value, dict):
			raise PyMSError('JSON', f'Invalid JSON format ({description})')
		try:
			return val_type.from_json(value)
		except Exception as exc:
			if index is None:
				raise
			raise PyMSError('JSON', f'Invalid JSON format ({description})') from exc
	if issubclass(val_type, _enum.StrEnum):
		if not isinstance(value, str):
			raise PyMSError('JSON', f'Invalid JSON format ({description})')
		try:
			return val_type(value) # type: ignore[return-value]
		except ValueError as exc:
			raise PyMSError('JSON', f'Invalid JSON format ({description}, invalid enum case)') from exc
	if issubclass(val_type, _enum.IntEnum):
		if not isinstance(value, int):
			raise PyMSError('JSON', f'Invalid JSON format ({description})')
		try:
			return val_type(value) # type: ignore[return-value]
		except ValueError as exc:
			raise PyMSError('JSON', f'Invalid JSON format ({description}, invalid enum case)') from exc
	if not isinstance(value, val_type):
		raise PyMSError('JSON', f'Invalid JSON format ({description})')
	return value

def get(json: Object, key: str, val_type: Type[T]) -> T:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	return _value(json.get(key), key, None, val_type)

@overload
def get_available(json: Object, key: str, val_type: Type[T], default: T) -> T:
	...
@overload
def get_available(json: Object, key: str, val_type: Type[T], default: None = None) -> T | None:
	...
def get_available(json: Object, key: str, val_type: Type[T], default: T | None = None) -> T | None:
	if not key in json:
		return default
	return get(json, key, val_type)

def get_obj(json: Object, key: str, discriminator: Discriminator[C]) -> C:
	obj_json = get(json, key, dict)
	val_type = discriminator(obj_json)
	return get(json, key, val_type)

@overload
def get_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: C) -> C:
	...
@overload
def get_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: None = None) -> C | None:
	...
def get_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: C | None = None) -> C | None:
	if not key in json:
		return default
	return get_obj(json, key, discriminator)

def get_array(json: Object, key: str, val_type: Type[T]) -> list[T]:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	array = json.get(key)
	if not isinstance(array, list):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}`)')
	result: list[T] = []
	for index, value in enumerate(array):
		result.append(_value(value, key, index, val_type))
	return result

@overload
def get_array_available(json: Object, key: str, val_type: Type[T], default: list[T]) -> list[T]:
	...
@overload
def get_array_available(json: Object, key: str, val_type: Type[T], default: None = None) -> list[T] | None:
	...
def get_array_available(json: Object, key: str, val_type: Type[T], default: list[T] | None = None) -> list[T] | None:
	if not key in json:
		return default
	return get_array(json, key, val_type)

def get_array_obj(json: Object, key: str, discriminator: Discriminator[C]) -> list[C]:
	val_type = discriminator(json)
	return get_array(json, key, val_type)

@overload
def get_array_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: list[C]) -> list[C]:
	...
@overload
def get_array_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: None = None) -> list[C] | None:
	...
def get_array_obj_available(json: Object, key: str, discriminator: Discriminator[C], default: list[C] | None = None) -> list[C] | None:
	if not key in json:
		return default
	return get_array_obj(json, key, discriminator)

def load_file(any_input: IO.AnyInputText, as_type: Type[D]) -> D:
	with IO.InputText(any_input) as f:
		json: Value = _json.load(f)
	if not isinstance(json, dict):
		raise PyMSError('JSON', 'Invalid JSON format (expected object)')
	return as_type.from_json(json)
