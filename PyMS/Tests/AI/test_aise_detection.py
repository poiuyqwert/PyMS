
from ...FileFormats.AIBIN.CodeHandlers import AISE, CodeCommands
from ...FileFormats.AIBIN.CodeHandlers.AIDecompileContext import AIDecompileContext

from ...Utilities.BytesScanner import BytesScanner

from ..utils import resource_path

import struct
import unittest

def _stub(target: int) -> bytes:
	return bytes([CodeCommands.Goto.byte_code_id or 0]) + target.to_bytes(4, 'little')

def _file(stubs: bytes, code_size: int) -> tuple[bytes, int, int]:
	# Returns (data, first script address, headers offset) for a file with the
	# given long jump table followed by `code_size` bytes of `stop` commands
	first = 4 + len(stubs)
	headers_offset = first + code_size
	data = headers_offset.to_bytes(4, 'little') + stubs + bytes([CodeCommands.Stop.byte_code_id or 0]) * code_size
	return (data, first, headers_offset)

def _header_addresses(name: str, header_size: int) -> tuple[bytes, int, list[int]]:
	with open(resource_path(name, __file__), 'rb') as f:
		data = f.read()
	headers_offset, = struct.unpack_from('<L', data)
	addresses: list[int] = []
	offset = headers_offset
	while struct.unpack_from('<L', data, offset)[0]:
		addresses.append(struct.unpack_from('<L', data, offset + 4)[0])
		offset += header_size
	return (data, headers_offset, addresses)

class Test_Long_Jump_Table_End(unittest.TestCase):
	def test_headers_past_expanded_offset_are_expanded(self) -> None:
		data, first, _ = _file(b'', 10)

		result = AISE.long_jump_table_end(data, AISE.expanded_headers_offset, [first])

		self.assertEqual(result, first)

	def test_headers_past_expanded_offset_without_scripts_are_expanded(self) -> None:
		data, _, _ = _file(b'', 10)

		result = AISE.long_jump_table_end(data, AISE.expanded_headers_offset, [0])

		self.assertEqual(result, AISE.expanded_headers_offset)

	def test_long_jump_table_under_expanded_offset_is_expanded(self) -> None:
		data, first, headers_offset = _file(_stub(14) + _stub(16), 10)

		result = AISE.long_jump_table_end(data, headers_offset, [0, first + 2, first])

		self.assertEqual(result, first)

	def test_script_at_start_of_code_is_not_expanded(self) -> None:
		data, first, headers_offset = _file(b'', 10)

		result = AISE.long_jump_table_end(data, headers_offset, [first])

		self.assertIsNone(result)

	def test_table_region_must_be_whole_long_jumps(self) -> None:
		data, first, headers_offset = _file(_stub(15) + b'\x00', 10)

		result = AISE.long_jump_table_end(data, headers_offset, [first])

		self.assertIsNone(result)

	def test_table_region_must_only_contain_gotos(self) -> None:
		stubs = _stub(14) + bytes([CodeCommands.Stop.byte_code_id or 0]) + (14).to_bytes(4, 'little')
		data, first, headers_offset = _file(stubs, 10)

		result = AISE.long_jump_table_end(data, headers_offset, [first])

		self.assertIsNone(result)

	def test_long_jump_targets_must_be_in_code(self) -> None:
		for target in (13, 24):
			with self.subTest(target=target):
				# First script at 14, headers at 24
				data, first, headers_offset = _file(_stub(14) + _stub(target), 10)

				result = AISE.long_jump_table_end(data, headers_offset, [first])

				self.assertIsNone(result)

	def test_scripts_past_headers_are_not_expanded(self) -> None:
		data, _, headers_offset = _file(_stub(14), 10)

		result = AISE.long_jump_table_end(data, headers_offset, [headers_offset + 5])

		self.assertIsNone(result)

	def test_no_scripts_with_code_is_not_expanded(self) -> None:
		data, _, headers_offset = _file(_stub(14), 10)

		result = AISE.long_jump_table_end(data, headers_offset, [0, 0])

		self.assertIsNone(result)

	def test_standard_files_are_not_expanded(self) -> None:
		for name, header_size in (('aiscript.bin', 16), ('bwscript.bin', 8)):
			with self.subTest(name=name):
				data, headers_offset, addresses = _header_addresses(name, header_size)

				result = AISE.long_jump_table_end(data, headers_offset, addresses)

				self.assertIsNone(result)

	def test_expanded_files_are_expanded(self) -> None:
		for name, header_size in (('expanded_aiscript.bin', 16), ('expanded_bwscript.bin', 8)):
			with self.subTest(name=name):
				data, headers_offset, addresses = _header_addresses(name, header_size)

				result = AISE.long_jump_table_end(data, headers_offset, addresses)

				self.assertEqual(result, min(address for address in addresses if address))

class Test_Load_Long_Jumps(unittest.TestCase):
	def test_reads_only_up_to_table_end(self) -> None:
		# The first script starts with a `goto`, which is code, not a long jump
		data, first, _ = _file(_stub(14) + _stub(19), 10)
		data = data[:first] + _stub(19) + data[first + 5:]
		context = AIDecompileContext(data)
		context.aise_context.expand(context.language_context)

		context.aise_context.load_long_jumps(BytesScanner(data, 4), context, first)

		self.assertEqual(context.aise_context.loaded_long_jumps, {4: 14, 9: 19})
