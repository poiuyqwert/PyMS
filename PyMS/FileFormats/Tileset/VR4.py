
from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING, Tuple, Sequence
if TYPE_CHECKING:
	from typing import BinaryIO

VR4Image = Tuple[Tuple[int, ...], ...]
VR4ImageInput = Sequence[Sequence[int]]

class VR4(object):
	MAX_ID 				= int(0xFFFE / 2)
	MAX_ID_EXPANDED_VX4 = int(0xFFFFFFFE / 2)

	def __init__(self): # type: () -> None
		self.images = [] # type: list[VR4Image]
		self.lookup = {} # type: dict[int, list[int]]

	def max_id(self, expanded_vx4=False): # type: (bool) -> int
		return VR4.MAX_ID_EXPANDED_VX4 if expanded_vx4 else VR4.MAX_ID
	def images_remaining(self, expanded_vx4=False): # type: (bool) -> int
		return self.max_id(expanded_vx4)+1 - len(self.images)

	# returns ([ids],isFlipped) or None
	def find_image(self, image): # type: (VR4ImageInput) -> (tuple[list[int], bool] | None)
		image = tuple(tuple(r) for r in image)
		image_hash = hash(image)
		if image_hash in self.lookup:
			return (self.lookup[image_hash],False)
		flipped_hash = hash(tuple(tuple(reversed(r)) for r in image))
		if flipped_hash in self.lookup:
			return (self.lookup[flipped_hash],True)
		return None

	def add_image(self, image): # type: (VR4ImageInput) -> None
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Add Image', 'Incorrect image size (must be 8x8)')
		id = len(self.images)
		self.images.append(tuple(tuple(r) for r in image))
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)

	def set_image(self, id, image): # type: (int, VR4ImageInput) -> None
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Set Image', 'Incorrect image size (must be 8x8)')
		old_hash = hash(self.images[id])
		self.lookup[old_hash].remove(id)
		if len(self.lookup[old_hash]) == 0:
			del self.lookup[old_hash]
		self.images[id] = tuple(tuple(r) for r in image)
		image_hash = hash(self.images[id])
		if not image_hash in self.lookup:
			self.lookup[image_hash] = []
		self.lookup[image_hash].append(id)

	def load_file(self, file): # type: (str | BinaryIO) -> None
		data = load_file(file, 'VR4')
		if data and len(data) % 64:
			raise PyMSError('Load',"'%s' is an invalid VR4 file" % file)
		images = [] # type: list[VR4Image]
		lookup = {} # type: dict[int, list[int]]
		try:
			for id in range(int(len(data) / 64)):
				d = tuple(int(v) for v in struct.unpack('64B', data[id*64:(id+1)*64]))
				images.append(tuple(tuple(d[y:y+8]) for y in range(0,64,8)))
				image_hash = hash(images[-1])
				if not image_hash in self.lookup:
					lookup[image_hash] = []
				lookup[image_hash].append(id)
		except:
			raise PyMSError('Load',"Unsupported VR4 file '%s', could possibly be corrupt" % file)
		self.images = images
		self.lookup = lookup

	def save_file(self, file): # type: (str | BinaryIO) -> None
		data = b''
		for d in self.images:
			i = [] # type: list[int]
			for l in d:
				i.extend(l)
			data += struct.pack('64B', *i)
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except:
				raise PyMSError('Save',"Could not save the VR4 to '%s'" % file)
		else:
			file.write(data)
			file.close()
