
from ..FileFormats.Graft import AbstractReqGraft, UnitsGraft, UpgradesGraft, ResearchGraft, TechGraft, OrdersGraft, ButtonsGraft, FGP
from ..FileFormats.Graft.CodeHandlers import GraftLexer, GraftParseContext, GraftSerializeContext

from ..Utilities.DataContext import DataContext
from ..Utilities.PyMSWarning import PyMSWarning
from ..Utilities import IO

from typing import Generic, TypeVar

ReqGraftT = TypeVar('ReqGraftT', bound=AbstractReqGraft)

# An open requirements .graft file (subclassed for units, upgrades, research, tech, and orders)
class ReqGraftData(Generic[ReqGraftT]):
	def __init__(self, graft_type: type[ReqGraftT]) -> None:
		self.graft_type = graft_type
		self.graft = graft_type()
		self.file_path: str | None = None
		self.edited = False

	@property
	def file_name(self) -> str:
		return self.graft_type.FILE_NAME

	@property
	def mpq_path(self) -> str:
		return self.graft_type.MPQ_PATH

	@property
	def display_name(self) -> str:
		return self.file_path or self.file_name

	def new(self) -> None:
		graft = self.graft_type()
		graft.new()
		self.graft = graft
		self.file_path = None
		self.edited = False

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		graft = self.graft_type()
		warnings = graft.load(any_input)
		self.graft = graft
		self.file_path = any_input if isinstance(any_input, str) else None
		self.edited = False
		return warnings

	def save(self, output: IO.AnyOutputBytes) -> None:
		self.graft.save(output)

	def save_bytes(self) -> bytes:
		return IO.output_to_bytes(self.graft.save)

	def export_text(self, output: IO.AnyOutputText, data_context: DataContext | None) -> None:
		with IO.OutputText(output) as f:
			self.graft.decompile(GraftSerializeContext(f, data_context))

	def import_text(self, any_input: IO.AnyInputText, data_context: DataContext | None) -> None:
		# Replaces the scripts of the open file, so it's marked edited but still saves to the same place
		with IO.InputText(any_input) as f:
			code = f.read()
		scripts = self.graft_type.compile(GraftParseContext(GraftLexer(code), data_context, self.graft_type.LANGUAGE()))
		self.graft.replace_scripts(scripts)
		self.edited = True

	def import_fgp(self, fgp: FGP) -> list[PyMSWarning]:
		# Projects don't have to include every file, so only mark edited if it changed
		before = self.save_bytes()
		warnings = self.graft.import_fgp(fgp)
		if self.save_bytes() != before:
			self.edited = True
		return warnings

	def entry_count(self, data_context: DataContext) -> int:
		# The number of entries in the dat file the scripts are for
		raise NotImplementedError(self.__class__.__name__ + '.entry_count()')

	def entry_ids(self, data_context: DataContext) -> list[int]:
		# Every dat entry, plus any scripts for IDs past the end of the dat file
		return sorted(set(range(self.entry_count(data_context))) | set(self.graft.list_ids()))

	def has_script(self, entry_id: int) -> bool:
		return self.graft.get_script(entry_id) is not None

	def entry_name(self, data_context: DataContext, entry_id: int) -> str | None:
		return self.graft_type.entry_name(data_context, entry_id)

class UnitsGraftData(ReqGraftData[UnitsGraft]):
	def __init__(self) -> None:
		super().__init__(UnitsGraft)

	def entry_count(self, data_context: DataContext) -> int:
		return data_context.unit_entry_count

class UpgradesGraftData(ReqGraftData[UpgradesGraft]):
	def __init__(self) -> None:
		super().__init__(UpgradesGraft)

	def entry_count(self, data_context: DataContext) -> int:
		return data_context.upgrade_entry_count

class ResearchGraftData(ReqGraftData[ResearchGraft]):
	def __init__(self) -> None:
		super().__init__(ResearchGraft)

	def entry_count(self, data_context: DataContext) -> int:
		return data_context.tech_entry_count

class TechGraftData(ReqGraftData[TechGraft]):
	def __init__(self) -> None:
		super().__init__(TechGraft)

	def entry_count(self, data_context: DataContext) -> int:
		return data_context.tech_entry_count

class OrdersGraftData(ReqGraftData[OrdersGraft]):
	def __init__(self) -> None:
		super().__init__(OrdersGraft)

	def entry_count(self, data_context: DataContext) -> int:
		return data_context.order_entry_count

# The open Buttons.graft file
class ButtonsGraftData:
	def __init__(self) -> None:
		self.graft = ButtonsGraft()
		self.file_path: str | None = None
		self.edited = False

	@property
	def file_name(self) -> str:
		return ButtonsGraft.FILE_NAME

	@property
	def mpq_path(self) -> str:
		return ButtonsGraft.MPQ_PATH

	@property
	def display_name(self) -> str:
		return self.file_path or self.file_name

	def new(self) -> None:
		graft = ButtonsGraft()
		graft.new()
		self.graft = graft
		self.file_path = None
		self.edited = False

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		graft = ButtonsGraft()
		warnings = graft.load(any_input)
		self.graft = graft
		self.file_path = any_input if isinstance(any_input, str) else None
		self.edited = False
		return warnings

	def save(self, output: IO.AnyOutputBytes) -> None:
		self.graft.save(output)

	def save_bytes(self) -> bytes:
		return IO.output_to_bytes(self.graft.save)

	def export_text(self, output: IO.AnyOutputText, data_context: DataContext | None) -> None:
		with IO.OutputText(output) as f:
			self.graft.decompile(GraftSerializeContext(f, data_context))

	def import_text(self, any_input: IO.AnyInputText, data_context: DataContext | None) -> None:
		# Replaces the contents of the open file, so it's marked edited but still saves to the same place
		with IO.InputText(any_input) as f:
			code = f.read()
		self.graft = ButtonsGraft.compile(GraftParseContext(GraftLexer(code), data_context))
		self.edited = True

	def import_fgp(self, fgp: FGP) -> list[PyMSWarning]:
		# Projects don't have to include every file, so only mark edited if it changed
		before = self.save_bytes()
		warnings = self.graft.import_fgp(fgp)
		if self.save_bytes() != before:
			self.edited = True
		return warnings

AnyGraftData = ReqGraftData | ButtonsGraftData
