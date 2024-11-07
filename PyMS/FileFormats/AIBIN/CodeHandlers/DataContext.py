
from ...TBL import TBL, decompile_string, compile_string
from ...DAT import UnitsDAT, UpgradesDAT, TechDAT

# TODO: Use DatEntryName?

class DataContext(object):
	def __init__(self, stattxt_tbl: TBL | None = None, unitnames_tbl: TBL | None = None, units_dat: UnitsDAT | None = None, upgrades_dat: UpgradesDAT | None = None, techdata_dat: TechDAT | None = None) -> None:
		self.stattxt_tbl = stattxt_tbl
		self.unitnames_tbl = unitnames_tbl
		self.units_dat = units_dat
		self._unit_names: list[str] | None = None
		self.upgrades_dat = upgrades_dat
		self._upgrade_names: list[str | None] | None = None
		self.techdata_dat = techdata_dat
		self._technology_names: list[str | None] | None = None

	def set_stattxt_tbl(self, stattxt_tbl: TBL | None) -> None:
		self.stattxt_tbl = stattxt_tbl
		self._unit_names = None

	def stattxt_string(self, string_id: int) -> str | None:
		if not self.stattxt_tbl:
			return None
		if string_id >= len(self.stattxt_tbl.strings):
			return None
		return decompile_string(self.stattxt_tbl.strings[string_id][:-1])

	def stattxt_strings(self) -> list[str] | None:
		if not self.stattxt_tbl:
			return None
		return [decompile_string(string[:-1]) for string in self.stattxt_tbl.strings]

	def stattxt_id(self, string: str) -> int | None:
		if not self.stattxt_tbl:
			return None
		string = compile_string(string)
		if not string.endswith('\x00'):
			string += '\x00'
		try:
			return self.stattxt_tbl.strings.index(string)
		except:
			return None

	def set_unitnames_tbl(self, unitnames_tbl: TBL | None) -> None:
		self.unitnames_tbl = unitnames_tbl
		self._unit_names = None

	def set_units_dat(self, units_dat: UnitsDAT | None) -> None:
		self.units_dat = units_dat

	def _unit_name(self, raw_string: str) -> str:
		name = raw_string
		components = raw_string.split('\x00')
		if len(components) > 1 and components[1] != '*':
			name = '\x00'.join(components[:2])
		else:
			name = components[0]
		return decompile_string(name, exclude='\x0A\x28\x29\x2C').strip()

	def _get_unit_names(self) -> (list[str] | None):
		if self._unit_names:
			return self._unit_names
		strings = None
		if self.unitnames_tbl:
			strings = self.unitnames_tbl.strings
		elif self.stattxt_tbl:
			strings = self.stattxt_tbl.strings[:UnitsDAT.FORMAT.entries]
		if not strings:
			return None
		self._unit_names = []
		for raw_string in strings:
			self._unit_names.append(self._unit_name(raw_string))
		return self._unit_names

	def unit_name(self, unit_id: int) -> (str | None):
		unit_names = self._get_unit_names()
		if not unit_names:
			return None
		if unit_id >= len(unit_names):
			return None
		return unit_names[unit_id]

	def unit_id(self, unit_name: str) -> (int | None):
		unit_names = self._get_unit_names()
		if not unit_names:
			return None
		try:
			return unit_names.index(unit_name)
		except:
			return None

	def set_upgrades_dat(self, upgrades_dat: UpgradesDAT | None) -> None:
		self.upgrades_dat = upgrades_dat
		self._upgrade_names = None

	def _upgrade_name(self, raw_string: str) -> str:
		return decompile_string(raw_string.split('\x00')[0], exclude='\x0A\x28\x29\x2C').strip()

	def _get_upgrade_names(self) -> (list[str | None] | None):
		if self._upgrade_names:
			return self._upgrade_names
		if not self.upgrades_dat:
			return None
		if not self.stattxt_tbl:
			return None
		self._upgrade_names = []
		for upgrade_id in range(0, self.upgrades_dat.entry_count()):
			string_id = self.upgrades_dat.get_entry(upgrade_id).label - 1
			if string_id < 0 or string_id >= len(self.stattxt_tbl.strings):
				self._upgrade_names.append(None)
			else:
				self._upgrade_names.append(self._upgrade_name(self.stattxt_tbl.strings[string_id]))
		return self._upgrade_names

	def upgrade_name(self, upgrade_id: int) -> (str | None):
		upgrade_names = self._get_upgrade_names()
		if not upgrade_names:
			return None
		if upgrade_id >= len(upgrade_names):
			return None
		return upgrade_names[upgrade_id]

	def upgrade_id(self, upgrade_name: str) -> (int | None):
		upgrade_names = self._get_upgrade_names()
		if not upgrade_names:
			return None
		try:
			return upgrade_names.index(upgrade_name)
		except:
			return None

	def set_techdata_dat(self, techdata_dat: TechDAT | None) -> None:
		self.techdata_dat = techdata_dat
		self._technology_names = None

	def _technology_name(self, raw_string: str) -> str:
		return decompile_string(raw_string.split('\x00')[0], exclude='\x0A\x28\x29\x2C').strip()

	def _get_technology_names(self) -> (list[str | None] | None):
		if self._technology_names:
			return self._technology_names
		if not self.techdata_dat:
			return None
		if not self.stattxt_tbl:
			return None
		self._technology_names = []
		for technology_id in range(0, self.techdata_dat.entry_count()):
			string_id = self.techdata_dat.get_entry(technology_id).label - 1
			if string_id < 0 or string_id >= len(self.stattxt_tbl.strings):
				self._technology_names.append(None)
			else:
				self._technology_names.append(self._technology_name(self.stattxt_tbl.strings[string_id]))
		return self._technology_names

	def technology_name(self, technology_id: int) -> (str | None):
		technology_names = self._get_technology_names()
		if not technology_names:
			return None
		if technology_id >= len(technology_names):
			return None
		return technology_names[technology_id]

	def technology_id(self, technology_name: str) -> (int | None):
		technology_names = self._get_technology_names()
		if not technology_names:
			return None
		try:
			return technology_names.index(technology_name)
		except:
			return None
