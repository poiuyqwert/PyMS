
from .DataID import DATID

from ..FileFormats.DAT import *
\
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.Callback import Callback
from ..Utilities import Assets

import copy

class NamesDisplaySetting:
	basic = 'basic'
	tbl = 'tbl'
	combine = 'combine'

	DATANAMES_USAGE_TO_SETTING = None # type: dict[DataNamesUsage, str]
	SETTING_TO_DATANAMES_USAGE = None # type: dict[str, DataNamesUsage]

NamesDisplaySetting.DATANAMES_USAGE_TO_SETTING = {
	DataNamesUsage.use: NamesDisplaySetting.basic,
	DataNamesUsage.ignore: NamesDisplaySetting.tbl,
	DataNamesUsage.combine: NamesDisplaySetting.combine
}
NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE = {
	NamesDisplaySetting.basic: DataNamesUsage.use,
	NamesDisplaySetting.tbl: DataNamesUsage.ignore,
	NamesDisplaySetting.combine: DataNamesUsage.combine
}

class DATData(object):
	def __init__(self, data_context, dat_id, dat_type, data_file, entry_type_name):
		self.data_context = data_context
		self.dat_id = dat_id
		self.dat_type = dat_type
		self.data_file = data_file
		self.entry_type_name = entry_type_name
		self.dat = None
		self.file_path = None
		self.default_dat = None
		self.names = ()
		self.name_overrides = {}

		self.update_cb = Callback()

	def load_defaults(self, mpqhandler):
		try:
			dat = self.dat_type()
			dat.load_file(mpqhandler.get_file('MPQ:arr\\' + self.dat_type.FILE_NAME, MPQHandler.GET_FROM_FOLDER_OR_MPQ))
		except:
			pass
		else:
			self.default_dat = dat
		if self.dat == None:
			self.new_file()
		else:
			self.update_names()

	def new_file(self):
		if self.default_dat:
			self.dat = copy.deepcopy(self.default_dat)
			self.file_path = None
		else:
			self.dat = self.dat_type()
			self.dat.new_file()
		self.update_names()

	def load_file(self, file_path):
		dat = self.dat_type()
		dat.load_file(file_path)
		self.dat = dat
		self.file_path = file_path
		self.update_names()

	def load_data(self, file_data):
		dat = self.dat_type()
		dat.load_data(file_data)
		self.dat = dat
		self.file_path = None

	def save_file(self, file_path):
		self.dat.save_file(file_path)

	def save_data(self):
		return self.dat.save_data()

	def load_name_overrides(self, path, update_names=True):
		with open(path, 'r') as f:
			contents = f.readlines()
		self.name_overrides = DATEntryName.parse_overrides(contents)
		if update_names:
			self.update_names()

	def save_name_overrides(self, path):
		with open(path, 'w') as f:
			for entry_id in sorted(self.name_overrides.keys()):
				f.write('%d%s:%s\n' % (entry_id, '+' if self.name_overrides[entry_id][0] else '', self.name_overrides[entry_id][1]))

	def update_names(self):
		entry_count = self.entry_count()
		names = []
		for entry_id in range(entry_count):
			names.append(DATEntryName.generic(entry_id, type=self.entry_type_name, id_count=entry_count, data_names=Assets.data_cache(self.data_file), name_overrides=self.name_overrides))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

	def entry_name(self, entry_id):
		if entry_id >= len(self.names):
			entry_count = self.entry_count()
			return DATEntryName.generic(entry_id, type=self.entry_type_name, id_count=entry_count, data_names=Assets.data_cache(self.data_file), name_overrides=self.name_overrides)
		return self.names[entry_id]

	def is_expanded(self):
		if self.dat:
			return self.dat.is_expanded()
		if self.default_dat:
			return self.default_dat.is_expanded()
		return False

	def entry_count(self):
		if self.dat:
			return self.dat.entry_count()
		if self.default_dat:
			return self.default_dat.entry_count()
		return self.dat_type.FORMAT.entries

	def expand_entries(self, add):
		expanded = self.dat.expand_entries(add)
		if expanded:
			self.update_names()
		return expanded

class UnitsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.units, UnitsDAT, Assets.DataReference.Units, 'Unit')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.unit(entry_id,
				data_names=Assets.data_cache(self.data_file),
				stat_txt=self.data_context.stat_txt,
				unitnamestbl=self.data_context.unitnamestbl,
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_raw_string=not self.data_context.settings.names[self.dat_id.id].get('simple', False),
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class WeaponsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.weapons, WeaponsDAT, Assets.DataReference.Weapons, 'Weapon')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.weapon(entry_id,
				data_names=Assets.data_cache(self.data_file),
				weaponsdat=self.dat,
				stat_txt=self.data_context.stat_txt,
				none_name='None',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_raw_string=not self.data_context.settings.names[self.dat_id.id].get('simple', False),
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class FlingyDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.flingy, FlingyDAT, Assets.DataReference.Flingy, 'Flingy')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.flingy(entry_id,
				data_names=Assets.data_cache(self.data_file),
				flingydat=self.dat,
				spritesdat=self.data_context.dat_data(DATID.sprites).dat,
				imagesdat=self.data_context.dat_data(DATID.images).dat,
				imagestbl=self.data_context.imagestbl,
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class SpritesDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.sprites, SpritesDAT, Assets.DataReference.Sprites, 'Sprite')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.sprite(entry_id,
				data_names=Assets.data_cache(self.data_file),
				spritesdat=self.dat,
				imagesdat=self.data_context.dat_data(DATID.images).dat,
				imagestbl=self.data_context.imagestbl,
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class ImagesDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.images, ImagesDAT, Assets.DataReference.Images, 'Image')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.image(entry_id,
				data_names=Assets.data_cache(self.data_file),
				imagesdat=self.dat,
				imagestbl=self.data_context.imagestbl,
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class UpgradesDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.upgrades, UpgradesDAT, Assets.DataReference.Upgrades, 'Upgrade')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.upgrade(entry_id,
				data_names=Assets.data_cache(self.data_file),
				upgradesdat=self.dat,
				stat_txt=self.data_context.stat_txt,
				none_name='None',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_raw_string=not self.data_context.settings.names[self.dat_id.id].get('simple', False),
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class TechDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.techdata, TechDAT, Assets.DataReference.Techdata, 'Technology')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.tech(entry_id,
				data_names=Assets.data_cache(self.data_file),
				techdatadat=self.dat,
				stat_txt=self.data_context.stat_txt,
				none_name='None',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_raw_string=not self.data_context.settings.names[self.dat_id.id].get('simple', False),
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class SoundsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.sfxdata, SoundsDAT, Assets.DataReference.Sfxdata, 'Sound')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.sound(entry_id,
				data_names=Assets.data_cache(self.data_file),
				sfxdatadat=self.dat,
				sfxdatatbl=self.data_context.sfxdatatbl,
				none_name='No sound',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class PortraitsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.portdata, PortraitsDAT, Assets.DataReference.Portdata, 'Portrait')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.portrait(entry_id,
				data_names=Assets.data_cache(self.data_file),
				portdatadat=self.dat,
				portdatatbl=self.data_context.portdatatbl,
				none_name='None',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class CampaignDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.mapdata, CampaignDAT, Assets.DataReference.Mapdata, 'Map')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.map(entry_id,
				data_names=Assets.data_cache(self.data_file),
				mapdatadat=self.dat,
				mapdatatbl=self.data_context.mapdatatbl,
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class OrdersDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.orders, OrdersDAT, Assets.DataReference.Orders, 'Order')

	def update_names(self):
		names = []
		entry_count = self.entry_count()
		for entry_id in range(entry_count):
			names.append(DATEntryName.order(entry_id,
				data_names=Assets.data_cache(self.data_file),
				ordersdat=self.dat,
				stat_txt=self.data_context.stat_txt,
				none_name='None',
				data_names_usage=NamesDisplaySetting.SETTING_TO_DATANAMES_USAGE[self.data_context.settings.names[self.dat_id.id].get('display', NamesDisplaySetting.basic)],
				tbl_raw_string=not self.data_context.settings.names[self.dat_id.id].get('simple', False),
				tbl_decompile=False,
				name_overrides=self.name_overrides
			))
		self.names = tuple(names)
		self.update_cb(self.dat_id)
