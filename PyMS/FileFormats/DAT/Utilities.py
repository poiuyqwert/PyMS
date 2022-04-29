
from UnitsDAT import UnitsDAT
from WeaponsDAT import WeaponsDAT
from ImagesDAT import ImagesDAT
from SpritesDAT import SpritesDAT
from FlingyDAT import FlingyDAT

from ..TBL import TBL, decompile_string

from ...Utilities.PyMSError import PyMSError

import re


class DataNamesUsage:
	use = None # type: DataNamesUsage
	"""Use Data Name if available, never use TBL Name"""
	ignore = None # type: DataNamesUsage
	"""Ignore Data Name, use TBL Name if available"""
	combine = None # type: DataNamesUsage
	"""Combine the Data Name with the TBL Name:
	
	Data Name (TBL Name)"""

	def __init__(self, value):
		self.value = value

	def __eq__(self, other):
		return isinstance(other, DataNamesUsage) and other.value == self.value
DataNamesUsage.use = DataNamesUsage('use')
DataNamesUsage.ignore = DataNamesUsage('ignore')
DataNamesUsage.combine = DataNamesUsage('combine')

class DATEntryName:
	RE_NAME_OVERRIDE = re.compile(r'\s*(\d{1,5})\s*(\+?)\s*:(.*)')
	RE_TBL_CODES = re.compile(r'[\x00-\x1F]')
	RE_HOTKEY = re.compile(r'^.[\x00-\x05]')

	@staticmethod
	def parse_overrides(overrides): # type: (list[str]) -> dict[int, tuple[bool, str]]
		try:
			name_overrides = {}
			for line in overrides:
				m = DATEntryName.RE_NAME_OVERRIDE.match(line)
				if not m:
					raise PyMSError('Open', "Invalid name override '%s'" % line)
				entry_id = int(m.group(1))
				append = (m.group(2) == '+')
				name = m.group(3)
				name_overrides[entry_id] = (append, name)
		except PyMSError:
			raise
		except:
			raise PyMSError('Open', "Invalid name overrides")

	@staticmethod
	def _build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, id_count, type): # type: (int, str, str, str, DataNamesUsage, int, str) -> str
		default_name = '%s #%d' % (type, entry_id)
		if entry_id >= id_count:
			default_name = 'Expanded ' + default_name
		name = None
		if data_names_usage == DataNamesUsage.combine and tbl_name:
			if data_name == None:
				data_name = default_name
			name = '%s (%s)' % (data_name, tbl_name)
		elif data_names_usage != DataNamesUsage.ignore and data_name:
			name = data_name
		elif data_names_usage != DataNamesUsage.use and tbl_name:
			name = tbl_name
		if not name:
			name = default_name
		if override_name:
			name += ' ' + override_name
		return name

	@staticmethod
	def unit(entry_id, data_names=None, stat_txt=None, unitnamestbl=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, name_overrides=None): # type: (int, list[str], TBL, TBL, DataNamesUsage, bool, dict[int, tuple[bool, str]]) -> str
		if UnitsDAT.FORMAT.expanded_entries_reserved and entry_id in UnitsDAT.FORMAT.expanded_entries_reserved:
			return 'Reserved Unit #%d' % entry_id
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if (stat_txt or unitnamestbl) and data_names_usage != DataNamesUsage.use:
			strings = unitnamestbl.strings if unitnamestbl else stat_txt.strings[:228]
			if entry_id < len(strings):
				tbl_name = strings[entry_id][:-1]
				if tbl_raw_string:
					tbl_name = decompile_string(tbl_name)
				else:
					tbl_name, group, _ = tbl_name.split('\x00')
					tbl_name = DATEntryName.RE_TBL_CODES.sub('', tbl_name)
					if group and group != '*':
						tbl_name += ' (%s)' % DATEntryName.RE_TBL_CODES.sub('', group)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, UnitsDAT.FORMAT.entries, 'Unit')

	@staticmethod
	def weapon(entry_id, data_names=None, weaponsdat=None, stat_txt=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, name_overrides=None): # type: (int, list[str], WeaponsDAT, TBL, DataNamesUsage, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if weaponsdat and stat_txt and data_names_usage != DataNamesUsage.use and entry_id < weaponsdat.entry_count():
			label_id = weaponsdat.get_entry(entry_id).label - 1
			if label_id < len(stat_txt.strings):
				tbl_name = stat_txt.strings[label_id][:-1]
				if tbl_raw_string:
					tbl_name = decompile_string(tbl_name)
				else:
					tbl_name = DATEntryName.RE_HOTKEY.sub('', tbl_name)
					tbl_name = DATEntryName.RE_TBL_CODES.sub('', tbl_name)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, WeaponsDAT.FORMAT.entries, 'Weapon')

	@staticmethod
	def grp_image(entry_id, imagesdat, imagestbl): # type: (int, ImagesDAT, TBL) -> str
		if entry_id >= imagesdat.entry_count():
			return None
		tbl_id = imagesdat.get_entry(entry_id).grp_file-1
		if tbl_id >= len(imagestbl.strings):
			return None
		return decompile_string(imagestbl.strings[tbl_id][:-1])

	@staticmethod
	def image(entry_id, data_names=None, imagesdat=None, imagestbl=None, data_names_usage=DataNamesUsage.combine, name_overrides=None): # type: (int, list[str], ImagesDAT, TBL, DataNamesUsage, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if imagesdat and imagestbl and data_names_usage != DataNamesUsage.use:
			tbl_name = DATEntryName.grp_image(entry_id, imagesdat, imagestbl)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, ImagesDAT.FORMAT.entries, 'Image')

	@staticmethod
	def grp_sprite(entry_id, spritesdat, imagesdat, imagestbl): # type: (int, SpritesDAT, ImagesDAT, TBL) -> str
		if entry_id >= spritesdat.entry_count():
			return None
		return DATEntryName.grp_image(spritesdat.get_entry(entry_id).image, imagesdat, imagestbl)

	@staticmethod
	def sprite(entry_id, data_names=None, spritesdat=None, imagesdat=None, imagestbl=None, data_names_usage=DataNamesUsage.combine, name_overrides=None): # type: (int, list[str], SpritesDAT, ImagesDAT, TBL, DataNamesUsage, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if spritesdat and imagesdat and imagestbl and data_names_usage != DataNamesUsage.use:
			tbl_name = DATEntryName.grp_sprite(entry_id, spritesdat, imagesdat, imagestbl)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, SpritesDAT.FORMAT.entries, 'Sprite')

	@staticmethod
	def grp_flingy(entry_id, flingydat, spritesdat, imagesdat, imagestbl): # type: (int, FlingyDAT, SpritesDAT, ImagesDAT, TBL) -> str
		if entry_id > flingydat.entry_count():
			return None
		return DATEntryName.grp_sprite(flingydat.get_entry(entry_id).sprite, spritesdat, imagesdat, imagestbl)

	@staticmethod
	def flingy(entry_id, data_names=None, flingydat=None, spritesdat=None, imagesdat=None, imagestbl=None, data_names_usage=DataNamesUsage.combine, name_overrides=None): # type: (int, list[str], FlingyDAT, SpritesDAT, ImagesDAT, TBL, DataNamesUsage, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if flingydat and spritesdat and imagesdat and imagestbl and data_names_usage != DataNamesUsage.use:
			tbl_name = DATEntryName.grp_flingy(entry_id, flingydat, spritesdat, imagesdat, imagestbl)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, FlingyDAT.FORMAT.entries, 'Flingy')
