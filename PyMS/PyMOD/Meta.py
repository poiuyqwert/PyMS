
import os as _os
import hashlib as _hashlib
import json as _json

from typing import TypedDict, Literal, cast

class Field:
	inputs: Literal['inputs'] = 'inputs'
	outputs: Literal['outputs'] = 'outputs'

class Meta(TypedDict):
	inputs: dict[str, str]
	outputs: dict[str, str]

class MetaHandler:
	def __init__(self, file_path: str):
		self.file_path = file_path
		self.meta: Meta = {
			'inputs': {},
			'outputs': {}
		}
		self.used_outputs: set[str] = set()

	def exists(self) -> bool:
		return _os.path.isfile(self.file_path)

	def load(self) -> bool:
		try:
			with open(self.file_path, 'r') as meta_file:
				meta = _json.load(meta_file)
		except:
			return False
		if not isinstance(meta, dict):
			return False
		if not Field.inputs in meta:
			meta[Field.inputs] = {}
		elif not isinstance(meta[Field.inputs], dict):
			return False
		if not Field.outputs in meta:
			meta[Field.outputs] = {}
		elif not isinstance(meta[Field.outputs], dict):
			return False
		self.meta = cast(Meta, meta)
		return True

	def save(self) -> bool:
		try:
			with open(self.file_path, 'w') as meta_file:
				_json.dump(self.meta, meta_file, indent=4)
		except:
			return False
		return True

	def _update_meta_hashes(self, type: Literal['inputs', 'outputs'], file_paths: list[str], file_hashes: list[str] | None = None) -> bool:
		if not file_hashes:
			try:
				file_hashes = list(compute_file_hash(file_path) for file_path in file_paths)
			except:
				pass
		if not file_hashes:
			return False
		if not type in self.meta or not isinstance(self.meta[type], dict):
			self.meta[type] = {}
		for file_path,file_hash in zip(file_paths, file_hashes):
			self.meta[type][file_path] = file_hash
		return True

	def update_input_metas(self, file_paths: list[str]) -> bool:
		return self._update_meta_hashes(Field.inputs, file_paths)

	def update_output_metas(self, file_paths: list[str]) -> bool:
		self.used_outputs.update(file_paths)
		return self._update_meta_hashes(Field.outputs, file_paths)

	def check_requires_update(self, input_file_paths: list[str], output_file_paths: list[str]) -> bool:
		if not Field.inputs in self.meta or not isinstance(self.meta[Field.inputs], dict):
			return True
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			return True
		self.used_outputs.update(output_file_paths)
		for output_file_path in output_file_paths:
			if not output_file_path in self.meta[Field.outputs]:
				return True
			if not _os.path.isfile(output_file_path):
				return True
			if compute_file_hash(output_file_path) != self.meta[Field.outputs][output_file_path]:
				return True
		for input_file_path in input_file_paths:
			if not input_file_path in self.meta[Field.inputs]:
				return True
			if compute_file_hash(input_file_path) != self.meta[Field.inputs][input_file_path]:
				return True
		return False

def compute_file_hash(file_path: str) -> str:
	hash = _hashlib.sha256()

	with open(file_path, 'rb') as file:
		while True:
			# Reading is buffered, so we can read smaller chunks.
			chunk = file.read(hash.block_size)
			if not chunk:
				break
			hash.update(chunk)

	return hash.hexdigest()
