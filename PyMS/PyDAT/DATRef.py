
class DATRef(object):
	def __init__(self, name, id, id_range_end=None):
		self.name = name
		self.id = id
		self.id_range_end = id_range_end

	def matches(self, entry_id):
		if self.id_range_end:
			return entry_id >= self.id and entry_id <= self.id_range_end
		else:
			return entry_id == self.id

	def __repr__(self):
		return "<DATRef '%s' %s%s>" % (self.name, self.id, '-%s' % self.id_range_end if self.id_range_end != None else '')