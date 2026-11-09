
from __future__ import annotations

from . import IO
from . import JSON
from .PyMSError import PyMSError

import json

from typing import Sequence, TYPE_CHECKING
if TYPE_CHECKING:
	from .UIKit import HighlightComponent

class SyntaxHighlightingFile:
	VERSION = 1

	def __init__(self) -> None:
		# Raw styles keyed by `HighlightComponent.key`, so styles for other programs survive a merge
		self.highlights: dict[str, JSON.Value] = {}

	def load(self, any_input: IO.AnyInputText) -> None:
		try:
			with IO.InputText(any_input) as f:
				data = json.load(f)
		except Exception as exc:
			raise PyMSError('Load', 'Syntax highlighting file is not valid JSON') from exc
		if not JSON.is_json_object(data):
			raise PyMSError('Load', 'Syntax highlighting file must contain a JSON object')
		version = data.get('version')
		if not isinstance(version, int) or isinstance(version, bool):
			raise PyMSError('Load', 'Syntax highlighting file is missing a valid `version`')
		if version > SyntaxHighlightingFile.VERSION:
			raise PyMSError('Load', f'Syntax highlighting file version {version} is newer than the supported version {SyntaxHighlightingFile.VERSION}')
		highlights = data.get('highlights')
		if not JSON.is_json_object(highlights):
			raise PyMSError('Load', 'Syntax highlighting file is missing the `highlights` object')
		self.highlights = dict(highlights)

	def save(self, output: IO.AnyOutputText) -> None:
		data: JSON.Object = {
			'version': SyntaxHighlightingFile.VERSION,
			'highlights': self.highlights
		}
		with IO.OutputText(output) as f:
			json.dump(data, f, sort_keys=True, indent=4)

	def apply(self, highlight_components: Sequence[HighlightComponent]) -> int:
		'''Decode the styles for `highlight_components` that are in this file, returning how many were applied'''
		applied: set[str] = set()
		for highlight_component in highlight_components:
			if highlight_component.key not in self.highlights:
				continue
			highlight_component.highlight_style.decode(self.highlights[highlight_component.key])
			applied.add(highlight_component.key)
		return len(applied)

	def update(self, highlight_components: Sequence[HighlightComponent]) -> None:
		'''Store the styles of `highlight_components`, keeping any other styles already in this file'''
		for highlight_component in highlight_components:
			self.highlights[highlight_component.key] = highlight_component.highlight_style.encode()
