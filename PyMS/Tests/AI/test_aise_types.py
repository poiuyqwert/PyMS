
from . import utils

from ...FileFormats.AIBIN.CodeHandlers.AIDecompileContext import AIDecompileContext
from ...FileFormats.AIBIN.CodeHandlers.AIByteCodeCompiler import AIByteCodeCompiler
from ...FileFormats.AIBIN.CodeHandlers import AISECodeTypes
from ...FileFormats.AIBIN.CodeHandlers import AISEIdleOrder

from ...Utilities.BytesScanner import BytesScanner
from ...Utilities.PyMSError import PyMSError

import unittest

class Test_PointCodeType(unittest.TestCase):
	def test_decompile(self) -> None:
		data = b'\x01\x00\x02\x00'
		expected = (1, 2)
		context = AIDecompileContext(data)
		scanner = BytesScanner(data)
		code_type = AISECodeTypes.PointCodeType()

		result = code_type.decompile(scanner, context)

		self.assertEqual(result, expected)

	def test_compile(self) -> None:
		value = (1, 2)
		expected = b'\x01\x00\x02\x00'
		builder = AIByteCodeCompiler()
		code_type = AISECodeTypes.PointCodeType()
		
		code_type.compile(value, builder)
		result = builder.data

		self.assertEqual(result, expected)

	def test_parse_success(self) -> None:
		cases = (
			('(1, 2)', (1, 2)),
			('Loc.1', (AISECodeTypes.PointCodeType.LOCATION, 1)),
			('ScriptArea', (AISECodeTypes.PointCodeType.SCRIPT_AREA, 0)),
		)
		code_type = AISECodeTypes.PointCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_parse_failure(self) -> None:
		cases = (
			('error', 'Expected a `point` value but got'),

			('(', 'Expected integer value in `point` x value'),
			('(a', 'Expected integer value in `point` x value'),
			('(1)', 'Expected comma between `point` x and y values'),
			('(1,a', 'Expected integer value in `point` y value'),
			('(1,2', 'Expected `)` to end `point`'),

			('Loc,', 'Expected `.` after `Loc` for `point`'),
			('Loc.a', 'Expected integer value for `point` location id'),
			('Loc.256', 'Location id `256` is not valid'),
		)
		code_type = AISECodeTypes.PointCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			with self.assertRaises(PyMSError) as error_context:
				_ = code_type.parse(parse_context)
			self.assertTrue(expected in str(error_context.exception), f'`{expected}` not in `{error_context.exception}`')

	def test_serialize(self) -> None:
		cases = (
			((1, 2), '(1, 2)'),
			((AISECodeTypes.PointCodeType.LOCATION, 1), 'Loc.1'),
			((AISECodeTypes.PointCodeType.SCRIPT_AREA, 0), 'ScriptArea'),
		)
		code_type = AISECodeTypes.PointCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_OrderCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		cases = (
			('0', 0),
			('Die', 0),
			('Fatal', 188),
		)
		code_type = AISECodeTypes.OrderCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			(0, 'Die'),
			(188, 'Fatal'),
		)
		code_type = AISECodeTypes.OrderCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_UnitIDCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		cases = (
			('1', 1),
			('227', 227),
			('none', 228),
			('any', 229),
			('group_men', 230),
			('group_buildings', 231),
			('group_factories', 232),
		)
		code_type = AISECodeTypes.UnitIDCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			(1, '1'),
			(227, '227'),
			(228, 'None'),
			(229, 'Any'),
			(230, 'Group_Men'),
			(231, 'Group_Buildings'),
			(232, 'Group_Factories'),
		)
		code_type = AISECodeTypes.UnitIDCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_UnitGroupCodeType(unittest.TestCase):
	def test_decompile(self) -> None:
		cases = (
			(b'\x01\x00', (1,)),
			(b'\xFE\x00', (254,)),
			(b'\x01\xFF\x01\x00', (1,)),
			(b'\x03\xFF\x01\x00\xE7\x00\xE8\x00', (1, 231, 232)),
		)
		code_type = AISECodeTypes.UnitGroupCodeType()
		for data, expected in cases:
			context = AIDecompileContext(data)
			scanner = BytesScanner(data)
			result = code_type.decompile(scanner, context)
			self.assertEqual(result, expected)

	def test_compile(self) -> None:
		cases = (
			((1,), b'\x01\x00'),
			((254,), b'\xFE\x00'),
			((1, 231, 232), b'\x03\xFF\x01\x00\xE7\x00\xE8\x00'),
		)
		code_type = AISECodeTypes.UnitGroupCodeType()
		for value, expected in cases:
			builder = AIByteCodeCompiler()
			code_type.compile(value, builder)
			result = builder.data
			self.assertEqual(result, expected)

	def test_parse(self) -> None:
		cases = (
			('1', (1,)),
			('227 | None', (227, 228)),
			('Any | Group_Men | Group_Buildings | Group_Factories', (229, 230, 231, 232))
		)
		code_type = AISECodeTypes.UnitGroupCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			((1,), '1'),
			((227, 228), '227 | None'),
			((229, 230, 231, 232), 'Any | Group_Men | Group_Buildings | Group_Factories')
		)
		code_type = AISECodeTypes.UnitGroupCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_AreaCodeType(unittest.TestCase):
	def test_decompile(self) -> None:
		data = b'\x01\x00\x02\x00\x03\x00'
		expected = ((1, 2), 3)
		context = AIDecompileContext(data)
		scanner = BytesScanner(data)
		code_type = AISECodeTypes.AreaCodeType()

		result = code_type.decompile(scanner, context)

		self.assertEqual(result, expected)

	def test_compile(self) -> None:
		value = ((1, 2), 3)
		expected = b'\x01\x00\x02\x00\x03\x00'
		builder = AIByteCodeCompiler()
		code_type = AISECodeTypes.AreaCodeType()
		
		code_type.compile(value, builder)
		result = builder.data

		self.assertEqual(result, expected)

	def test_parse_success(self) -> None:
		cases = (
			('(1, 2)', ((1, 2), 0)),
			('(1, 2) ~ 3', ((1, 2), 3)),
			('Loc.1', ((AISECodeTypes.PointCodeType.LOCATION, 1), 0)),
			('Loc.1 ~ 2', ((AISECodeTypes.PointCodeType.LOCATION, 1), 2)),
			('ScriptArea', ((AISECodeTypes.PointCodeType.SCRIPT_AREA, 0), 0)),
			('ScriptArea ~ 1', ((AISECodeTypes.PointCodeType.SCRIPT_AREA, 0), 1)),
		)
		code_type = AISECodeTypes.AreaCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_parse_failure(self) -> None:
		cases = (
			('(1, 2) ~ a', 'Expected integer value for `area` radius value'),
			('Loc.1 ~ a', 'Expected integer value for `area` radius value'),
			('ScriptArea ~ a', 'Expected integer value for `area` radius value'),
		)
		code_type = AISECodeTypes.AreaCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			with self.assertRaises(PyMSError) as error_context:
				_ = code_type.parse(parse_context)
			self.assertTrue(expected in str(error_context.exception), f'`{expected}` not in `{error_context.exception}`')

	def test_serialize(self) -> None:
		cases = (
			(((1, 2), 0), '(1, 2)'),
			(((1, 2), 3), '(1, 2) ~ 3'),
			(((AISECodeTypes.PointCodeType.LOCATION, 1), 0), 'Loc.1'),
			(((AISECodeTypes.PointCodeType.LOCATION, 1), 2), 'Loc.1 ~ 2'),
			(((AISECodeTypes.PointCodeType.SCRIPT_AREA, 0), 0), 'ScriptArea'),
			(((AISECodeTypes.PointCodeType.SCRIPT_AREA, 0), 1), 'ScriptArea ~ 1'),
		)
		code_type = AISECodeTypes.AreaCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_IssueOrderFlagsCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		cases = (
			('1', 0x01),
			('0xFF', 0xFF),
			('Enemies', 0x01),
			('IgnoreDatReqs', 0x40),
			('1 | 2', 0x03),
			('Enemies | IgnoreDatReqs', 0x41),
			('1 | 0x02 | Allied | IgnoreDatReqs', 0x47),
		)
		code_type = AISECodeTypes.IssueOrderFlagsCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			(0x01, 'Enemies'),
			(0x40, 'IgnoreDatReqs'),
			(0x03, 'Enemies | Own'),
			(0x41, 'Enemies | IgnoreDatReqs'),
			(0x47, 'Enemies | Own | Allied | IgnoreDatReqs'),
			(0xFF, 'Enemies | Own | Allied | SingleUnit | EachAtMostOnce | 0x20 | IgnoreDatReqs | 0x80'),
		)
		code_type = AISECodeTypes.IssueOrderFlagsCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_CompareTrigCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		cases = (
			('AtLeast', 0),
			('AtMost', 1),
			('Set', 7),
			('Add', 8),
			('Subtract', 9),
			('Exactly', 10),
			('Randomize', 11),
			('AtLeast_Call', 128),
			('AtMost_Call', 129),
			('Exactly_Call', 138),
			('AtLeast_Wait', 64),
			('AtMost_Wait', 65),
			('Exactly_Wait', 74),
		)
		code_type = AISECodeTypes.CompareTrigCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			(0, 'AtLeast'),
			(1, 'AtMost'),
			(7, 'Set'),
			(8, 'Add'),
			(9, 'Subtract'),
			(10, 'Exactly'),
			(11, 'Randomize'),
			(128, 'AtLeast_Call'),
			(129, 'AtMost_Call'),
			(138, 'Exactly_Call'),
			(64, 'AtLeast_Wait'),
			(65, 'AtMost_Wait'),
			(74, 'Exactly_Wait'),
		)
		code_type = AISECodeTypes.CompareTrigCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_IdleOrderCodeType(unittest.TestCase):
	def test_parse(self) -> None:
		cases = (
			('EnableBuiltin', 254),
			('DisableBuiltin', 255),
		)
		code_type = AISECodeTypes.IdleOrderCodeType()
		for code, expected in cases:
			parse_context = utils.parse_context(code)
			result = code_type.parse(parse_context)
			self.assertEqual(result, expected)

	def test_serialize(self) -> None:
		cases = (
			(254, 'EnableBuiltin'),
			(255, 'DisableBuiltin'),
		)
		code_type = AISECodeTypes.IdleOrderCodeType()
		for value, expected in cases:
			_, serialize_context = utils.serialize_context()
			result = code_type.serialize(value, serialize_context)
			self.assertEqual(result, expected)

class Test_IdleOrderFlagsCodeType(unittest.TestCase):
	def test_decompile(self) -> None:
		cases = (
			(b'\x00\x00', (AISEIdleOrder.BasicFlags(0),)),
			(b'\x26\x00', (AISEIdleOrder.BasicFlags(0x26),)),
			(b'\x26\x80', (AISEIdleOrder.BasicFlags(0x8026),)),
			(b'\x03\x01\x00\x00', (AISEIdleOrder.SpellEffects(False, 0x03), AISEIdleOrder.BasicFlags(0))),
			(b'\x03\x01\x02\x00', (AISEIdleOrder.SpellEffects(False, 0x03), AISEIdleOrder.BasicFlags(0x02))),
			(b'\x10\x03\x32\x00\x00\x00\x22\x03\x32\x00\x00\x00\x00\x00', (AISEIdleOrder.UnitProps(1, 0, 50), AISEIdleOrder.UnitProps(2, 2, 50), AISEIdleOrder.BasicFlags(0))),
			(b'\x00\x04\x02\x01\x00\x0A\x04\x20\x00\x00\x00', (
				(AISEIdleOrder.SpellEffects(False, 0x02), AISEIdleOrder.TileFlags(False, 0x04), AISEIdleOrder.BasicFlags(0x20)),
				AISEIdleOrder.BasicFlags(0))
			),
			(b'\x00\x04\x0A\x05\x02\x07\x00\x0A\x0C\x00\x00\x40\x01\x20\x02\x40\x03\x01\x00\x00\x00\x00\x08\x32\x00\x3C\x00\x00\x09\x0A\x32\x00\x06\x00\x0D\x01\x06\x40\x40\x00\x00\x20\x00', (
				(AISEIdleOrder.Order(order_id=10), AISEIdleOrder.Targetting(flags=2), AISEIdleOrder.TileFlags(without=False, flags=12), AISEIdleOrder.BasicFlags(flags=0)),
				AISEIdleOrder.SpellEffects(without=False, flags=64),
				AISEIdleOrder.SpellEffects(without=True, flags=32),
				AISEIdleOrder.UnitProps(field=4, comparison=0, amount=1),
				AISEIdleOrder.RandomRate(low=50, high=60),
				AISEIdleOrder.UnitCount(comparison=10, amount=50, radius=6, players=13),
				AISEIdleOrder.UnitFlags(without=True, flags=16448),
				AISEIdleOrder.BasicFlags(flags=32)
			)),
		)
		code_type = AISECodeTypes.IdleOrderFlagsCodeType()
		for data, expected in cases:
			context = AIDecompileContext(data)
			scanner = BytesScanner(data)
			result = code_type.decompile(scanner, context)
			print('####', result)
			self.assertEqual(result, expected)

	# def test_compile(self) -> None:
	# 	cases = (
	# 		((1,), b'\x01\x00'),
	# 		((254,), b'\xFE\x00'),
	# 		((1, 231, 232), b'\x03\xFF\x01\x00\xE7\x00\xE8\x00'),
	# 	)
	# 	code_type = AISECodeTypes.IdleOrderFlagsCodeType()
	# 	for value, expected in cases:
	# 		builder = AIByteCodeCompiler()
	# 		code_type.compile(value, builder)
	# 		result = builder.data
	# 		self.assertEqual(result, expected)

	# def test_parse_success(self) -> None:
	# 	cases = (
	# 		('(1, 2)', (1, 2)),
	# 		('Loc.1', (2, 1)),
	# 		('ScriptArea', (3, 0)),
	# 	)
	# 	code_type = AISECodeTypes.IdleOrderFlagsCodeType()
	# 	for code, expected in cases:
	# 		parse_context = utils.parse_context(code)
	# 		result = code_type.parse(parse_context)
	# 		self.assertEqual(result, expected)

	# def test_parse_failure(self) -> None:
	# 	cases = (
	# 		('error', 'Expected a `point` value but got'),

	# 		('(', 'Expected integer value in `point` x value'),
	# 		('(a', 'Expected integer value in `point` x value'),
	# 		('(1)', 'Expected comma between `point` x and y values'),
	# 		('(1,a', 'Expected integer value in `point` y value'),
	# 		('(1,2', 'Expected `)` to end `point`'),

	# 		('Loc,', 'Expected `.` after `Loc` for `point`'),
	# 		('Loc.a', 'Expected integer value for `point` location id'),
	# 		('Loc.256', 'Location id `256` is not valid'),
	# 	)
	# 	code_type = AISECodeTypes.IdleOrderFlagsCodeType()
	# 	for code, expected in cases:
	# 		parse_context = utils.parse_context(code)
	# 		with self.assertRaises(PyMSError) as error_context:
	# 			_ = code_type.parse(parse_context)
	# 		self.assertTrue(expected in str(error_context.exception), f'`{expected}` not in `{error_context.exception}`')

	# def test_serialize(self) -> None:
	# 	cases = (
	# 		((1, 2), '(1, 2)'),
	# 		((2, 1), 'Loc.1'),
	# 		((3, 0), 'ScriptArea'),
	# 	)
	# 	code_type = AISECodeTypes.IdleOrderFlagsCodeType()
	# 	for value, expected in cases:
	# 		_, serialize_context = utils.serialize_context()
	# 		result = code_type.serialize(value, serialize_context)
	# 		self.assertEqual(result, expected)

# # Nothing
# '0'
# b'\x00\x00'

# # Simple u16 flags
# 'Own|Allied|InCombat'
# b'\x26\x00'

# # Simple u16 flags with high bits used
# 'Own|Allied|InCombat|Remove'
# b'\x26\x80'

# # Extended filter
# 'SpellEffects(Ensnare|Plague)'
# b'\x03\x01\x00\x00'

# # Extended filter + simple flag;
# # Simple flag field always terminates the parameter while other filters can (should?) be compiled in the order they are in text.
# 'Own|SpellEffects(Ensnare|Plague)'
# b'\x03\x01\x02\x00'

# 'SpellEffects(Ensnare|Plague)|Own'
# b'\x03\x01\x02\x00'

# # Two filters with same type id. Also example where a filter needs more space than just single u16
# 'Shields(LessThan, 50)|Health(LessThanPercent, 50)'
# b'\x10\x03\x00\x32\x00\x00\x22\x03\x32\x00\x00\x00\x00\x00'

# # `Self` contains another idle_order_flags inside it
# 'Self(InCombat|SpellEffects(Plague)|TileFlags(Creep))'
# #         v--------------------------v This part
# b'\x00\x04\x02\x01\x00\x0A\x04\x20\x00\x00\x00'

# # Every possible filter type, some inside self()
# 'InCombat|SpellEffects(Matrix)|WithoutSpellEffects(Blind)|Hangar(LessThan,1)|Self(Order(AttackUnit)|Targeting(Enemy)|TileFlags(Creep|Ramp))|RandomRate(50, 60)|Count(Exactly, 50, 6, 13)|WithoutUnitFlags(Robotic|Hero)'
# b'\x00\x04\x0A\x05\x02\x07\x00\x0A\x0C\x00\x00\x40\x01\x20\x02\x40\x03\x01\x00\x00\x00\x00\x08\x32\x00\x3C\x00\x00\x09\x0A\x32\x00\x06\x00\x0D\x01\x06\x40\x40\x00\x00\x20\x00'

