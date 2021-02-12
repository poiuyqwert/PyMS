
class DATRef(object):
	def __init__(self, ref_name, ref_id, ref_id_range_end=None):
		self.ref_name = ref_name
		self.ref_id = ref_id
		self.ref_id_range_end = ref_id_range_end

	def matches(self, entry_id):
		if self.ref_id_range_end:
			return entry_id >= self.ref_id and entry_id <= self.ref_id_range_end
		else:
			return entry_id == self.ref_id
