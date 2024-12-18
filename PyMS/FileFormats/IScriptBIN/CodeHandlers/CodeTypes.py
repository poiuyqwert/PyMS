
from .. import IType
from .ICESerializeContext import ICESerializeContext
from .ICEParseContext import ICEParseContext
from .ICELexer import ICELexer

from ....Utilities.CodeHandlers import CodeType
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock
from ....Utilities.CodeHandlers.SerializeContext import SerializeContext
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers.ByteCodeCompiler import ByteCodeBuilderType
from ....Utilities.CodeHandlers import Tokens
from ....Utilities import Struct
from ....Utilities.PyMSError import PyMSError
# from ....Utilities.PyMSWarning import PyMSWarning
from ....Utilities import Assets

from typing import cast, Sequence

class FrameCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Frame', 'The index of a frame in a GRP, in decimal or hexadecimal (number in the range 0 to 65535. framesets are increments of 17, so 17 or 0x11, 34 or 0x22, 51 or 0x33, etc.)', Struct.l_u16, allow_hex=True)

	def serialize(self, value: int, context: SerializeContext) -> str:
		if context.definitions:
			variable = context.definitions.lookup_variable(value, self)
			if variable:
				return variable.name
		if value % 17:
			return str(value)
		return f'0x{value:02X}'

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if not value % 17:
			return f'Frame set {value // 17}'
		if value > 17:
			return f'Frame set {value // 17}, direction {value % 17}'
		return None

	def validate(self, num: int, parse_context: ParseContext, token: str | None = None) -> None:
		# TODO: Check against GRP frames
		# if bin and bin.grpframes and v > bin.grpframes:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frame for one or more of the GRP's specified in the header, and may cause a crash (max frame value is %s, or frameset 0x%02x)" % (data, bin.grpframes, (bin.grpframes - 17) // 17 * 17),extra=v)
		# if bin and bin.grpframes and v > bin.grpframes - 17:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frame value is %s, or frameset 0x%02x)" % (data, bin.grpframes , (bin.grpframes - 17) // 17 * 17),extra=v)
		try:
			return super().validate(num, parse_context, token)
		except:
			raise PyMSError('Parse', f"Invalid Frame value '{num}', it must be a number in the range 0 to 65535 in decimal or hexidecimal (framesets are increments of 17: 17 or 0x11, 34 or 0x22, 51 or 0x33, etc.)")

class FramesetCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Frameset', 'The index of a frame set in a GRP (number in the range 0 to 255)', Struct.l_u8)

	def validate(self, num: int, parse_context: ParseContext, token: str | None = None) -> None:
		# TODO: Check against GRP frames
		# if bin and bin.grpframes and v*17 > bin.grpframes:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frameset value is %s)" % (data, (bin.grpframes - 17) // 17),extra=v)
		# if bin and bin.grpframes and v*17 > bin.grpframes - 17:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frameset value is %s)" % (data, (bin.grpframes - 17) // 17),extra=v)
		return super().validate(num, parse_context, token)

class BFrameCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('BFrame', 'The index of a frame in a GRP (number in the range 0 to 255)', Struct.l_u8)

	def validate(self, num: int, parse_context: ParseContext, token: str | None = None) -> None:
		# TODO: Check against GRP frames
		# if bin and bin.grpframes and v*17 > bin.grpframes:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frameset value is %s)" % (data, (bin.grpframes - 17) // 17),extra=v)
		# if bin and bin.grpframes and v*17 > bin.grpframes - 17:
		# 	raise PyMSWarning('Parameter',"'%s' is an invalid frameset for one or more of the GRP's specified in the header, and may cause a crash (max frameset value is %s)" % (data, (bin.grpframes - 17) // 17),extra=v)
		return super().validate(num, parse_context, token)

class ByteCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Byte', 'A number in the range 0 to 255', Struct.l_u8)

class SByteCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('SByte', 'A number in the range -128 to 127', Struct.l_s8)

class LabelCodeType(CodeType.AddressCodeType):
	def __init__(self) -> None:
		super().__init__('Label', 'A label name of a block in the script', Struct.l_u16)

class ImageIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('ImageID', 'The ID of an images.dat entry', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if isinstance(context, ICESerializeContext):
			return context.data_context.image_name(value)
		return super().comment(value, context)

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if isinstance(parse_context, ICEParseContext):
			return (0, parse_context.data_context.images_entry_count - 1)
		return super().get_limits(parse_context)

class SpriteIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('SpriteID', 'The ID of a sprites.dat entry', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if isinstance(context, ICESerializeContext):
			return context.data_context.sprite_name(value)
		return super().comment(value, context)

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if isinstance(parse_context, ICEParseContext) and parse_context.data_context.sprites_dat is not None:
			return (0, parse_context.data_context.sprites_entry_count - 1)
		return super().get_limits(parse_context)

class FlingyIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('FlingyID', 'The ID of a flingy.dat entry', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if isinstance(context, ICESerializeContext):
			return context.data_context.flingy_name(value)
		return super().comment(value, context)

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if isinstance(parse_context, ICEParseContext) and parse_context.data_context.flingy_dat is not None:
			return (0, parse_context.data_context.flingy_entry_count - 1)
		return super().get_limits(parse_context)

class OverlayIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		# TODO: Limits and validation?
		super().__init__('OverlayID', 'The ID of an overlay', Struct.l_u8)

class FlipStateCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('FlipState', 'The flip state to set on the current image overlay', Struct.l_u8)

class SoundIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('SoundID', 'The ID of a sfxdata.dat entry', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if isinstance(context, ICESerializeContext):
			return context.data_context.sound_name(value)
		return super().comment(value, context)

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if isinstance(parse_context, ICEParseContext) and parse_context.data_context.sounds_dat is not None:
			return (0, parse_context.data_context.sounds_entry_count - 1)
		return super().get_limits(parse_context)

class SoundsCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Sounds', 'How many sounds to pick from', Struct.l_u8, param_repeater=True)

class SignalIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('SignalID', 'A signal order ID', Struct.l_u8)

class WeaponCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Weapon', 'Either 1 for ground attack, or not 1 for air attack', Struct.l_u8)

class WeaponIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('WeaponID', 'The ID of a weapons.dat entry', Struct.l_u8)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if isinstance(context, ICESerializeContext):
			return context.data_context.weapon_name(value)
		return super().comment(value, context)

	def get_limits(self, parse_context: ParseContext) -> tuple[int, int]:
		if isinstance(parse_context, ICEParseContext) and parse_context.data_context.weapons_dat is not None:
			return (0, parse_context.data_context.weapons_entry_count - 1)
		return super().get_limits(parse_context)

class SpeedCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Speed', 'The speed to set on the flingy.dat entry of the current flingy', Struct.l_u16)

class GasOverlayCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		# TODO: Limits and validation?
		super().__init__('GasOverlay', 'The ID of a gas overlay', Struct.l_u8)

class ShortCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Short', 'A number in the range 0 to 65535', Struct.l_u16)

all_basic_types: list[CodeType.CodeType] = [
	FrameCodeType(),
	FramesetCodeType(),
	BFrameCodeType(),
	ByteCodeType(),
	SByteCodeType(),
	LabelCodeType(),
	ImageIDCodeType(),
	SpriteIDCodeType(),
	FlingyIDCodeType(),
	OverlayIDCodeType(),
	FlipStateCodeType(),
	SoundIDCodeType(),
	SoundsCodeType(),
	SignalIDCodeType(),
	WeaponCodeType(),
	WeaponIDCodeType(),
	SpeedCodeType(),
	GasOverlayCodeType(),
	ShortCodeType(),
]

class HeaderIDCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('ID', 'The iscript id of an animation set which is referenced by images.dat, each set has a unique id', Struct.l_u16)

	def comment(self, value: int, context: SerializeContext) -> str | None:
		if value < len(Assets.data_cache(Assets.DataReference.IscriptIDList)):
			return Assets.data_cache(Assets.DataReference.IscriptIDList)[value]
		return f'UnknownScript{value}'

class HeaderTypeCodeType(CodeType.IntCodeType):
	def __init__(self) -> None:
		super().__init__('Type', 'The type of animation header. There are 28 different types, each with a different number of animations', Struct.l_u16)

	def validate(self, num: int, parse_context: ParseContext, token: str | None = None) -> None:
		if not num in IType.TYPE_TO_ENTRY_POINT_COUNT_MAP:
			raise PyMSError('Parse', f'Invalid Type value, must be one of the numbers: {", ".join(str(type) for type in IType.TYPE_TO_ENTRY_POINT_COUNT_MAP.keys())}')

class HeaderLabelCodeType(CodeType.CodeType[CodeBlock | None, CodeBlock | None], CodeType.HasKeywords):
	def __init__(self) -> None:
		super().__init__('HeaderLabel', 'A label name of a block in the script, or [NONE]', Struct.l_u16, True)

	def compile(self, block: CodeBlock | None, context: ByteCodeBuilderType) -> None:
		type = cast(Struct.IntField, self._bytecode_type)
		if block:
			context.add_block_ref(block, type)
		else:
			context.add_data(type.pack(0))

	def serialize(self, block: CodeBlock | None, context: SerializeContext) -> str:
		if block:
			return context.strategy.block_label(block)
		else:
			return '[NONE]'

	def lex(self, parse_context: ParseContext) -> CodeBlock | None:
		token = parse_context.lexer.next_token()
		if not isinstance(token, (Tokens.IdentifierToken, ICELexer.NoneToken)):
			raise parse_context.error('Parse', "Expected block label identifier or '[NONE]' but got '%s'" % token.raw_value)
		if token.raw_value == '[NONE]':
			return None
		return parse_context.get_block(token.raw_value)

	def keywords(self) -> Sequence[str]:
		return ('[NONE]',)

all_header_types = [
	HeaderIDCodeType(),
	HeaderTypeCodeType(),
	HeaderLabelCodeType(),
]
