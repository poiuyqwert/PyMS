
from ..Utilities import IO
from ..Utilities.PyMSError import PyMSError
from ..Utilities import JSON

import json as _json

def load(inp: IO.AnyInputText) -> JSON.Array | JSON.Object:
	try:
		with IO.InputText(inp) as f:
			raw_json = f.read()
	except Exception as exc:
		raise PyMSError('Load', "Couldn't load json") from exc
	try:
		json = _json.loads(raw_json)
	except Exception as exc:
		raise PyMSError('Load', "Couldn't parse json") from exc
	return json

def save(output: IO.AnyOutputText, json: JSON.Array | JSON.Object) -> None:
	try:
		raw_json = _json.dumps(json)
	except Exception as exc:
		raise PyMSError('Save', "Couldn't save json") from exc
	try:
		with IO.OutputText(output) as f:
			f.write(raw_json)
	except Exception as exc:
		raise PyMSError('Save', "Couldn't open file") from exc
