
from .UnitsDAT import UnitsDAT
from .WeaponsDAT import WeaponsDAT
from .ImagesDAT import ImagesDAT
from .SpritesDAT import SpritesDAT
from .FlingyDAT import FlingyDAT
from .UpgradesDAT import UpgradesDAT
from .TechDAT import TechDAT
from .SoundsDAT import SoundsDAT
from .OrdersDAT import OrdersDAT
from .CampaignDAT import CampaignDAT
from .PortraitsDAT import PortraitsDAT

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

	def __hash__(self):
		return hash(self.value)
DataNamesUsage.use = DataNamesUsage('use')
DataNamesUsage.ignore = DataNamesUsage('ignore')
DataNamesUsage.combine = DataNamesUsage('combine')

class DATEntryName:
	RE_NAME_OVERRIDE = re.compile(r'\s*(\d{1,5})\s*(\+?)\s*:(.*)')
	RE_TBL_CODES = re.compile(r'<\d+>')
	RE_HOTKEY = re.compile(r'^.<0*[0-5]>')
	RE_STR_END = re.compile(r'(?:<0>|\x00)$')

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
		return name_overrides

	@staticmethod
	def _build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, id_count, type): # type: (int, str, str, str, DataNamesUsage, int, str) -> str
		default_name = '%s #%d' % (type, entry_id)
		if entry_id >= id_count:
			default_name = 'Expanded ' + default_name
		name = None
		if data_names_usage == DataNamesUsage.combine and tbl_name:
			if data_name == None:
				data_name = default_name
			if data_name == tbl_name:
				name = data_name
			else:
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
	def generic(entry_id, type, id_count, data_names=None, name_overrides=None): # type: (int, str, int, list[str], dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		if data_names and entry_id < len(data_names):
			data_name = data_names[entry_id]
		return DATEntryName._build_name(entry_id, data_name, None, override_name, DataNamesUsage.use, id_count, type)

	@staticmethod
	def unit(entry_id, data_names=None, stat_txt=None, unitnamestbl=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, tbl_decompile=True, name_overrides=None): # type: (int, list[str], TBL, TBL, DataNamesUsage, bool, bool, dict[int, tuple[bool, str]]) -> str
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
				tbl_name = strings[entry_id] # type: str
				if tbl_decompile:
					tbl_name = decompile_string(tbl_name[:-1])
				else:
					tbl_name = tbl_name.rstrip('<0>')
				if not tbl_raw_string:
					pieces = tbl_name.split('<0>')
					tbl_name = ''
					special = '*'
					if pieces:
						tbl_name = pieces[0]
					if len(pieces) > 1:
						special = pieces[1]
					tbl_name = DATEntryName.RE_TBL_CODES.sub('', tbl_name)
					if special and special != '*':
						tbl_name += ' (%s)' % DATEntryName.RE_TBL_CODES.sub('', special)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, UnitsDAT.FORMAT.entries, 'Unit')

	@staticmethod
	def _entry_label(label_id, stat_txt, none_name, tbl_raw_string, tbl_decompile, offset=1): # type: (int, TBL, str | None, bool, bool, int) -> (str | None)
		if offset:
			if label_id < offset:
				return none_name
			label_id -= offset
		if label_id >= len(stat_txt.strings):
			return None
		tbl_name = DATEntryName.RE_STR_END.sub('', stat_txt.strings[label_id])
		if tbl_decompile:
			tbl_name = decompile_string(tbl_name)
		if not tbl_raw_string:
			tbl_name = DATEntryName.RE_HOTKEY.sub('', tbl_name)
			tbl_name = DATEntryName.RE_TBL_CODES.sub('', tbl_name)
		return tbl_name

	@staticmethod
	def weapon(entry_id, data_names=None, weaponsdat=None, stat_txt=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, tbl_decompile=True, name_overrides=None): # type: (int, list[str], WeaponsDAT, TBL, str, DataNamesUsage, bool, bool, dict[int, tuple[bool, str]]) -> str
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
			tbl_name = DATEntryName._entry_label(weaponsdat.get_entry(entry_id).label, stat_txt, none_name, tbl_raw_string, tbl_decompile)
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

	@staticmethod
	def upgrade(entry_id, data_names=None, upgradesdat=None, stat_txt=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, tbl_decompile=True, name_overrides=None): # type: (int, list[str], UpgradesDAT, TBL, str, DataNamesUsage, bool, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if upgradesdat and stat_txt and data_names_usage != DataNamesUsage.use and entry_id < upgradesdat.entry_count():
			tbl_name = DATEntryName._entry_label(upgradesdat.get_entry(entry_id).label, stat_txt, none_name, tbl_raw_string, tbl_decompile)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, UpgradesDAT.FORMAT.entries, 'Upgrade')

	@staticmethod
	def tech(entry_id, data_names=None, techdatadat=None, stat_txt=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, tbl_decompile=True, name_overrides=None): # type: (int, list[str], TechDAT, TBL, str, DataNamesUsage, bool, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if techdatadat and stat_txt and data_names_usage != DataNamesUsage.use and entry_id < techdatadat.entry_count():
			tbl_name = DATEntryName._entry_label(techdatadat.get_entry(entry_id).label, stat_txt, none_name, tbl_raw_string, tbl_decompile)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, TechDAT.FORMAT.entries, 'Tech')

	@staticmethod
	def sound(entry_id, data_names=None, sfxdatadat=None, sfxdatatbl=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_decompile=True, name_overrides=None): # type: (int, list[str], SoundsDAT, TBL, str, DataNamesUsage, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if sfxdatadat and sfxdatatbl and data_names_usage != DataNamesUsage.use and entry_id < sfxdatadat.entry_count():
			tbl_name = DATEntryName._entry_label(sfxdatadat.get_entry(entry_id).sound_file, sfxdatatbl, none_name, True, tbl_decompile)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, SoundsDAT.FORMAT.entries, 'Sound')

	@staticmethod
	def portrait(entry_id, data_names=None, portdatadat=None, portdatatbl=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_decompile=True, name_overrides=None): # type: (int, list[str], PortraitsDAT, TBL, str, DataNamesUsage, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if portdatadat and portdatatbl and data_names_usage != DataNamesUsage.use and entry_id < portdatadat.entry_count():
			tbl_name = DATEntryName._entry_label(portdatadat.get_entry(entry_id).idle.portrait_file, portdatatbl, none_name, True, tbl_decompile, offset=0)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, PortraitsDAT.FORMAT.entries, 'Portrait')

	@staticmethod
	def map(entry_id, data_names=None, mapdatadat=None, mapdatatbl=None, data_names_usage=DataNamesUsage.use, tbl_decompile=True, name_overrides=None): # type: (int, list[str], CampaignDAT, TBL, DataNamesUsage, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if mapdatadat and mapdatatbl and data_names_usage != DataNamesUsage.use and entry_id < mapdatadat.entry_count():
			tbl_name = DATEntryName._entry_label(mapdatadat.get_entry(entry_id).map_file, mapdatatbl, None, True, tbl_decompile, offset=0)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, CampaignDAT.FORMAT.entries, 'Map')

	@staticmethod
	def order(entry_id, data_names=None, ordersdat=None, stat_txt=None, none_name=None, data_names_usage=DataNamesUsage.use, tbl_raw_string=True, tbl_decompile=True, name_overrides=None): # type: (int, list[str], OrdersDAT, TBL, str, DataNamesUsage, bool, bool, dict[int, tuple[bool, str]]) -> str
		override_append, override_name = None, None
		if name_overrides and entry_id in name_overrides:
			override_append, override_name = name_overrides[entry_id]
			if not override_append:
				return override_name
		data_name = None
		tbl_name = None
		if data_names and data_names_usage != DataNamesUsage.ignore and entry_id < len(data_names):
			data_name = data_names[entry_id]
		if ordersdat and stat_txt and data_names_usage != DataNamesUsage.use and entry_id < ordersdat.entry_count():
			tbl_name = DATEntryName._entry_label(ordersdat.get_entry(entry_id).label, stat_txt, none_name, tbl_raw_string, tbl_decompile)
		return DATEntryName._build_name(entry_id, data_name, tbl_name, override_name, data_names_usage, OrdersDAT.FORMAT.entries, 'Order')
