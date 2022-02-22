
from DataID import DATID

from ..FileFormats.DAT import *

from ..Utilities.utils import isstr
from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.DataCache import DATA_CACHE
from ..Utilities.Callback import Callback

import copy

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

	def load_file(self, file_info):
		dat = self.dat_type()
		dat.load_file(file_info)
		self.dat = dat
		self.file_path = file_info
		self.update_names()

	def load_data(self, file_data):
		dat = self.dat_type()
		dat.load_data(file_data)
		self.dat = dat
		self.file_path = None

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
			else:
				name = ''
				if entry_id >= len(DATA_CACHE[self.data_file]):
					name = self.unknown_name(entry_id)
				else:
					name = DATA_CACHE[self.data_file][entry_id]
				if entry_id in self.name_overrides:
					append, override = self.name_overrides[entry_id]
					if append:
						name += " " + override
					else:
						name = override
				names.append(name)
		self.names = tuple(names)
		self.update_cb(self.dat_id)

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

	def expand_entries(self):
		expanded = self.dat.expand_entries()
		if expanded:
			self.update_names()
		return expanded

class UnitsDATData(DATData):
	def __init__(self, data_context):
		DATData.__init__(self, data_context, DATID.units, UnitsDAT, 'Units.txt', 'Unit')

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
			else:
				name = ''
				if strings and self.data_context.settings.settings.get('customlabels'):
					if entry_id >= len(strings):
						name = self.unknown_name(entry_id)
					else:
						name = strings[entry_id]
				else:
					if entry_id >= len(DATA_CACHE[self.data_file]):
						name = self.unknown_name(entry_id)
					else:
						name = DATA_CACHE[self.data_file][entry_id]
				if entry_id in self.name_overrides:
					append, override = self.name_overrides[entry_id]
					if append:
						name += " " + override
					else:
						name = override
				names.append(name)
		self.names = tuple(names)
		self.update_cb(self.dat_id)

class EntryLabelDATData(DATData):
	def __init__(self, data_context, dat_id, dat_type, data_file, entry_type_name, label_offset=1):
		self.label_offset = label_offset
		DATData.__init__(self, data_context, dat_id, dat_type, data_file, entry_type_name)

	def update_names(self):
		names = []
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		strings = self.data_context.stat_txt.strings
		for entry_id in range(entry_count):
			name = ''
			if strings and self.data_context.settings.settings.get('customlabels'):
				if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
					name = self.reserved_name(entry_id)
				elif not dat:
					name = self.unknown_name()
				else:
					label_id = dat.get_entry(entry_id).label - self.label_offset
					if label_id < 0:
						name = 'None'
					elif label_id >= len(strings):
						name = self.unknown_name(entry_id)
					else:
						name = strings[label_id]
			else:
				if entry_id >= len(DATA_CACHE[self.data_file]):
					name = self.unknown_name(entry_id)
				else:
					name = DATA_CACHE[self.data_file][entry_id]
			if entry_id in self.name_overrides:
				append, override = self.name_overrides[entry_id]
				if append:
					name += " " + override
				else:
					name = override
			names.append(name)
		self.names = tuple(names)
		self.update_cb(self.dat_id)
