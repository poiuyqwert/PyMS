
from __future__ import annotations

from ...Utilities.UIKit import Frame, Misc
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

from typing import Self, Type, Callable, TypeVar, Generic

class CodeGeneratorType(JSON.Codable):
	@classmethod
	def type_name(cls) -> str:
		raise NotImplementedError(cls.__name__ + '.type_name()')

	@classmethod
	def from_json(self, json: JSON.Object) -> Self:
		raise NotImplementedError(self.__class__.__name__ + '.from_json()')

	def to_json(self) -> JSON.Object:
		return {
			'type': self.type_name()
		}

	# None for infinite
	def count(self) -> int | None:
		raise NotImplementedError(self.__class__.__name__ + '.count()')

	def value(self, lookup_value: Callable[[str], int]) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.value()')

	def description(self) -> str:
		raise NotImplementedError(self.__class__.__name__ + '.description()')

	def editor_type(self) -> Type[CodeGeneratorEditor]:
		raise NotImplementedError(self.__class__.__name__ + '.editor()')

T = TypeVar('T', bound=CodeGeneratorType)
class CodeGeneratorEditor(Frame, Generic[T]):
	def __init__(self, parent: Misc, generator: T):
		self.generator = generator
		Frame.__init__(self, parent)

	def save(self):
		raise NotImplementedError(self.__class__.__name__ + '.save()')

_REGISTRY: dict[str, Type[CodeGeneratorType]] = {}

def register_type(type: Type[CodeGeneratorType]):
	_REGISTRY[type.type_name()] = type

def lookup_type(name: str) -> Type[CodeGeneratorType] | None:
	return _REGISTRY.get(name)

def discriminate_type(json: JSON.Object) -> Type[CodeGeneratorType]:
	name = json.get('type')
	if not isinstance(name, str):
		raise PyMSError('JSON', 'Invalid JSON format (object missing discriminator type)')
	type = lookup_type(name)
	if not type:
		raise PyMSError('JSON', f'Invalid JSON format (object has invalid discriminator type `{name}`)')
	return type
