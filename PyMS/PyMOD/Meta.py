
import os as _os
import hashlib as _hashlib
import json as _json

from typing import TypedDict, Literal

class Field:
	inputs: Literal['inputs'] = 'inputs'
	outputs: Literal['outputs'] = 'outputs'

class Meta(TypedDict):
	# A fingerprint of the full input set each target (keyed by its primary output) was built from,
	# so any changed, added, removed, or renamed input triggers a rebuild
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
		self.used_outputs: set[str] = set()
		# Whether the in-memory meta reflects what is on disk (so saving won't discard prior build info)
		self.ready = False

	def _key(self, file_path: str) -> str:
		return _os.path.relpath(file_path, self.root_path).replace(_os.sep, '/')

	# The fingerprint covers both the input paths and their contents — a renamed input can change
	# the output even with identical contents (e.g. GRP frame order comes from the file names)
	def _input_fingerprint(self, input_file_paths: list[str]) -> str | None:
		try:
			entries = sorted((self._key(file_path), compute_file_hash(file_path)) for file_path in input_file_paths)
		except Exception:
			return None
		digest = _hashlib.sha256()
		for key, file_hash in entries:
			digest.update(key.encode('utf-8'))
			digest.update(b'\x00')
			digest.update(file_hash.encode('utf-8'))
			digest.update(b'\x00')
		return digest.hexdigest()

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
		inputs = meta.get(Field.inputs, {})
		if not isinstance(inputs, dict):
			return False
		outputs = meta.get(Field.outputs, {})
		if not isinstance(outputs, dict):
			return False
		# Unknown fields (e.g. from older meta formats) are dropped
		self.meta = {
			'inputs': inputs,
			'outputs': outputs
		}
		return True

	def save(self, prune: bool = False) -> bool:
		if prune:
			used_output_keys = set(self._key(file_path) for file_path in self.used_outputs)
			self.meta[Field.inputs] = dict((key, fingerprint) for key, fingerprint in self.meta[Field.inputs].items() if key in used_output_keys)
			self.meta[Field.outputs] = dict((key, file_hash) for key, file_hash in self.meta[Field.outputs].items() if key in used_output_keys)
		try:
			with open(self.file_path, 'w', encoding='utf-8') as meta_file:
				_json.dump(self.meta, meta_file, indent=4)
		except Exception:
			return False
		return True

	def update_output_metas(self, file_paths: list[str]) -> bool:
		self.used_outputs.update(file_paths)
		try:
			file_hashes = list(compute_file_hash(file_path) for file_path in file_paths)
		except Exception:
			return False
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			self.meta[Field.outputs] = {}
		for file_path, file_hash in zip(file_paths, file_hashes):
			self.meta[Field.outputs][self._key(file_path)] = file_hash
		return True

	# Record a completed build of a target: its output hashes and a fingerprint of its full input set
	def update_metas(self, input_file_paths: list[str], output_file_paths: list[str]) -> bool:
		updated_outputs = self.update_output_metas(output_file_paths)
		if not Field.inputs in self.meta or not isinstance(self.meta[Field.inputs], dict):
			self.meta[Field.inputs] = {}
		target_key = self._key(output_file_paths[0])
		fingerprint = self._input_fingerprint(input_file_paths)
		if fingerprint is None:
			# Without a fingerprint this build can't be trusted as up to date by the next compile
			self.meta[Field.inputs].pop(target_key, None)
			return False
		self.meta[Field.inputs][target_key] = fingerprint
		return updated_outputs

	def has_output(self, file_path: str) -> bool:
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			return False
		return self._key(file_path) in self.meta[Field.outputs]

	def check_requires_update(self, input_file_paths: list[str], output_file_paths: list[str]) -> bool:
		self.used_outputs.update(output_file_paths)
		if not Field.inputs in self.meta or not isinstance(self.meta[Field.inputs], dict):
			return True
		if not Field.outputs in self.meta or not isinstance(self.meta[Field.outputs], dict):
			return True
		recorded_fingerprint = self.meta[Field.inputs].get(self._key(output_file_paths[0]))
		if recorded_fingerprint is None:
			return True
		for output_file_path in output_file_paths:
			if not self._key(output_file_path) in self.meta[Field.outputs]:
				return True
			if not _os.path.isfile(output_file_path):
				return True
			if compute_file_hash(output_file_path) != self.meta[Field.outputs][self._key(output_file_path)]:
				return True
		return self._input_fingerprint(input_file_paths) != recorded_fingerprint

def compute_file_hash(file_path: str) -> str:
	with open(file_path, 'rb') as file:
		return _hashlib.file_digest(file, 'sha256').hexdigest()
