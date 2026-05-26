
from __future__ import annotations

from ...Utilities.fileutils import load_file
from ...Utilities.PyMSError import PyMSError
from ...Utilities.AtomicWriter import AtomicWriter

import struct

from typing import TYPE_CHECKING, Tuple, Sequence
if TYPE_CHECKING:
	from typing import BinaryIO

VR4Image = Tuple[Tuple[int, ...], ...]
VR4ImageInput = Sequence[Sequence[int]]

class VR4:
	MAX_ID 				= 0xFFFE // 2
	MAX_ID_EXPANDED_VX4 = 0xFFFFFFFE // 2

	def __init__(self) -> None:
		self._images: list[VR4Image] = []
		self._lookup: dict[int, list[int]] = {}

	@staticmethod
	def max_id( expanded_vx4: bool = False) -> int:
		return VR4.MAX_ID_EXPANDED_VX4 if expanded_vx4 else VR4.MAX_ID

	def image_count(self) -> int:
		return len(self._images)

	def images_remaining(self, expanded_vx4: bool = False) -> int:
		return self.max_id(expanded_vx4)+1 - len(self._images)

	@staticmethod
	def image_hash(image: VR4ImageInput, flip: bool = False) -> int:
		return hash(tuple(tuple(reversed(r) if flip else r) for r in image))

	@staticmethod
	def image_hashes(image: VR4ImageInput) -> tuple[int, int]:
		return (VR4.image_hash(image), VR4.image_hash(image, True))

	# returns ([normal_ids],[flipped_ids])
	def find_image_ids(self, image: VR4ImageInput) -> tuple[list[int], list[int]]:
		image = tuple(tuple(r) for r in image)
		image_hash, flipped_hash = self.image_hashes(image)
		return (list(self._lookup.get(image_hash, ())), list(self._lookup.get(flipped_hash, ())))

	def add_image(self, image: VR4ImageInput) -> None:
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Add Image', 'Incorrect image size (must be 8x8)')
		image_id = len(self._images)
		self._images.append(tuple(tuple(r) for r in image))
		image_hash = self.image_hash(self._images[image_id])
		if not image_hash in self._lookup:
			self._lookup[image_hash] = []
		self._lookup[image_hash].append(image_id)

	def set_image(self, image_id: int, image: VR4ImageInput) -> None:
		correct_size = (len(image) == 8)
		if correct_size:
			for r in image:
				if len(r) != 8:
					correct_size = False
					break
		if not correct_size:
			raise PyMSError('Set Image', 'Incorrect image size (must be 8x8)')
		old_hash = self.image_hash(self._images[image_id])
		self._lookup[old_hash].remove(image_id)
		if len(self._lookup[old_hash]) == 0:
			del self._lookup[old_hash]
		self._images[image_id] = tuple(tuple(r) for r in image)
		image_hash = self.image_hash(self._images[image_id])
		if not image_hash in self._lookup:
			self._lookup[image_hash] = []
		self._lookup[image_hash].append(image_id)

	def get_image(self, image_id: int) -> VR4Image:
		return self._images[image_id]

	def load_file(self, file: str | BinaryIO) -> None:
		data = load_file(file, 'VR4')
		if data and len(data) % 64:
			raise PyMSError('Load', f"'{file}' is an invalid VR4 file")
		images: list[VR4Image] = []
		lookup: dict[int, list[int]] = {}
		try:
			for image_id in range(len(data) // 64):
				d = tuple(int(v) for v in struct.unpack('64B', data[image_id*64:(image_id+1)*64]))
				images.append(tuple(tuple(d[y:y+8]) for y in range(0,64,8)))
				image_hash = self.image_hash(images[-1])
				if not image_hash in self._lookup:
					lookup[image_hash] = []
				lookup[image_hash].append(image_id)
		except Exception as exc:
			raise PyMSError('Load', f"Unsupported VR4 file '{file}', could possibly be corrupt") from exc
		self._images = images
		self._lookup = lookup

	def save_file(self, file: str | BinaryIO) -> None:
		data = b''
		for d in self._images:
			i: list[int] = []
			for l in d:
				i.extend(l)
			data += struct.pack('64B', *i)
		if isinstance(file, str):
			try:
				f = AtomicWriter(file, 'wb')
				f.write(data)
				f.close()
			except Exception as exc:
				raise PyMSError('Save', f"Could not save the VR4 to '{file}'") from exc
		else:
			file.write(data)
			file.close()
