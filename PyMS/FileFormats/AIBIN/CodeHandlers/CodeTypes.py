
from . import WarningID
from .AISerializeContext import AISerializeContext
from .AIParseContext import AIParseContext

from ....FileFormats.DAT.UnitsDAT import DATUnit

from ....Utilities.CodeHandlers import CodeType
from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Lexer
from ....Utilities.CodeHandlers import Tokens

from ....Utilities import Struct
from ....Utilities.PyMSError import PyMSError
from ....Utilities.PyMSWarning import PyMSWarning


class ByteCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'byte', 'A number in the range 0 to 255', Struct.l_u8)

class WordCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'word', 'A number in the range 0 to 65535', Struct.l_u16)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (WordCodeType, ByteCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match type(other_type):
			case WordCodeType():
				return 2
			case ByteCodeType():
				return 1
			case _:
				return 0

class DWordCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'dword', 'A number in the range 0 to 4294967295', Struct.l_u32)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (DWordCodeType, WordCodeType, ByteCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case DWordCodeType():
				return 3
			case WordCodeType():
				return 2
			case ByteCodeType():
				return 1
			case _:
				return 0
class BlockCodeType(CodeType.AddressCodeType):
	def __init__(self) -> None:
		CodeType.AddressCodeType.__init__(self, 'block', 'The label name of a block in the code', Struct.l_u16)

class UnitCodeType(CodeType.IntCodeType):
	def __init__(self, name: str = 'unit', help_text: str = 'A unit ID from 0 to 227 (or higher if using expanded DAT file), or a full unit name from stat_txt.tbl') -> None:
		CodeType.IntCodeType.__init__(self, name, help_text, bytecode_type=Struct.l_u16)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (UnitCodeType, BuildingCodeType, MilitaryCodeType, GGMilitaryCodeType, AGMilitaryCodeType, GAMilitaryCodeType, AAMilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, UnitCodeType)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if isinstance(context, AISerializeContext) and context.data_context:
			name = context.data_context.unit_name(value)
			if name:
				return StringCodeType.serialize_string(name)
		return str(value)

	def lex_token(self, parse_context: ParseContext) -> str:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			rollback = parse_context.lexer.get_rollback()
			unit_name: str | None = None
			token: Tokens.Token | None = parse_context.lexer.get_token(Tokens.StringToken)
			if token:
				unit_name = CodeType.StrCodeType.parse_string(token.raw_value)
			elif parse_context.command_in_parens:
				token = parse_context.lexer.read_open_string(lambda token: Lexer.Stop.exclude if token.raw_value == ',' or token.raw_value == ')' else Lexer.Stop.proceed)
				unit_name = token.raw_value
			if unit_name is not None and parse_context.data_context.unit_id(unit_name) is not None:
				return unit_name
			parse_context.lexer.rollback(rollback)
		return super().lex_token(parse_context)

	def parse_token(self, token: str, parse_context: ParseContext) -> int:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			unit_id = parse_context.data_context.unit_id(token)
			if unit_id is not None:
				return unit_id
		return super().parse_token(token, parse_context)

	def validate(self, num: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		token = token or str(num)
		if num < 0:
			raise PyMSError('Parameter', f"Unit '{token}' is not a valid unit")
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if num > parse_context.data_context.units_dat.entry_count():
			raise PyMSError('Parameter', f"Unit '{token}' is not a valid unit")

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		entry_count = 227
		if isinstance(parse_context, AIParseContext) and parse_context.data_context.units_dat is not None:
			entry_count = parse_context.data_context.units_dat.entry_count()
		return (0, entry_count)

class BuildingCodeType(UnitCodeType):
	def __init__(self) -> None:
		UnitCodeType.__init__(self, 'building', 'Same as unit type, but only units that are Buildings, Resource Miners, and Overlords')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(self, BuildingCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case BuildingCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if unit_id == 42: # Overlord
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if (entry.special_ability_flags & DATUnit.SpecialAbilityFlag.building) or (entry.special_ability_flags & DATUnit.SpecialAbilityFlag.resource_miner):
			return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' is not a building, resource miner, or Overlord", level=1, id=WarningID.building))

class MilitaryCodeType(UnitCodeType):
	def __init__(self, name: str = 'military', help_text: str = 'Same as unit type, but only for a unit to train (not a Building, Resource Miners, or Overlords)') -> None:
		UnitCodeType.__init__(self, name, help_text)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (MilitaryCodeType, GGMilitaryCodeType, AGMilitaryCodeType, GAMilitaryCodeType, AAMilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if not (entry.special_ability_flags & DATUnit.SpecialAbilityFlag.building):
			return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' Unit is a building", level=1, id=WarningID.military))

class GGMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'gg_military', 'Same as Military type, but only for defending against an enemy Ground unit attacking your Ground unit')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (GGMilitaryCodeType, GAMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case GGMilitaryCodeType():
				return 4
			case GAMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if unit_id in parse_context.spellcasters:
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if entry.ground_weapon != 130 or entry.attack_unit in (53,59):
			return
		if entry.subunit1 is not None and entry.subunit1 != 228:
			subunit_entry = parse_context.data_context.units_dat.get_entry(entry.subunit1)
			if subunit_entry.ground_weapon != 130 or subunit_entry.attack_unit in (53,59):
				return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' has no ground weapon, and is not marked as a @spellcaster", level=1, id=WarningID.gg_military))

class AGMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'ag_military', 'Same as Military type, but only for defending against an enemy Air unit attacking your Ground unit')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (AGMilitaryCodeType, AAMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case AGMilitaryCodeType():
				return 4
			case AAMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if unit_id in parse_context.spellcasters:
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if entry.air_weapon != 130 or entry.attack_unit != 53:
			return
		if entry.subunit1 is not None and entry.subunit1 != 228:
			subunit_entry = parse_context.data_context.units_dat.get_entry(entry.subunit1)
			if subunit_entry.air_weapon != 130 or subunit_entry.attack_unit != 53:
				return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' has no air weapon, and is not marked as a @spellcaster", level=1, id=WarningID.ag_military))

class GAMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'ga_military', 'Same as Military type, but only for defending against an enemy Ground unit attacking your Air unit')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (GAMilitaryCodeType, GGMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case GAMilitaryCodeType():
				return 4
			case GGMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if unit_id in parse_context.spellcasters:
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if entry.ground_weapon != 130 or entry.attack_unit in (53,59):
			return
		if entry.subunit1 is not None and entry.subunit1 != 228:
			subunit_entry = parse_context.data_context.units_dat.get_entry(entry.subunit1)
			if subunit_entry.ground_weapon != 130 or subunit_entry.attack_unit in (53,59):
				return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' has no ground weapon, and is not marked as a @spellcaster", level=1, id=WarningID.ga_military))

class AAMilitaryCodeType(MilitaryCodeType):
	def __init__(self) -> None:
		MilitaryCodeType.__init__(self, 'aa_military', 'Same as Military type, but only for defending against an enemy Air unit attacking your Air unit')

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, (AAMilitaryCodeType, AGMilitaryCodeType, MilitaryCodeType))

	def compatible(self, other_type: CodeType.CodeType) -> int:
		match other_type:
			case AAMilitaryCodeType():
				return 4
			case AGMilitaryCodeType():
				return 3
			case MilitaryCodeType():
				return 2
			case UnitCodeType():
				return 1
			case _:
				return 0

	def validate(self, unit_id: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		UnitCodeType.validate(self, unit_id, parse_context, token)
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.units_dat is None:
			return
		if unit_id in parse_context.spellcasters:
			return
		entry = parse_context.data_context.units_dat.get_entry(unit_id)
		if entry.air_weapon != 130 or entry.attack_unit != 53:
			return
		if entry.subunit1 is not None and entry.subunit1 != 228:
			subunit_entry = parse_context.data_context.units_dat.get_entry(entry.subunit1)
			if subunit_entry.air_weapon != 130 or subunit_entry.attack_unit != 53:
				return
		parse_context.add_warning(PyMSWarning('Parameter', f"Unit '{token or unit_id}' has no air weapon, and is not marked as a @spellcaster", level=1, id=WarningID.aa_military))

class UpgradeCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'upgrade', 'An upgrade ID from 0 to 60 (or higher if using expanded DAT file), or a full upgrade name from stat_txt.tbl', Struct.l_u16)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, UpgradeCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, UpgradeCodeType)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if isinstance(context, AISerializeContext) and context.data_context:
			name = context.data_context.upgrade_name(value)
			if name:
				return StringCodeType.serialize_string(name)
		return str(value)

	def lex_token(self, parse_context: ParseContext) -> str:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			rollback = parse_context.lexer.get_rollback()
			upgrade_name: str | None = None
			token: Tokens.Token | None = parse_context.lexer.get_token(Tokens.StringToken)
			if token:
				upgrade_name = CodeType.StrCodeType.parse_string(token.raw_value)
			elif parse_context.command_in_parens:
				token = parse_context.lexer.read_open_string(lambda token: Lexer.Stop.exclude if token.raw_value == ',' or token.raw_value == ')' else Lexer.Stop.proceed)
				upgrade_name = token.raw_value
			if upgrade_name is not None and parse_context.data_context.upgrade_id(upgrade_name) is not None:
				return upgrade_name
			parse_context.lexer.rollback(rollback)
		return super().lex_token(parse_context)

	def parse_token(self, token: str, parse_context: ParseContext) -> int:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			upgrade_id = parse_context.data_context.upgrade_id(token)
			if upgrade_id is not None:
				return upgrade_id
		return super().parse_token(token, parse_context)

	def validate(self, num: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		token = token or str(num)
		if num < 0:
			raise PyMSError('Parameter', f"Upgrade '{token}' is not a valid upgrade")
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.upgrades_dat is None:
			return
		if num > parse_context.data_context.upgrades_dat.entry_count():
			raise PyMSError('Parameter', f"Upgrade '{token}' is not a valid upgrade")

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		entry_count = 60
		if isinstance(parse_context, AIParseContext) and parse_context.data_context.upgrades_dat is not None:
			entry_count = parse_context.data_context.upgrades_dat.entry_count()
		return (0, entry_count)

class TechnologyCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'technology', 'An technology ID from 0 to 43 (or higher if using expanded DAT file), or a full technology name from stat_txt.tbl', Struct.l_u16)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, TechnologyCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, TechnologyCodeType)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if isinstance(context, AISerializeContext) and context.data_context:
			name = context.data_context.technology_name(value)
			if name:
				return StringCodeType.serialize_string(name)
		return str(value)

	def lex_token(self, parse_context: ParseContext) -> str:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			rollback = parse_context.lexer.get_rollback()
			technology_name: str | None = None
			token: Tokens.Token | None = parse_context.lexer.get_token(Tokens.StringToken)
			if token:
				technology_name = CodeType.StrCodeType.parse_string(token.raw_value)
			elif parse_context.command_in_parens:
				token = parse_context.lexer.read_open_string(lambda token: Lexer.Stop.exclude if token.raw_value == ',' or token.raw_value == ')' else Lexer.Stop.proceed)
				technology_name = token.raw_value
			if technology_name is not None and parse_context.data_context.technology_id(technology_name) is not None:
				return technology_name
			parse_context.lexer.rollback(rollback)
		return super().lex_token(parse_context)

	def parse_token(self, token: str, parse_context: ParseContext) -> int:
		if isinstance(parse_context, AIParseContext) and parse_context.data_context:
			technology_id = parse_context.data_context.technology_id(token)
			if technology_id is not None:
				return technology_id
		return super().parse_token(token, parse_context)

	def validate(self, num: int, parse_context: ParseContext | None, token: str | None = None) -> None:
		token = token or str(num)
		if num < 0:
			raise PyMSError('Parameter', f"Technology '{token}' is not a valid technology")
		if not isinstance(parse_context, AIParseContext) or parse_context.data_context.techdata_dat is None:
			return
		if num > parse_context.data_context.techdata_dat.entry_count():
			raise PyMSError('Parameter', f"Technology '{token}' is not a valid technology")

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		entry_count = 43
		if isinstance(parse_context, AIParseContext) and parse_context.data_context.techdata_dat is not None:
			entry_count = parse_context.data_context.techdata_dat.entry_count()
		return (0, entry_count)

class StringCodeType(CodeType.StrCodeType):
	def __init__(self) -> None:
		CodeType.StrCodeType.__init__(self, 'string', "A string of any characters (except for nulls: <0>) in TBL string formatting (use <40> for an open parenthesis '(', <41> for a close parenthesis ')', and <44> for a comma ',')")

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, StringCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, StringCodeType)

class CompareCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		cases = {
			'GreaterThan': 1,
			'LessThan': 0
		}
		CodeType.EnumCodeType.__init__(self, 'compare', 'Either LessThan or GreaterThan', Struct.l_u8, cases)

	def accepts(self, other_type: CodeType.CodeType) -> bool:
		return isinstance(other_type, CompareCodeType)

	def compatible(self, other_type: CodeType.CodeType) -> int:
		return isinstance(other_type, CompareCodeType)

all_basic_types: list[CodeType.CodeType] = [
	ByteCodeType(),
	WordCodeType(),
	DWordCodeType(),
	BlockCodeType(),
	UnitCodeType(),
	BuildingCodeType(),
	MilitaryCodeType(),
	GGMilitaryCodeType(),
	GAMilitaryCodeType(),
	AGMilitaryCodeType(),
	AAMilitaryCodeType(),
	UpgradeCodeType(),
	TechnologyCodeType(),
	StringCodeType(),
	CompareCodeType(),
]

# Types used by header

class TBLStringCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		CodeType.IntCodeType.__init__(self, 'tbl_string', 'Index of a string in stat_txt.tbl', Struct.l_u32)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if not isinstance(context, AISerializeContext):
			return None
		return context.data_context.stattxt_string(value)

class BinFileCodeType(CodeType.EnumCodeType):
	def __init__(self) -> None:
		cases = {
			'aiscript': 0,
			'bwscript': 1
		}
		CodeType.EnumCodeType.__init__(self, 'bin_file', 'Either aiscript or bwscript', Struct.l_u8, cases) # TODO: bytecode_type

class BoolCodeType(CodeType.BooleanCodeType):
	def __init__(self) -> None:
		CodeType.BooleanCodeType.__init__(self, 'bool', 'A value of either true/1 or false/0', Struct.l_u8) # TODO: bytecode_type

all_header_types: list[CodeType.CodeType] = [
	TBLStringCodeType(),
	BinFileCodeType(),
	BoolCodeType(),
]
