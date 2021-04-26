
from ..FileFormats.DAT import *

from ..Utilities.utils import isstr
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.DataCache import DATA_CACHE

import copy

class DATData(object):
	def __init__(self, data_context, dat_type, data_file, entry_type_name):
		self.data_context = data_context
		self.dat_type = dat_type
		self.data_file = data_file
		self.entry_type_name = entry_type_name
		self.dat = None
		self.file_path = None
		self.default_dat = None
		self.names = ()
		self.name_overrides = {}

	def load_defaults(self, mpqhandler):
		update_names = False
		try:
			dat = self.dat_type()
			dat.load_file(mpqhandler.get_file('MPQ:arr\\' + self.dat_type.FILE_NAME, MPQHandler.GET_FROM_FOLDER_OR_MPQ))
			update_names = True
		except:
			pass
		else:
			self.default_dat = dat
		if self.dat == None:
			self.new_file()
			update_names = True
		if update_names:
			self.update_names()

	def new_file(self):
		if self.default_dat:
			self.dat = copy.deepcopy(self.default_dat)
			self.file_path = None
			self.update_names()
		else:
			self.dat = self.dat_type()
			self.dat.new_file()

	def load_file(self, file_info):
		if isstr(file_info):
			dat = self.dat_type()
			dat.load_file(file_info)
			self.dat = dat
			self.file_path = file_info
		# TODO: Handle open from folder/mpq
		else:
			raise Exception()
		self.update_names()

	def load_name_overrides(self, path):
		pass

	def update_names(self):
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		names = []
		for entry_id in range(entry_count):
			if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
				names.append(self.reserved_name(entry_id))
			elif entry_id in self.name_overrides:
				names.append(self.name_overrides[entry_id])
			elif entry_id >= len(DATA_CACHE[self.data_file]):
				names.append(self.unknown_name(entry_id))
			else:
				names.append(DATA_CACHE[self.data_file][entry_id])
		self.names = tuple(names)

	def reserved_name(self, entry_id):
		return "Reserved %s #%s" % (self.entry_type_name, entry_id)

	def unknown_name(self, entry_id=None):
		name = self.entry_type_name
		if entry_id != None:
			name += " #%s" % entry_id
		return name

	def entry_name(self, entry_id):
		if entry_id >= len(self.names):
			return self.unknown_name(entry_id)
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

class UnitsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, UnitsDAT, 'Units.txt', 'Unit')

	def update_names(self):
		names = []
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		strings = self.data_context.unitnamestbl.strings or self.data_context.stat_txt.strings[:228]
		for entry_id in range(entry_count):
			if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
				names.append(self.reserved_name(entry_id))
			elif entry_id in self.name_overrides:
				names.append(self.name_overrides[entry_id])
			elif strings and self.data_context.settings.settings.get('customlabels'):
				if entry_id >= len(strings):
					names.append(self.unknown_name(entry_id))
				else:
					names.append(strings[entry_id])
			else:
				if entry_id >= len(DATA_CACHE[self.data_file]):
					names.append(self.unknown_name(entry_id))
				else:
					names.append(DATA_CACHE[self.data_file][entry_id])
		self.names = tuple(names)

class EntryLabelDATData(DATData):
	def __init__(self, data_context, dat_type, data_file, entry_type_name, label_offset=1):
		self.label_offset = label_offset
		DATData.__init__(self, data_context, dat_type, data_file, entry_type_name)

	def update_names(self):
		names = []
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		strings = self.data_context.stat_txt.strings
		for entry_id in range(entry_count):
			if entry_id in self.name_overrides:
				names.append(self.name_overrides[entry_id])
			elif strings and self.data_context.settings.settings.get('customlabels'):
				if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
					names.append(self.reserved_name(entry_id))
				elif not dat:
					names.append(self.unknown_name())
				else:
					label_id = dat.get_entry(entry_id).label - self.label_offset
					if label_id < 0:
						names.append('None')
					elif label_id >= len(strings):
						names.append(self.unknown_name(entry_id))
					else:
						names.append(strings[label_id])
			else:
				if entry_id >= len(DATA_CACHE[self.data_file]):
					names.append(self.unknown_name(entry_id))
				else:
					names.append(DATA_CACHE[self.data_file][entry_id])
		self.names = tuple(names)
