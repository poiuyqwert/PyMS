
# from .DefinitionsHandler import DefinitionsHandler

class SerializeContext(object):
	def __init__(self, definitions=None): # type: (str, DefinitionsHandler) -> SerializeContext
		self.definitions = definitions
		self._label_prefix = None
		self._label_counts = {} # type: dict[str, int]
		self._block_labels = {} # type: dict[CodeBlock, str]
		self._blocks_serialized = set()

	def set_label_prefix(self, label_prefix): # type: (str) -> None
		self._label_prefix = label_prefix

	def block_label(self, block): # type: (CodeBlock) -> str
		if not block in self._block_labels:
			prefix = self._label_prefix
			if len(block.owners) > 1:
				prefix = 'shared'
			if not prefix in self._label_counts:
				self._label_counts[prefix] = 0
			index = self._label_counts[prefix]
			self._label_counts[prefix] += 1
			self._block_labels[block] = '%s_%04d' % (prefix, index)
		return self._block_labels[block]

	def is_block_serialized(self, block): # type: (CodeBlock) -> bool
		return block in self._blocks_serialized

	def mark_block_serialized(self, block): # type: (CodeBlock) -> None
		self._blocks_serialized.add(block)
