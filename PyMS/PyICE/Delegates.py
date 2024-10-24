
from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, IO as BuiltinIO
if TYPE_CHECKING:
	from .CodeGenerators.GeneratorPreset import GeneratorPreset
	from .CodeGenerators.CodeGeneratorVariable import CodeGeneratorVariable

	from ..FileFormats import DAT
	from ..FileFormats.IScriptBIN import IScriptBIN
	from ..FileFormats.IScriptBIN.CodeHandlers import ICESerializeContext, ICEParseContext, DataContext

	from ..Utilities import IO
	from ..Utilities.MPQHandler import MPQHandler
	from ..Utilities.UIKit import ScrolledListbox, Toplevel, Misc, AnyWindow

class MainDelegate(Protocol):
	unitsdat: DAT.UnitsDAT # TODO: units.dat?

	mpqhandler: MPQHandler

	iscriptlist: ScrolledListbox
	imageslist: ScrolledListbox
	spriteslist: ScrolledListbox
	flingylist: ScrolledListbox
	unitlist: ScrolledListbox

	def get_iscript_bin(self) -> IScriptBIN.IScriptBIN:
		...

	def get_data_context(self) -> DataContext:
		...

	def get_serialize_context(self, output: BuiltinIO[str]) -> ICESerializeContext:
		...

	def get_parse_context(self, input: IO.AnyInputText) -> ICEParseContext:
		...

	def save_code(self, code: str, parent: AnyWindow) -> bool:
		...

class CodeGeneratorDelegate(Protocol):
	def insert_code(self, code: str) -> None:
		pass

class ManagePresetsDelegate(Protocol):
	def load_preset(self, preset: GeneratorPreset, window: Toplevel | None) -> bool:
		...

class VariableEditorDelegate(Protocol):
	def unique_name(self, name: str, ignore: CodeGeneratorVariable | None = None) -> str:
		...

	def update_list(self, select: int | None = None) -> None:
		...

class ImportListDelegate(Protocol):
	imports: list[str]

	def iimport(self, files: str | list[str] | None = None, parent: Misc | None = None) -> None:
		...
