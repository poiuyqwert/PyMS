
from __future__ import annotations

from .PyMSError import PyMSError

import re
from enum import Enum, Flag
from collections import OrderedDict

from typing import Type, Any, TypeAlias, Sequence, Protocol, TypeVar, Callable, Generic

JSONObject = dict[str, 'JSONValue'] | OrderedDict[str, 'JSONValue']
JSONArray = Sequence['JSONValue']
JSONValue: TypeAlias = int | float | str | bool | None | JSONObject | JSONArray

SubFields = dict[str, bool]
Fields = dict[str, bool | SubFields]

V = TypeVar('V')
class Encoder(Generic[V]):
	def encode(self, value: V) -> JSONValue:
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, value: JSONValue) -> V:
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class GroupEncoder(Generic[V]):
	def encode(self, value: V, fields: Fields | SubFields | None) -> JSONValue:
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, value: JSONValue, field: str, current: Any | None) -> V:
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class SplitEncoder(Generic[V]):
	attr: str

	def encode(self, value: V) -> JSONValue:
		raise NotImplementedError(self.__class__.__name__ + '.encode()')

	def decode(self, value: JSONValue, current: Any | None) -> V:
		raise NotImplementedError(self.__class__.__name__ + '.decode()')

class IntEncoder(Encoder[int]):
	_RE = re.compile(r'^\d+$')
	def __init__(self, min: int | None = None, max: int | None = None):
		self.min = min
		self.max = max

	def encode(self, value: int) -> JSONValue:
		return value

	def decode(self, value: JSONValue) -> int:
		if isinstance(value, str):
			if not IntEncoder._RE.match(value):
				raise PyMSError('Decode', f"Expected an integer, got '{value}'")
			value = int(value)
		if not isinstance(value, int):
			raise PyMSError('Decode', f"Expected an integer, got '{value}'")
		if self.min is not None and value < self.min:
			raise PyMSError('Decode', f'{self.min} is the minimum value, got {value}')
		if self.max is not None and value > self.max:
			raise PyMSError('Decode', f'{self.max} is the maximum value, got {value}')
		return value

class FloatEncoder(Encoder[float]):
	def __init__(self, min: float | None = None, max: float | None = None):
		self.min = min
		self.max = max

	def encode(self, value: float) -> JSONValue:
		return value

	def decode(self, value: JSONValue) -> float:
		if not isinstance(value, float) and not isinstance(value, int):
			raise PyMSError('Decode', f"Expected a float/integer, got '{value}'")
		if self.min is not None and value < self.min:
			raise PyMSError('Decode', f'{self.min} is the minimum value, got {value}')
		if self.max is not None and value > self.max:
			raise PyMSError('Decode', f'{self.max} is the maximum value, got {value}')
		return value

class BoolEncoder(Encoder[bool]):
	def encode(self, value: bool) -> JSONValue:
		return value

	@staticmethod
	def parse(value: JSONValue) -> bool:
		if isinstance(value, bool):
			return value
		if isinstance(value, str):
			if value.lower() in ('true', 't', '1'):
				return True
			if value.lower() in ('false', 'f', '0'):
				return False
		if value == 0:
			return False
		if value == 1:
			return True
		raise PyMSError('Decode', f"Expected a boolen ('true', 't', '1', 'false', 'f', or '0'), got '{value}'")

	def decode(self, value: JSONValue) -> bool:
		return BoolEncoder.parse(value)

class StrEncoder(Encoder[str]):
	def __init__(self, max_length: int | None = None):
		self.max_length = max_length

	def encode(self, value: str) -> JSONValue:
		return value

	def decode(self, value: JSONValue) -> str:
		if not isinstance(value, str):
			raise PyMSError('Decode', f"Expected a string, got '{value}")
		if self.max_length is not None and len(value) > self.max_length:
			raise PyMSError('Decode', f'{self.max_length} is the maximum length, got {len(value)}')
		return value

F = TypeVar('F', bound=Flag)
class FlagEncoder(GroupEncoder[F]):
	def __init__(self, zero_flags: F):
		self.zero_flags = zero_flags

	def encode(self, value: F, fields: Fields | SubFields | None) -> JSONValue:
		f_type = type(self.zero_flags)
		flags: OrderedDict = OrderedDict()
		for flag_name in dir(f_type):
			if flag_name.startswith('_'):
				continue
			if fields is not None and not fields.get(flag_name):
				continue
			flag = getattr(value, flag_name)
			if callable(flag):
				continue
			has_flag = (value & flag) == flag
			flags[flag_name] = has_flag
		return flags

	def decode(self, value: JSONValue, field: str, current: F | None) -> F:
		if current is not None:
			result = current
		else:
			result = self.zero_flags
		f_type = type(self.zero_flags)
		if not hasattr(f_type, field):
			raise PyMSError('Decode', f"'{field}' is not a valid flag name")
		flag = getattr(f_type, field)
		if not isinstance(flag, f_type):
			raise PyMSError('Decode', f"'{field}' is not a valid flag name")
		has_flag = BoolEncoder.parse(value)
		if has_flag:
			result |= flag
		return result

class IntFlagEncoder(GroupEncoder[int]):
	def __init__(self, flags: dict[str, int]) -> None:
		self.flags = flags

	def encode(self, value: int, fields: Fields | SubFields | None) -> JSONValue:
		flags: OrderedDict = OrderedDict()
		for flag_name,flag in sorted(self.flags.items(), key=lambda t: t[1]):
			if fields is not None and not fields.get(flag_name):
				continue
			has_flag = (value & flag) == flag
			flags[flag_name] = has_flag
		return flags

	def decode(self, value: JSONValue, field: str, current: int | None) -> int:
		if current is not None:
			result = current
		else:
			result = 0
		for flag_name,flag in self.flags.items():
			if field == flag_name:
				has_flag = BoolEncoder.parse(value)
				if has_flag:
					result |= flag
				break
		else:
			raise PyMSError('Decode', f"'{field}' is not a valid flag name")
		return result

E = TypeVar('E', bound=Enum)
class EnumValueEncoder(Encoder[E]):
	def __init__(self, enum_type: Type[E]) -> None:
		self.enum_type = enum_type

	def encode(self, value: E) -> JSONValue:
		return value.value

	def decode(self, value: JSONValue) -> E:
		try:
			return self.enum_type(value)
		except:
			raise PyMSError('Decode', f"'{value}' is not a valid option")

class EnumNameEncoder(Encoder[E]):
	def __init__(self, enum_type: Type[E]) -> None:
		self.enum_type = enum_type

	def encode(self, value: E) -> JSONValue:
		return value.name

	def decode(self, value: JSONValue) -> E:
		if not isinstance(value, str):
			raise PyMSError('Decode', f"Expected a string, got '{value}'")
		if not hasattr(self.enum_type, value):
			raise PyMSError('Decode', f"'{value}' is not a valid option")
		value = getattr(self.enum_type, value)
		if not isinstance(value, self.enum_type):
			raise PyMSError('Decode', f"'{value}' is not a valid option")
		return value

class JoinEncoder(Encoder[V]):
	def __init__(self, join_name: str, field_name: str, encoder: Encoder[V]) -> None:
		self.join_name = join_name
		self.field_name = field_name
		self.encoder = encoder

	def encode(self, value: V) -> JSONValue:
		return self.encoder.encode(value)

	def decode(self, value: JSONValue) -> V:
		return self.encoder.decode(value)

class RenameEncoder(Encoder[V]):
	def __init__(self, name: str, encoder: Encoder[V]) -> None:
		self.name = name
		self.encoder = encoder

	def encode(self, value: V) -> JSONValue:
		return self.encoder.encode(value)

	def decode(self, value: JSONValue) -> V:
		return self.encoder.decode(value)

AnyEncoder = Encoder | GroupEncoder | SplitEncoder
SubStructure = dict[str, AnyEncoder]
Structure = dict[str, AnyEncoder | SubStructure]

class IDMode(Enum):
	comment = 0
	header = 1

class Definition:
	def __init__(self, name: str, id_mode: IDMode, structure: Structure):
		self.name = name
		self.id_mode = id_mode
		self.structure = structure

def _encode_json(obj: object, structure: Structure | SubStructure, fields: Fields | SubFields | None) -> OrderedDict[str, JSONValue]:
	if fields is not None and len(fields) == 0:
		raise PyMSError('Internal', 'No fields to encode')
	json: OrderedDict[str, JSONValue] = OrderedDict()
	for key,encoder in structure.items():
		field: bool | SubFields | None = None
		if fields is not None:
			field = fields.get(key)
			if not field:
				continue
		attr = key
		if isinstance(encoder, SplitEncoder):
			attr = encoder.attr
		if isinstance(encoder, RenameEncoder):
			key = encoder.name
		if not hasattr(obj, attr):
			raise PyMSError('Internal', f"'{attr}' is not a valid attribute name")
		value = getattr(obj, attr)
		if isinstance(encoder, JoinEncoder):
			if encoder.join_name in json:
				group = json[encoder.join_name]
				if not isinstance(group, dict):
					raise PyMSError('Internal', f"Group '{encoder.join_name}' has value '{group}' instead of map")
			else:
				group = OrderedDict()
				json[encoder.join_name] = group
			group[encoder.field_name] = encoder.encode(value)
			continue
		elif isinstance(encoder, GroupEncoder):
			if not isinstance(field, dict):
				field = None
			value = encoder.encode(value, field)
		elif isinstance(encoder, dict):
			if not isinstance(field, dict):
				field = None
			value = _encode_json(value, encoder, field)
		else:
			value = encoder.encode(value)
		json[key] = value
	return json

def encode_json(obj: object, id: int | None, definition: Definition, fields: Fields | None = None) -> OrderedDict[str, JSONValue]:
	json = _encode_json(obj, definition.structure, fields)
	if id is not None:
		json['_id'] = id
		json.move_to_end('_id', last=False)
	elif definition.id_mode == IDMode.header:
		raise PyMSError('Internal', f"Missing ID for '{definition.name}' object")
	json['_type'] = definition.name
	json.move_to_end('_type', last=False)
	return json

def encode_jsons(objs: Sequence[tuple[object, int]], get_definition: Callable[[object], Definition | None], fields: Fields | None = None) -> list[OrderedDict[str, JSONValue]]:
	json: list[OrderedDict[str, JSONValue]] = []
	for obj,id in objs:
		definition = get_definition(obj)
		if not definition:
			raise PyMSError('Internal', f"Object type '{obj.__class__.__name__}' has no definition")
		json.append(encode_json(obj, id, definition, fields))
	return json

def encode_text(obj: object, id: int | None, definition: Definition, fields: Fields | None = None) -> str:
	def flatten(json: dict[str, JSONValue], prefix: str | None = None) -> str:
		result = ''
		for key,value in json.items():
			if key.startswith('_'):
				continue
			if prefix:
				key = f'{prefix}.{key}'
			if isinstance(value, dict):
				result += flatten(value, key)
			elif isinstance(value, str) and '\n' in value:
				value = value.replace('\n', '\n\t\t')
				result += f'\t{key}:\n\t\t{value}\n'
			else:
				if isinstance(value, bool):
					value = 1 if value else 0
				result += f'\t{key} {value}\n'
		return result
	result: str
	if id is not None:
		match definition.id_mode:
			case IDMode.comment:
				result = f'# Export of {definition.name} {id}\n{definition.name}:\n'
			case IDMode.header:
				result = f'{definition.name}({id}):\n'
	elif definition.id_mode == IDMode.header:
		raise PyMSError('Internal', f"Missing ID for '{definition.name}' object")
	else:
		result = f'{definition.name}:\n'
	json = encode_json(obj, id, definition, fields)
	return result + flatten(json)

def encode_texts(objs: Sequence[tuple[object, int]], get_definition: Callable[[object], Definition | None], fields: Fields | None = None) -> str:
	result = ''
	for obj, id in objs:
		definition = get_definition(obj)
		if not definition:
			raise PyMSError('Internal', f"Object type '{obj.__class__.__name__}' has no definition")
		if result:
			result += '\n'
		result += encode_text(obj, id, definition, fields)
	return result

class LineScanner:
	def __init__(self, text: str) -> None:
		self.lines = text.splitlines()
		self.line = 0

	def pop(self) -> str:
		if self.at_end():
			raise PyMSError('Decode', "Unexpected end of file")
		line = self.lines[self.line]
		self.line += 1
		return line

	def peek(self) -> str:
		if self.at_end():
			raise PyMSError('Decode', "Unexpected end of file")
		return self.lines[self.line]

	def skip(self) -> None:
		self.line += 1

	def at_end(self) -> bool:
		return (self.line == len(self.lines))

_RE_COMMENT = re.compile(r'\s*(?:#|//).*$')
_RE_TYPE = re.compile(r'^([A-Z]\w+)(?:\((\d+)\))?:$')
_RE_FIELD_FLAT = re.compile(r'^([a-z]\w*(?:\.[a-z]\w*)*)\s+(.+?)$')
_RE_FIELD_MULTI = re.compile(r'^([a-z]\w*(?:\.[a-z]\w*)*):$')
def _decode_text_to_json(text: str, definitions: Sequence[Definition]) -> list[OrderedDict]:
	def _decode_value(key_path: list[str], value: str, obj: dict, structure: Structure | SubStructure) -> None:
		while len(key_path):
			key = key_path.pop(0)
			decoder = structure.get(key)
			if not decoder:
				raise PyMSError('Decode', f"'{key}' is not a valid field name")
			if isinstance(decoder, GroupEncoder):
				if len(key_path) == 0:
					raise PyMSError('Decode', f"'{key}' needs a sub-field")
				sub_key = key_path.pop(0)
				if len(key_path) > 0:
					raise PyMSError('Decode', f"'{key}.{sub_key}' can't have sub-fields")
				obj[key] = decoder.decode(value, sub_key, obj.get(key))
			elif isinstance(decoder, SplitEncoder):
				if len(key_path) > 0:
					raise PyMSError('Decode', f"'{key}' can't have sub-fields")
				obj[decoder.attr] = decoder.decode(value, obj.get(decoder.attr))
			elif isinstance(decoder, dict):
				if len(key_path) == 0:
					raise PyMSError('Decode', f"'{key}' needs a sub-field")
				sub_obj = obj.get(key)
				if not sub_obj:
					sub_obj = OrderedDict()
					obj[key] = sub_obj
					obj = sub_obj
				elif isinstance(sub_obj, dict):
					obj = sub_obj
				else:
					raise PyMSError('Decode', f"Expected '{key}' to be an object but got '{sub_obj}'")
			else:
				if len(key_path) > 0:
					raise PyMSError('Decode', f"'{key}' can't have sub-fields")
				obj[key] = decoder.decode(value)
	def _add_obj(obj: OrderedDict, definition: Definition, result: list[OrderedDict]) -> None:
		if len(obj) == 0:
			raise PyMSError('Decode', f"'{definition.name}' object is empty")
		obj['_type'] = definition.name
		obj.move_to_end('_type', last=False)
		result.append(obj)
	definition_map = {definition.name: definition for definition in definitions}
	working: OrderedDict | None = None
	definition: Definition | None = None
	result: list[OrderedDict] = []
	scanner = LineScanner(text)
	while not scanner.at_end():
		line = _RE_COMMENT.sub('', scanner.pop()).strip()
		if not line:
			continue
		match = _RE_TYPE.match(line)
		if match:
			new_definition = definition_map.get(match.group(1))
			if not new_definition:
				raise PyMSError('Decode', f"Can't find definition for '{match.group(1)}' type")
			if working:
				assert definition is not None
				_add_obj(working, definition, result)
			working = OrderedDict()
			definition = new_definition
			continue
		match = _RE_FIELD_FLAT.match(line)
		if match:
			if working is None or definition is None:
				raise PyMSError('Decode', f"Expected an object start ('<type>:'), got '{line}'")
			obj: OrderedDict = working
			structure: Structure | SubStructure = definition.structure
			key_path = match.group(1).split('.')
			value = match.group(2)
			_decode_value(key_path, value, obj, structure)
			continue
		match = _RE_FIELD_MULTI.match(line)
		if match:
			if working is None or definition is None:
				raise PyMSError('Decode', f"Expected an object start ('<type>:'), got '{line}'")
			obj = working
			structure = definition.structure
			key_path = match.group(1).split('.')
			value = ''
			while not scanner.at_end():
				line = _RE_COMMENT.sub('', scanner.peek()).strip()
				if not line:
					continue
				if _RE_TYPE.match(line) or _RE_FIELD_FLAT.match(line) or _RE_FIELD_MULTI.match(line):
					break
				if value:
					value += '\n'
				value += line
				scanner.skip()
			_decode_value(key_path, value, obj, structure)
			continue
		raise PyMSError('Decoding', f"Unexpected line '{line}'")
	if working:
		assert definition is not None
		_add_obj(working, definition, result)
	if not len(result):
		raise PyMSError('Decoding', 'Nothing to decode.')
	return result

Repeater = Callable[[int, int, int], int | None]

def repeater_ignore(decode_count: int, obj_n: int, obj_count: int) -> (int | None):
	if obj_n >= decode_count:
		return None
	return obj_n

def repeater_loop(decode_count: int, obj_n: int, obj_count: int) -> (int | None):
	return obj_n % decode_count

def repeater_repeat_last(decode_count: int, obj_n: int, obj_count: int) -> (int | None):
	return min(obj_n, decode_count-1)

O = TypeVar('O')
def decode_text(text: str, definitions: Sequence[Definition], builder: Callable[[Definition], O], objs: int | None = None, repeater: Repeater = repeater_ignore) -> list[O]:
	def _apply(json: dict[str, Any], obj: object):
		for key,value in json.items():
			if key.startswith('_'):
				continue
			if not hasattr(obj, key):
				raise PyMSError('Decode', f"'{key}' is not a valid field name")
			if isinstance(value, dict):
				_apply(value, getattr(obj, key))
			else:
				setattr(obj, key, value)
	jsons = _decode_text_to_json(text, definitions)
	decode_count = len(jsons)
	definition_map = {definition.name: definition for definition in definitions}
	result: list[O] = []
	count: int
	if objs is not None:
		count = objs
	else:
		count = len(jsons)
	for raw_n in range(count):
		n = raw_n
		if objs is not None:
			repeat_n = repeater(decode_count, raw_n, count)
			if repeat_n is None:
				break
			n = repeat_n
		json = jsons[n]
		json_type = json.get('_type')
		if not json_type:
			raise PyMSError('Decode', 'Object is missing a type')
		definition = definition_map.get(json_type)
		if definition is None:
			raise PyMSError('Decode', f"Unrecognized object type '{json_type}'")
		obj = builder(definition)
		_apply(json, obj)
		result.append(obj)
	return result
