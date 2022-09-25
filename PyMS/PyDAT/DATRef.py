
class DATRefs(object):
	def __init__(self, dat_id, refs_lookup):
		self.dat_id = dat_id
		self.refs_lookup = refs_lookup

	def matching(self, data_context, lookup_id):
		matches = []
		dat_data = data_context.dat_data(self.dat_id)
		if not dat_data.dat:
			return []
		for check_entry_id in range(dat_data.entry_count()):
			check_entry = dat_data.dat.get_entry(check_entry_id)
			check_refs = self.refs_lookup(check_entry)
			for ref in check_refs:
				if ref.matches(lookup_id):
					matches.append(DATRefMatch(self.dat_id, ref.dat_sub_tab, ref.field_name, check_entry_id, dat_data.entry_name(check_entry_id)))
		return matches

class DATRef(object):
	def __init__(self, field_name, entry_id, entry_id_range_end=None, dat_sub_tab=None):
		self.field_name = field_name
		self.entry_id = entry_id
		self.entry_id_range_end = entry_id_range_end
		self.dat_sub_tab = dat_sub_tab

	def matches(self, entry_id):
		if self.entry_id_range_end:
			return entry_id >= self.entry_id and entry_id <= self.entry_id_range_end
		else:
			return entry_id == self.entry_id

class DATRefMatch(object):
	def __init__(self, dat_id, dat_sub_tab_id, field_name, entry_id, entry_name):
		self.dat_id = dat_id
		self.dat_sub_tab_id = dat_sub_tab_id
		self.field_name = field_name
		self.entry_id = entry_id
		self.entry_name = entry_name

	def __str__(self):
		dat_sub_tab = ''
		if self.dat_sub_tab_id:
			dat_sub_tab = ' (%s sub-tab)' % self.dat_sub_tab_id.tab_name
		return '%s, %s field%s, entry %s: %s' % (self.dat_id.filename, self.field_name, dat_sub_tab, self.entry_id, self.entry_name)
