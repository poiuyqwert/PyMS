
from ..FileFormats.AIBIN import AIBIN
from ..FileFormats.AIBIN.AICodeHandlers import AISerializeContext, AIParseContext
from ..FileFormats import TBL
from ..FileFormats import DAT

from ..Utilities.UIKit import AnyWindow
from ..Utilities import IO

from typing import Protocol

class MainDelegate(Protocol):
	def get_ai_bin(self) -> AIBIN.AIBIN:
		...

	# TODO: Proper typing
	def get_highlights(self) -> dict[str, dict]:
		...

	def set_highlights(self, highlights: dict[str, dict]) -> None:
		...

	def get_tbl(self) -> TBL.TBL:
		...

	def get_upgrades_dat(self) -> DAT.UpgradesDAT:
		...

	def get_tech_dat(self) -> DAT.TechDAT:
		...

	def save_code(self, code: str, parent: AnyWindow) -> bool:
		...

	def get_export_references(self) -> bool:
		...

	def get_serialize_context(self) -> AISerializeContext:
		...

	def get_parse_context(self, input: IO.AnyInputText) -> AIParseContext:
		...

class ActionDelegate(Protocol):
	def get_ai_bin(self) -> AIBIN.AIBIN:
		...

	def refresh_scripts(self, select_script_ids: list[str] | None = None) -> None:
		...

class TooltipDelegate(Protocol):
	def get_ai_bin(self) -> AIBIN.AIBIN:
		...

	def get_tbl(self) -> TBL.TBL:
		...

	def get_list_entry(self, index: int) -> AIBIN.AIScriptHeader:
		...
