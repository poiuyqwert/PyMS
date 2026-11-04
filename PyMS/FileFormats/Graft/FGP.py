from __future__ import annotations

from .AbstractReqGraft import AbstractReqGraft
from .UnitsGraft import UnitsGraft
from .UpgradesGraft import UpgradesGraft
from .ResearchGraft import ResearchGraft
from .TechGraft import TechGraft
from .OrdersGraft import OrdersGraft
from .ButtonsGraft import Button, StatInfo

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import Struct
from ...Utilities import IO

from dataclasses import dataclass
from enum import Enum

# FireGraft project (.fgp) files, as saved by FireGraft 1.16.1 (in the `Firegraft\` folder of its MPQ).
# Only the button, unit, and requirement data is read (EXE edits and plugins are not supported).

class _UnitHeader(Struct.Struct):
	unit_id: int
	button_count: int
	button_set: int
	connected_unit: int
	has_stat_info: int

	_fields = (
		('unit_id', Struct.t_u8),
		('button_count', Struct.t_u8),
		('button_set', Struct.t_u8), # 1-based, 0 is no button set
		('connected_unit', Struct.t_u16),
		('has_stat_info', Struct.t_u8),
	)

class _UnitStatInfo(Struct.Struct):
	debug_unit_id: int
	status_function: int
	display_function: int

	_fields = (
		('debug_unit_id', Struct.t_u8),
		('status_function', Struct.t_u8),
		('display_function', Struct.t_u8),
	)

class _NameNode(Struct.Struct):
	entry_id: int
	is_folder: int
	depth: int

	_fields = (
		('entry_id', Struct.t_s32), # -1 for no ID
		('is_folder', Struct.t_u8),
		('depth', Struct.t_u32),
	)

# The chunks of custom names from the FireGraft project
class FGPNames(Enum):
	units = 'SUni'
	technologies = 'SRes'
	upgrades = 'SUpg'
	orders = 'SOrd'
	button_sets = 'SBut'

@dataclass
class FGPUnit:
	unit_id: int
	button_set: int | None
	connected_unit: int
	stat_info: StatInfo | None

class FGP:
	SUPPORTED_VERSION = '1.16.1'

	CHUNK_VERSION = 'FgPa'
	CHUNK_BUTTON_SETS = 'Buts'
	CHUNK_UNITS = 'Unit'
	CHUNK_REQUIREMENTS: dict[type[AbstractReqGraft], str] = {
		UnitsGraft: 'UntR',
		UpgradesGraft: 'UpgR',
		ResearchGraft: 'TecR',
		TechGraft: 'TecU',
		OrdersGraft: 'OrdR',
	}

	def __init__(self) -> None:
		self.button_sets: dict[int, list[Button]] = {}
		self.units: list[FGPUnit] = []
		# Requirement scripts as raw words, `None` for a removed script
		self.requirements: dict[type[AbstractReqGraft], dict[int, list[int] | None]] = {}
		# Custom names from the FireGraft project
		self.names: dict[FGPNames, dict[int, str]] = {}
		self.warnings: list[PyMSWarning] = []

	@staticmethod
	def _chunks(data: bytes) -> dict[str, bytes]:
		chunks: dict[str, bytes] = {}
		scanner = BytesScanner(data)
		while scanner.remaining_len() >= 8:
			tag = scanner.scan_bytes(4).decode('latin-1')
			size = scanner.scan(Struct.l_u32)
			if size > scanner.remaining_len():
				break
			# The first chunk with a tag is used
			chunks.setdefault(tag, scanner.scan_bytes(size))
		return chunks

	def load(self, any_input: IO.AnyInputBytes) -> list[PyMSWarning]:
		with IO.InputBytes(any_input) as f:
			data = f.read()
		try:
			chunks = FGP._chunks(data)
			version_data = chunks.get(FGP.CHUNK_VERSION)
			version = version_data.split(b'\x00', 1)[0].decode('ascii', 'replace') if version_data is not None else None
		except Exception as exc:
			raise PyMSError('Load', 'Unsupported FireGraft project, could possibly be invalid or corrupt') from exc
		if version != FGP.SUPPORTED_VERSION:
			raise PyMSError('Load', f'Unsupported FireGraft project version `{version}` (only FireGraft {FGP.SUPPORTED_VERSION} projects are supported)')
		warnings: list[PyMSWarning] = []
		try:
			button_sets = FGP._load_button_sets(chunks.get(FGP.CHUNK_BUTTON_SETS))
			units = FGP._load_units(chunks.get(FGP.CHUNK_UNITS), warnings)
			requirements: dict[type[AbstractReqGraft], dict[int, list[int] | None]] = {}
			for graft_type, tag in FGP.CHUNK_REQUIREMENTS.items():
				if (chunk := chunks.get(tag)) is not None:
					requirements[graft_type] = FGP._load_requirements(chunk, graft_type, warnings)
			names: dict[FGPNames, dict[int, str]] = {}
			for kind in FGPNames:
				if (chunk := chunks.get(kind.value)) is not None:
					names[kind] = FGP._load_names(chunk)
		except Exception as exc:
			raise PyMSError('Load', 'Unsupported FireGraft project, could possibly be invalid or corrupt') from exc
		self.button_sets = button_sets
		self.units = units
		self.requirements = requirements
		self.names = names
		self.warnings = warnings
		return warnings

	@staticmethod
	def _load_button_sets(chunk: bytes | None) -> dict[int, list[Button]]:
		button_sets: dict[int, list[Button]] = {}
		if chunk is None:
			return button_sets
		scanner = BytesScanner(chunk)
		count = scanner.scan(Struct.l_u16)
		for _ in range(count):
			set_id = scanner.scan(Struct.l_u8)
			button_count = scanner.scan(Struct.l_u8)
			button_sets[set_id] = [scanner.scan(Button) for _ in range(button_count)]
		return button_sets

	@staticmethod
	def _load_units(chunk: bytes | None, warnings: list[PyMSWarning]) -> list[FGPUnit]:
		units: list[FGPUnit] = []
		if chunk is None:
			return units
		scanner = BytesScanner(chunk)
		count = scanner.scan(Struct.l_u16)
		previous_id = 0
		id_offset = 0
		for _ in range(count):
			header = scanner.scan(_UnitHeader)
			stat_info: StatInfo | None = None
			if header.has_stat_info:
				fg_stat_info = scanner.scan(_UnitStatInfo)
				stat_info = StatInfo(fg_stat_info.debug_unit_id, fg_stat_info.status_function, fg_stat_info.display_function)
			# FireGraft only stores the low byte of unit IDs, so units past 255 are detected by the IDs wrapping around
			unit_id = header.unit_id + id_offset
			if unit_id < previous_id:
				if not id_offset:
					warnings.append(PyMSWarning(warn_type='Load', warning='Extended unit IDs detected (FireGraft only stores the low byte of unit IDs), verify the units past 255 are correct'))
				while unit_id < previous_id:
					id_offset += 256
					unit_id += 256
			previous_id = unit_id
			button_set = header.button_set - 1 if header.button_set else None
			units.append(FGPUnit(unit_id, button_set, header.connected_unit, stat_info))
		return units

	@staticmethod
	def _load_requirements(chunk: bytes, graft_type: type[AbstractReqGraft], warnings: list[PyMSWarning]) -> dict[int, list[int] | None]:
		requirements: dict[int, list[int] | None] = {}
		scanner = BytesScanner(chunk)
		count = scanner.scan(Struct.l_u16)
		warned = False
		for _ in range(count):
			entry_id = scanner.scan(Struct.l_u8)
			word_count = scanner.scan(Struct.l_u8)
			words = scanner.scan(Struct.l_au16(word_count)) if word_count else []
			used = scanner.scan(Struct.l_u8)
			# FireGraft only stores the low byte of IDs, so a repeated ID is the same low byte of a later ID
			fg_id = entry_id
			while entry_id in requirements:
				entry_id += 256
			if entry_id != fg_id and not warned:
				warnings.append(PyMSWarning(warn_type='Load', warning=f'Extended IDs detected in the {graft_type.DESCRIPTION.lower()} (FireGraft only stores the low byte of IDs), verify the scripts past 255 are correct'))
				warned = True
			requirements[entry_id] = words if used else None
		return requirements

	@staticmethod
	def _load_names(chunk: bytes) -> dict[int, str]:
		names: dict[int, str] = {}
		scanner = BytesScanner(chunk)
		count = scanner.scan(Struct.l_u32)
		for _ in range(count):
			node = scanner.scan(_NameNode)
			name = scanner.scan_cstr('latin-1')
			if node.entry_id != -1 and not node.is_folder:
				names[node.entry_id] = name
		return names
