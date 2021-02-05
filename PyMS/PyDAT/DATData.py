
from ..FileFormats.DAT import *
from ..FileFormats.TBL import decompile_string

from ..Utilities.MPQHandler import MPQHandler
from ..Utilities.DataCache import DATA_CACHE

import copy

class DATData(object):
	def __init__(self, dat_type, data_file, entry_type_name):
		self.dat_type = dat_type
		self.data_file = data_file
		self.entry_type_name = entry_type_name
		self.dat = None
		self.default_dat = None
		# TODO: Make tuple
		self.names = []

	def load_defaults(self, mpqhandler):
		try:
			dat = self.dat_type()
			dat.load_file(mpqhandler.get_file('MPQ:arr\\' + self.dat_type.FILE_NAME, MPQHandler.GET_FROM_FOLDER_OR_MPQ))
		except:
			pass
		else:
			self.default_dat = dat
			if self.dat == None:
				self.dat = copy.deepcopy(dat)

	def update_names(self, data_context):
		entry_count = TechDAT.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		for entry_id in range(entry_count):
			if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
				self.names.append(self.reserved_name(entry_id))
			elif entry_id >= len(DATA_CACHE[self.data_file]):
				self.names.append(self.entry_name(entry_id))
			else:
				self.names.append(DATA_CACHE[self.data_file][entry_id])

	def reserved_name(self, entry_id):
		return "Reserved %s #%s" % (self.entry_type_name, entry_id)

	def entry_name(self, entry_id):
		if entry_id >= len(self.names):
			return "%s #%s" % (self.entry_type_name, entry_id)
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
	def __init__(self):
		DATData.__init__(self, UnitsDAT, 'Units.txt', 'Unit')

	def update_names(self, data_context):
		self.names = []
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		strings = data_context.unitnamestbl.strings or data_context.stat_txt.strings
		for entry_id in range(entry_count):
			if strings and data_context.settings.settings.customlabels:
				if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
					self.names.append(self.reserved_name(entry_id))
				elif entry_id >= len(strings):
					self.names.append(self.entry_name(entry_id))
				else:
					self.names.append(strings[entry_id])
			else:
				if entry_id >= len(DATA_CACHE[self.data_file]):
					self.names.append(self.entry_name(entry_id))
				else:
					self.names.append(DATA_CACHE[self.data_file][entry_id])

class EntryLabelDATData(DATData):
	def __init__(self, dat_type, data_file, entry_type_name, label_offset=1):
		self.label_offset = label_offset
		DATData.__init__(self, dat_type, data_file, entry_type_name)

	def update_names(self, data_context):
		self.names = []
		entry_count = self.dat_type.FORMAT.entries
		dat = self.dat or self.default_dat
		if dat:
			entry_count = dat.entry_count()
		strings = data_context.stat_txt.strings
		for entry_id in range(entry_count):
			if strings and data_context.settings.settings.customlabels:
				if self.dat_type.FORMAT.expanded_entries_reserved and entry_id in self.dat_type.FORMAT.expanded_entries_reserved:
					self.names.append(self.reserved_name(entry_id))
				else:
					label_id = dat.get_entry(entry_id).label - self.label_offset
					if label_id < 0:
						self.names.append('None')
					elif label_id >= len(strings):
						self.names.append(self.entry_name(entry_id))
					else:
						self.names.append(strings[label_id])
			else:
				if entry_id >= len(DATA_CACHE[self.data_file]):
					self.names.append(self.entry_name(entry_id))
				else:
					self.names.append(DATA_CACHE[self.data_file][entry_id])
	