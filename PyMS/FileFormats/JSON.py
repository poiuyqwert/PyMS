
from ..Utilities import IO
from ..Utilities.PyMSError import PyMSError

import json as _json

from typing import TypeAlias, Any, TypeGuard

JSONValue: TypeAlias = 'int | float | str | bool | None | JSONObject | JSONArray'
JSONObject = dict[str, JSONValue]
JSONArray = list[JSONValue]

# def is_json(json: Any, check_keys: bool = False) -> TypeGuard[JSONArray]:
# 	if not isinstance(json, list):
# 		return False
# 	for object in json:
# 		if not isinstance(object, dict):
# 			return False
# 		if check_keys:
# 			for key in object.keys():
# 				if not isinstance(key, str):
# 					return False
# 	return True

def is_json_value(json: Any) -> TypeGuard[JSONValue]:
	return False

def is_json_object(json: Any) -> TypeGuard[JSONObject]:
	return False

def is_json_array(json: Any) -> TypeGuard[JSONArray]:
	return False

def load(input: IO.AnyInputText) -> JSONArray | JSONObject:
	try:
		with IO.InputText(input) as f:
			raw_json = f.read()
	except:
		raise PyMSError('Load', "Couldn't load json")
	try:
		json = _json.loads(raw_json)
	except:
		raise PyMSError('Load', "Couldn't parse json")
	return json

def save(output: IO.AnyOutputText, json: JSONArray | JSONObject) -> None:
	try:
		raw_json = _json.dumps(json)
	except:
		raise PyMSError('Save', "Couldn't save json")
	try:
		with IO.OutputText(output) as f:
			f.write(raw_json)
	except:
		raise PyMSError('Save', "Couldn't open file")
