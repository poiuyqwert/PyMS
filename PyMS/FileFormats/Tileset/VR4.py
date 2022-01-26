
from ...Utilities.utils import isstr
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

class VR4:
	MAX_ID 				= 0xFFFE / 2
	MAX_ID_EXPANDED_VX4 = 0xFFFFFFFE / 2

	def __init__(self):
		self.images = []
		self.lookup = {}

	def max_id(self, expanded_vx4=False):
		return VR4.MAX_ID_EXPANDED_VX4 if expanded_vx4 else VR4.MAX_ID
	def images_remaining(self, expanded_vx4=False):
		return self.max_id(expanded_vx4)+1 - len(self.images)

	# returns ([ids],isFlipped) or None
	def find_image(self, image):
		image = tuple(tuple(r) for r in image)
		image_hash = hash(image)
		if image_hash in self.lookup:
			return (self.lookup[image_hash],False)
		flipped_hash = hash(tuple(tuple(reversed(r)) for r in image))
		if flipped_hash in self.lookup:
			return (self.lookup[flipped_hash],True)
		return None

	def add_image(self, image):
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Add Image', 'Incorrect image size')
		id = len(self.images)
		self.images.append(tuple(tuple(r) for r in image))
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)
	def set_image(self, id, image):
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Set Image', 'Incorrect image size')
		old_hash = hash(self.images[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.images[id] = tuple(tuple(r) for r in image)
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)

	def load_file(self, file):
		data = load_file(file, 'VR4')
		if data and len(data) % 64:
			raise PyMSError('Load',"'%s' is an invalid VR4 file" % file)
		images = []
		lookup = {}
		try:
			for id in range(len(data) / 64):
				d = struct.unpack('64B', data[id*64:(id+1)*64])
				images.append(tuple(tuple(d[y:y+8]) for y in range(0,64,8)))
				image_hash = hash(images[-1])
				if not image_hash in self.lookup:
					lookup[image_hash] = []
				lookup[image_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported VR4 file '%s', could possibly be corrupt" % file)
		self.images = images
		self.lookup = lookup

	def save_file(self, file):
		data = ''
		for d in self.images:
			i = []
			for l in d:
				i.extend(l)
			data += struct.pack('64B', *i)
		if isstr(file):
			try:
				f = AtomicWriter(file, 'wb')
			except:
				raise PyMSError('Save',"Could not save the VR4 to '%s'" % file)
		else:
			f = file
		f.write(data)
		f.close()
