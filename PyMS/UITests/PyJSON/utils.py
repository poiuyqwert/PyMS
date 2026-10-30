
from ..harness import UITestCase

from ...PyJSON.PyJSON import PyJSON

import json
from unittest import mock

from typing import Any

# PyJSON is a work in progress: its `__init__` reads a hardcoded JSON file with the
# builtin `open`. Shadow `open` in the PyJSON module's globals (lookups check module
# globals before builtins) so construction reads this in-memory document instead of
# touching disk. The window's own `open` method is an attribute, so it is unaffected.
OBJECTS = [
	{'id': 'first', 'value': 1},
	{'id': 'second', 'value': 2},
]

LOADER = 'PyMS.PyJSON.PyJSON.open'

class PyJSONTestCase(UITestCase):
	def open_pyjson(self, extra_patches: dict[str, dict[str, Any]] | None = None) -> PyJSON:
		patches: dict[str, dict[str, Any]] = {
			LOADER: {'new': mock.mock_open(read_data=json.dumps(OBJECTS)), 'create': True},
		}
		return self.make_window(PyJSON, extra_patches={**patches, **(extra_patches or {})})
