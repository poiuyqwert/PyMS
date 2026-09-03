from .ExtractorDialog import ExtractorDialog
from .DefaultExtractorDialog import DefaultExtractorDialog

from .DestinationView import DestinationView
from .MPQConfigView import MPQConfigView

from typing import Type as _Type

# Format specific extractors (AIScript, GRP, ...) get registered here. `DefaultExtractorDialog` is
# deliberately absent: it is the fallback, not a candidate
EXTRACTOR_TYPES: list[_Type[ExtractorDialog]] = [
]

# Highest confidence wins, and the comparison is strict so registration order breaks ties (the same
# rule `Project.update_source_graph` uses to pick a `Source` type)
def find_extractor(mpq_file_name: str) -> _Type[ExtractorDialog]:
	detected_extractor_type: _Type[ExtractorDialog] = DefaultExtractorDialog
	detected_extractor_confidence: float = 0
	for extractor_type in EXTRACTOR_TYPES:
		confidence = extractor_type.matches(mpq_file_name)
		if confidence > detected_extractor_confidence:
			detected_extractor_type = extractor_type
			detected_extractor_confidence = confidence
	return detected_extractor_type
