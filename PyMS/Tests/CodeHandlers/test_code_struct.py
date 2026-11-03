from ._helpers import make_parse_context, ByteType, WordType

from ...Utilities.CodeHandlers.CodeStruct import StructField, StructBlockDefinition, StructBlock, StructSourceCodeParser, parse_struct_blocks
from ...Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition, CodeCommand
from ...Utilities.CodeHandlers.CodeType import IntCodeType
from ...Utilities.CodeHandlers.ParseContext import ParseContext
from ...Utilities.CodeHandlers.SerializeContext import SerializeContext
from ...Utilities.CodeHandlers.Formatters import Formatters
from ...Utilities.PyMSError import PyMSError
from ...Utilities import Struct

import io
import unittest

class NamedIDType(IntCodeType):
	def __init__(self) -> None:
		super().__init__('id', 'an ID', Struct.l_u16)

	def comment(self, value: int, _context: SerializeContext) -> str | None:
		return f'Item {value}'

Size = CodeCommandDefinition('size', 'Size {1}', None, (ByteType,))
Red = CodeCommandDefinition('red', 'Red', None)
Blue = CodeCommandDefinition('blue', 'Blue {1}', None, (WordType,))
Note = CodeCommandDefinition('note', 'Note {1}', None, (WordType,))

ColorField = StructField('color', (Red, Blue))

Part = StructBlockDefinition('part', 'part', 'Part {0}', (ByteType,), fields=(StructField('size', (Size,)),))
Item = StructBlockDefinition('item', 'item', 'Item {0}', (NamedIDType(),), fields=(
	StructField('size', (Size,)),
	ColorField,
	StructField('note', (Note,), required=False),
), children=(Part,))

def _parse(code: str) -> list[StructBlock]:
	return list(parse_struct_blocks(make_parse_context(code, with_block=False), (Item, Part)))

def _serialize(block: StructBlock) -> str:
	output = io.StringIO()
	block.serialize(SerializeContext(output, formatters=Formatters(indent='\t')))
	return output.getvalue()

ITEM = '''item 3 {\t# Item 3
\tsize 2
\tblue 7
\tpart 1 {
\t\tsize 4
\t}
\tpart 1 {
\t\tsize 5
\t}
}
'''

class Test_Parse(unittest.TestCase):
	def test_parses_fields_and_children(self) -> None:
		blocks = _parse(ITEM)
		self.assertEqual(len(blocks), 1)
		block = blocks[0]
		self.assertIs(block.definition, Item)
		self.assertEqual(block.header_params, [3])
		self.assertEqual(block.param(Size), 2)
		command = block.get(ColorField)
		assert command is not None
		self.assertIs(command.definition, Blue)
		self.assertIsNone(block.find(Note))
		self.assertEqual(block.param(Note, 9), 9)
		self.assertEqual([child.header_params for child in block.children], [[1], [1]])
		self.assertEqual([child.param(Size) for child in block.children], [4, 5])

	def test_round_trip(self) -> None:
		self.assertEqual(_serialize(_parse(ITEM)[0]), ITEM)

	def test_blank_lines_and_comments_are_skipped(self) -> None:
		blocks = _parse('\n# Comment\nitem 1 {\t# Comment\n\n\tsize 1\n\t# Comment\n\tred\n}\n\npart 2 {\n\tsize 3\n}')
		self.assertEqual([block.header_params for block in blocks], [[1], [2]])

	def assertParseError(self, code: str, message: str, line: int) -> None:
		with self.assertRaises(PyMSError) as cm:
			_parse(code)
		self.assertIn(message, str(cm.exception))
		self.assertEqual(cm.exception.line, line)

	def test_missing_required_field(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n}\n', "Item 1 is missing 'color'", 3)

	def test_duplicate_field(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n\tsize 2\n\tred\n}\n', "Duplicate item command 'size'", 3)

	def test_duplicate_choice(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n\tred\n\tblue 1\n}\n', "Duplicate item command 'blue'", 4)

	def test_unknown_command(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n\tgreen\n}\n', "Unknown item command 'green'", 3)

	def test_child_commands_are_scoped(self) -> None:
		self.assertParseError('item 1 {\n\tpart 1 {\n\t\tred\n\t}\n}\n', "Unknown part command 'red'", 3)

	def test_missing_open_brace(self) -> None:
		self.assertParseError('item 1\n', "Expected a '{' to start the item, got", 1)

	def test_text_after_open_brace(self) -> None:
		self.assertParseError('item 1 { size 1\n}\n', "Unexpected token 'size' (expected end of line)", 1)

	def test_missing_close_brace(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n\tred\n', "Expected a '}' to end the item, got end of file instead", 4)

	def test_text_after_close_brace(self) -> None:
		self.assertParseError('item 1 {\n\tsize 1\n\tred\n} 5\n', "Unexpected token '5' (expected end of line or file)", 4)

	def test_text_after_child_close_brace(self) -> None:
		self.assertParseError('item 1 {\n\tpart 1 {\n\t\tsize 1\n\t} 5\n}\n', "Unexpected token '5' (expected end of line or file)", 4)

	def test_header_param_is_validated(self) -> None:
		self.assertParseError('part 256 {\n\tsize 1\n}\n', 'Value is too large for `byte`', 1)

	def test_unexpected_top_level_token(self) -> None:
		self.assertParseError('size 1\n', "Unexpected token 'size' (expected 'item' or 'part')", 1)

	def test_command_used_by_two_fields(self) -> None:
		with self.assertRaises(PyMSError) as cm:
			StructBlockDefinition('bad', 'bad', 'Bad', (), fields=(StructField('a', (Red,)), StructField('b', (Red,))))
		self.assertIn("Command 'red' is used by more than one field of 'bad'", str(cm.exception))

class Test_Serialize(unittest.TestCase):
	def test_commands_and_children_are_indented(self) -> None:
		part = StructBlock(Part, [2], [CodeCommand(Size, [1])])
		item = StructBlock(Item, [5], [CodeCommand(Size, [3]), CodeCommand(Red, [])], [part])
		self.assertEqual(_serialize(item), 'item 5 {\t# Item 5\n\tsize 3\n\tred\n\tpart 2 {\n\t\tsize 1\n\t}\n}\n')

class Test_StructSourceCodeParser(unittest.TestCase):
	def test_other_keywords_are_not_parsed(self) -> None:
		handled: list[StructBlock] = []
		parser = StructSourceCodeParser(Part, lambda _context, block: handled.append(block))
		self.assertFalse(parser.parse(make_parse_context('item 1 {\n}\n', with_block=False)))
		self.assertEqual(handled, [])

	def test_handles_its_block(self) -> None:
		handled: list[tuple[ParseContext, StructBlock]] = []
		parse_context = make_parse_context('\npart 1 {\n\tsize 2\n}\n', with_block=False)
		parser = StructSourceCodeParser(Part, lambda context, block: handled.append((context, block)))
		self.assertTrue(parser.parse(parse_context))
		self.assertEqual(len(handled), 1)
		self.assertIs(handled[0][0], parse_context)
		self.assertEqual(handled[0][1].param(Size), 2)
		self.assertEqual(handled[0][1].line, 1)

	def test_text_after_close_brace(self) -> None:
		parser = StructSourceCodeParser(Part, lambda _context, _block: None)
		with self.assertRaises(PyMSError) as cm:
			parser.parse(make_parse_context('part 1 {\n\tsize 2\n} 5\n', with_block=False))
		self.assertIn("Unexpected token '5' (expected end of line or file)", str(cm.exception))
		self.assertEqual(cm.exception.line, 3)
