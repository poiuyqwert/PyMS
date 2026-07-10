
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
	def __init__(self, file_path: str, root_path: str):
		self.file_path = file_path
		self.root_path = root_path
		self.meta: Meta = {
			'inputs': {},
			'outputs': {}
		}
		self.used_inputs: set[str] = set()
		self.used_outputs: set[str] = set()
		# Whether the in-memory meta reflects what is on disk (so saving won't discard prior build info)
		self.ready = False

	def _key(self, file_path: str) -> str:
		return _os.path.relpath(file_path, self.root_path).replace(_os.sep, '/')

	def exists(self) -> bool:
		return _os.path.isfile(self.file_path)

	def load(self) -> bool:
		try:
			with open(self.file_path, 'r', encoding='utf-8') as meta_file:
				meta = _json.load(meta_file)
		except Exception:
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

	def save(self, prune: bool = False) -> bool:
		if prune:
			used_input_keys = set(self._key(file_path) for file_path in self.used_inputs)
			used_output_keys = set(self._key(file_path) for file_path in self.used_outputs)
			self.meta[Field.inputs] = dict((key, file_hash) for key, file_hash in self.meta[Field.inputs].items() if key in used_input_keys)
			self.meta[Field.outputs] = dict((key, file_hash) for key, file_hash in self.meta[Field.outputs].items() if key in used_output_keys)
		try:
			with open(self.file_path, 'w', encoding='utf-8') as meta_file:
				_json.dump(self.meta, meta_file, indent=4)
		except Exception:
			return False
		return True

	def _update_meta_hashes(self, field: Literal['inputs', 'outputs'], file_paths: list[str], file_hashes: list[str] | None = None) -> bool:
		if not file_hashes:
			try:
				file_hashes = list(compute_file_hash(file_path) for file_path in file_paths)
			except Exception:
				pass
		if not file_hashes:
			return False
		if not field in self.meta or not isinstance(self.meta[field], dict):
			self.meta[field] = {}
		for file_path,file_hash in zip(file_paths, file_hashes):
			self.meta[field][self._key(file_path)] = file_hash
		return True

	def update_input_metas(self, file_paths: list[str]) -> bool:
		self.used_inputs.update(file_paths)
		return self._update_meta_hashes(Field.inputs, file_paths)

	def update_output_metas(self, file_paths: list[str]) -> bool:
		self.used_outputs.update(file_paths)
		return self._update_meta_hashes(Field.outputs, file_paths)

	def has_output(self, file_path: str) -> bool:
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			return False
		return self._key(file_path) in self.meta[Field.outputs]

	def check_requires_update(self, input_file_paths: list[str], output_file_paths: list[str]) -> bool:
		self.used_inputs.update(input_file_paths)
		self.used_outputs.update(output_file_paths)
		if not Field.inputs in self.meta or not isinstance(self.meta[Field.inputs], dict):
			return True
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			return True
		for output_file_path in output_file_paths:
			if not self._key(output_file_path) in self.meta[Field.outputs]:
				return True
			if not _os.path.isfile(output_file_path):
				return True
			if compute_file_hash(output_file_path) != self.meta[Field.outputs][self._key(output_file_path)]:
				return True
		for input_file_path in input_file_paths:
			if not self._key(input_file_path) in self.meta[Field.inputs]:
				return True
			if compute_file_hash(input_file_path) != self.meta[Field.inputs][self._key(input_file_path)]:
				return True
		return False

def compute_file_hash(file_path: str) -> str:
	with open(file_path, 'rb') as file:
		return _hashlib.file_digest(file, 'sha256').hexdigest()
