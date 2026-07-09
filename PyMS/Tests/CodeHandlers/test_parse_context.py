
from ._helpers import make_parse_context

from ...Utilities.CodeHandlers import CodeType
from ...Utilities.CodeHandlers.CodeHeader import CodeHeader
from ...Utilities.CodeHandlers.DefinitionsHandler import DefinitionsHandler
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities import Struct

import unittest
from typing import cast


THREE_LINES = 'line0\nline1\nline2'


class Test_Error(unittest.TestCase):
	def test_explicit_line_is_displayed_one_indexed(self) -> None:
		ctx = make_parse_context(THREE_LINES, with_block=False)
		error = ctx.error('Parse', 'boom', line=1)
		# PyMSError displays lines 1-indexed (constructor adds one).
		self.assertEqual(error.line, 2)
		self.assertEqual(error.code, 'line1')

	def test_default_line_is_current_lexer_line(self) -> None:
		ctx = make_parse_context(THREE_LINES, with_block=False)
		error = ctx.error('Parse', 'boom')
		self.assertEqual(error.line, 1)
		self.assertEqual(error.code, 'line0')


class Test_AttributeError(unittest.TestCase):
	def test_fills_missing_line_and_code(self) -> None:
		ctx = make_parse_context(THREE_LINES, with_block=False)
		error = PyMSError('Parse', 'boom')
		ctx.attribute_error(error)
		self.assertEqual(error.line, 1)
		self.assertEqual(error.code, 'line0')

	def test_preserves_existing_line_and_code(self) -> None:
		ctx = make_parse_context(THREE_LINES, with_block=False)
		error = PyMSError('Parse', 'boom', line=1, code='custom')
		ctx.attribute_error(error)
		self.assertEqual(error.line, 2)  # 1 + constructor increment
		self.assertEqual(error.code, 'custom')


class Test_Warning(unittest.TestCase):
	def test_builds_warning_with_line_and_code(self) -> None:
		ctx = make_parse_context(THREE_LINES, with_block=False)
		warning = ctx.warning(warn_type='Parse', warning='w', line=1)
		self.assertEqual(warning.line, 2)
		self.assertEqual(warning.code, 'line1')


class Test_AttributeWarning(unittest.TestCase):
	def test_does_not_clobber_existing_code(self) -> None:
		# A caller-supplied code on a warning must be preserved through
		# attribution, like errors preserve theirs.
		ctx = make_parse_context(THREE_LINES, with_block=False)
		warning = PyMSWarning(warn_type='Parse', warning='w', line=0, code='custom')
		ctx.add_warning(warning)
		self.assertEqual(warning.code, 'custom')

	def test_code_matches_the_warnings_reported_line(self) -> None:
		# The attached source code must correspond to the warning's own line,
		# not the following line.
		ctx = make_parse_context(THREE_LINES, with_block=False)
		warning = ctx.warning(warn_type='Parse', warning='w', line=1)
		ctx.add_warning(warning)
		self.assertEqual(warning.code, 'line1')

	def test_line_numbering_matches_errors(self) -> None:
		# A warning and an error created at the same lexer position must report
		# the same line number.
		ctx = make_parse_context(THREE_LINES, with_block=False)
		warning = PyMSWarning(warn_type='Parse', warning='w')
		error = PyMSError('Parse', 'e')
		ctx.attribute_warning(warning)
		ctx.attribute_error(error)
		self.assertEqual(warning.line, error.line)


class Test_Blocks(unittest.TestCase):
	def test_get_block_creates_and_marks_missing(self) -> None:
		ctx = make_parse_context('', with_block=False)
		block = ctx.get_block('foo')
		self.assertIn('foo', ctx.blocks)
		self.assertIn('foo', ctx.missing_blocks)
		# Looking it up again returns the same instance.
		self.assertIs(ctx.get_block('foo'), block)

	def test_define_block_records_definition_line(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.define_block('foo', 3)
		metadata = ctx.lookup_block_metadata_by_name('foo')
		assert metadata is not None
		self.assertEqual(metadata.definition_line, 3)

	def test_defining_a_block_clears_its_missing_status(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.get_block('foo')
		ctx.define_block('foo', 2)
		self.assertNotIn('foo', ctx.missing_blocks)

	def test_redefining_a_block_raises(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.define_block('foo', 1)
		with self.assertRaises(PyMSError) as cm:
			ctx.define_block('foo', 2)
		self.assertIn("A block named 'foo' is already defined", str(cm.exception))


class Test_AddBlockUse(unittest.TestCase):
	def test_use_propagates_to_next_and_referenced_blocks(self) -> None:
		ctx = make_parse_context('', with_block=False)
		head = ctx.get_block('head')
		nxt = ctx.get_block('next')
		ref = ctx.get_block('ref')
		head.next_block = nxt
		head.ref_blocks.append(ref)
		owner = cast(CodeHeader, object())
		ctx.add_block_use(head, owner)
		self.assertIn(owner, ctx.block_metadata[nxt].uses)
		self.assertIn(owner, ctx.block_metadata[ref].uses)


class Test_Finalize(unittest.TestCase):
	def test_missing_block_raises(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.get_block('never_defined')
		with self.assertRaises(PyMSError) as cm:
			ctx.finalize()
		self.assertIn('not defined', str(cm.exception))

	def test_unterminated_last_block_raises(self) -> None:
		ctx = make_parse_context('', with_block=False)
		block = ctx.define_block('blk', 1)
		ctx.active_block = block
		with self.assertRaises(PyMSError) as cm:
			ctx.finalize()
		self.assertIn('does not end', str(cm.exception))

	def test_unused_block_produces_discard_warning(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.define_block('blk', 1)
		ctx.unused_blocks.add('blk')
		ctx.finalize()
		self.assertTrue(any(w.id == 'block_unused' for w in ctx.warnings))

	def test_suppressed_warning_ids_are_filtered(self) -> None:
		ctx = make_parse_context('', with_block=False)
		ctx.settings.suppress_warnings.append('noisy')
		ctx.warnings.append(PyMSWarning(warn_type='Parse', warning='a', warn_id='noisy'))
		ctx.warnings.append(PyMSWarning(warn_type='Parse', warning='b', warn_id='kept'))
		ctx.finalize()
		ids = [w.id for w in ctx.warnings]
		self.assertNotIn('noisy', ids)
		self.assertIn('kept', ids)


class Test_LookupParamValue(unittest.TestCase):
	def test_substitutes_variable_value(self) -> None:
		int_type = CodeType.IntCodeType('num', 'n', Struct.l_u16)
		definitions = DefinitionsHandler()
		definitions.set_variable('answer', 42, int_type)
		ctx = make_parse_context('answer', definitions=definitions)
		self.assertEqual(int_type.parse(ctx), 42)

	def test_type_mismatch_raises(self) -> None:
		int_type = CodeType.IntCodeType('num', 'n', Struct.l_u16)
		float_type = CodeType.FloatCodeType('dec', 'd', Struct.l_float)
		definitions = DefinitionsHandler()
		definitions.set_variable('flt', 1.0, float_type)
		ctx = make_parse_context('flt', definitions=definitions)
		with self.assertRaises(PyMSError) as cm:
			int_type.parse(ctx)
		self.assertIn("Incorrect type on variable 'flt'", str(cm.exception))

	def test_variable_value_is_validated_against_parameter_limits(self) -> None:
		# A variable defined under a permissive type but used where the
		# parameter is tighter must still be range-checked.
		permissive = CodeType.IntCodeType('big', 'b', Struct.l_u16)
		definitions = DefinitionsHandler()
		definitions.set_variable('huge', 300, permissive)
		tight = CodeType.IntCodeType('small', 's', Struct.l_u8)
		ctx = make_parse_context('huge', definitions=definitions)
		with self.assertRaises(PyMSError) as cm:
			tight.parse(ctx)
		self.assertIn('Value is too large for `small`', str(cm.exception))

	def test_variable_with_invalid_enum_case_is_rejected(self) -> None:
		# An enum parameter must reject a value with no case whether it comes
		# from a literal or a substituted variable.
		enum = CodeType.EnumCodeType('choice', 'c', Struct.l_u8, ['first', 'second'])
		definitions = DefinitionsHandler()
		definitions.set_variable('bogus', 99, enum)
		ctx = make_parse_context('bogus', definitions=definitions)
		with self.assertRaises(PyMSError) as cm:
			enum.parse(ctx)
		self.assertIn('Value `99` is not a valid case for `choice`', str(cm.exception))


if __name__ == '__main__':
	unittest.main()
