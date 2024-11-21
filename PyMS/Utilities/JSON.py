
from __future__ import annotations

from .PyMSError import PyMSError
from . import IO

import json as _json
import enum as _enum

from typing import TypeAlias, Sequence, runtime_checkable, Protocol, Self, Type, TypeVar, Callable, overload

Value: TypeAlias = 'int | float | str | bool | None | Object | Array'
Object = dict[str, Value]
Array = Sequence[Value]

@runtime_checkable
class Decodable(Protocol):
	@classmethod
	def from_json(self, json: Object) -> Self:
		...

@runtime_checkable
class Encodable(Protocol):
	def to_json(self) -> Object:
		...

@runtime_checkable
class Codable(Decodable, Encodable, Protocol):
	pass

D = TypeVar('D', bound=Decodable)
E = TypeVar('E', bound=Encodable)
C = TypeVar('C', bound=Codable)
Discriminator = Callable[[Object], Type[C]]

def _value(value: Value, key: str, index: int | None, type: Type[T]) -> T:
	description: str
	if index is None:
		description = f'`{key}`'
	else:
		description = f'Index {index} of array `{key}`'
	if isinstance(type, Decodable):
		if not isinstance(value, dict):
			raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid value)')
		return type.from_json(value)
	if issubclass(type, _enum.StrEnum):
		if not isinstance(value, str):
			raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid value)')
		try:
			return type(value) # type: ignore[return-value]
		except:
			raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid enum case)')
	if issubclass(type, _enum.IntEnum):
		if not isinstance(value, int):
			raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid value)')
		try:
			return type(value) # type: ignore[return-value]
		except:
			raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid enum case)')
	if not isinstance(value, type):
		raise PyMSError('JSON', f'Invalid JSON format ({description} has invalid value)')
	return value

T = TypeVar('T')
def get(json: Object, key: str, type: Type[T]) -> T:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	return _value(json.get(key), key, None, type)

@overload
def get_available(json: Object, key: str, type: Type[T], default: T) -> T:
	...
@overload
def get_available(json: Object, key: str, type: Type[T], default: None = None) -> T | None:
	...
def get_available(json: Object, key: str, type: Type[T], default: T | None = None) -> T | None:
	if not key in json:
		return default
	return get(json, key, type)

def get_obj(json: Object, key: str, discriminator: Discriminator[C]) -> C:
	obj_json = get(json, key, dict)
	type = discriminator(obj_json)
	return get(json, key, type)

@overload
def get_obj_avaialable(json: Object, key: str, discriminator: Discriminator[C], default: C) -> C:
	...
@overload
def get_obj_avaialable(json: Object, key: str, discriminator: Discriminator[C], default: None = None) -> C | None:
	...
def get_obj_avaialable(json: Object, key: str, discriminator: Discriminator[C], default: C | None = None) -> C | None:
	if not key in json:
		return default
	return get_obj(json, key, discriminator)

def get_array(json: Object, key: str, type: Type[T]) -> list[T]:
	if not key in json:
		raise PyMSError('JSON', f'Invalid JSON format (missing `{key}`)')
	value = json.get(key)
	if not isinstance(value, list):
		raise PyMSError('JSON', f'Invalid JSON format (invalid `{key}` value)')
	for index in range(len(value)):
		value[index] = _value(value[index], key, index, type)
	return value

@overload
def get_array_available(json: Object, key: str, type: Type[T], default: list[T]) -> list[T]:
	...
@overload
def get_array_available(json: Object, key: str, type: Type[T], default: None = None) -> list[T] | None:
	...
def get_array_available(json: Object, key: str, type: Type[T], default: list[T] | None = None) -> list[T] | None:
	if not key in json:
		return default
	return get_array(json, key, type)

def get_array_obj(json: Object, key: str, discriminator: Discriminator[C]) -> list[C]:
	type = discriminator(json)
	return get_array(json, key, type)

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

def load_file(input: IO.AnyInputText, as_type: Type[D]) -> D:
	with IO.InputText(input) as f:
		json: Value = _json.load(f)
	if not isinstance(json, dict):
		raise PyMSError('JSON', f'Invalid JSON format (expected object)')
	return as_type.from_json(json)
