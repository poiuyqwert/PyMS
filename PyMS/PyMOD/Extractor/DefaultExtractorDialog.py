
from __future__ import annotations

from .ExtractorDialog import ExtractorDialog

from ...Utilities import Assets
from ...Utilities import JSON
from ...Utilities.PyMSError import PyMSError

import os

# The fallback used for any file no registered extractor claims: copy the file out of the MPQ as
# is, with nothing but the shared MPQ config to configure
class DefaultExtractorDialog(ExtractorDialog):
	# Never registered in `EXTRACTOR_TYPES`, `find_extractor` falls back to it directly
	@classmethod
	def matches(cls, mpq_file_name: str) -> float:
		return 0

	def perform_extract(self, destination_path: str) -> JSON.Object:
		# The `MPQ:` prefix is what lets `MPQHandler` fall back to the game files bundled with PyMS
		# when none of the configured MPQs have the file
		file_ref = Assets.mpq_file_ref(self.mpq_file_name)
		with self.mpqhandler.load_file(file_ref) as file:
			data = file.read()
		destination_folder = os.path.dirname(destination_path)
		try:
			if destination_folder:
				os.makedirs(destination_folder, exist_ok=True)
			with open(destination_path, 'wb') as destination_file:
				destination_file.write(data)
		except Exception as e:
			raise PyMSError('Extract', f"Couldn't write `{destination_path}`", cause=e) from e
		return {}
