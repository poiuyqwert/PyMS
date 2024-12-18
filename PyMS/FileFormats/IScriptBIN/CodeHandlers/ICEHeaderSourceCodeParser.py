
from .. import IType
from . import CodeCommands
from .ICELexer import ICELexer
from .ICEParseContext import ICEParseContext

from ....Utilities.CodeHandlers.SourceCodeParser import CommandSourceCodeParser
from ....Utilities.CodeHandlers.ParseContext import ParseContext
from ....Utilities.CodeHandlers import Tokens
from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeBlock import CodeBlock

class ICEHeaderSourceCodeParser(CommandSourceCodeParser):
	def __init__(self) -> None:
		super().__init__()
		self.cmd_defs: dict[str, CodeCommandDefinition] = {}
		for cmd_def in CodeCommands.all_header_commands:
			self.cmd_defs[cmd_def.name] = cmd_def

	def parse(self, parse_context: ParseContext) -> bool:
		from ..IScript import IScript
		assert isinstance(parse_context, ICEParseContext)

		token = parse_context.lexer.skip(Tokens.NewlineToken)
		if not isinstance(token, ICELexer.HeaderToken) or not token.raw_value == '.headerstart':
			return False
		headerstart_line = parse_context.lexer.state.line
		token = parse_context.lexer.next_token()
		if not isinstance(token, Tokens.NewlineToken):
			raise parse_context.error('Parse', "Unexpected token '%s' (expected end of line)" % token.raw_value)
		
		script_id: int | None = None
		script_type: int | None = None
		init: CodeBlock | None = None
		death: CodeBlock | None = None
		gndattkinit: CodeBlock | None = None
		airattkinit: CodeBlock | None = None
		unused1: CodeBlock | None = None
		gndattkrpt: CodeBlock | None = None
		airattkrpt: CodeBlock | None = None
		castspell: CodeBlock | None = None
		gndattktoidle: CodeBlock | None = None
		airattktoidle: CodeBlock | None = None
		unused2: CodeBlock | None = None
		walking: CodeBlock | None = None
		walkingtoidle: CodeBlock | None = None
		specialstate1: CodeBlock | None = None
		specialstate2: CodeBlock | None = None
		almostbuilt: CodeBlock | None = None
		built: CodeBlock | None = None
		landing: CodeBlock | None = None
		liftoff: CodeBlock | None = None
		isworking: CodeBlock | None = None
		workingtoidle: CodeBlock | None = None
		warpin: CodeBlock | None = None
		unused3: CodeBlock | None = None
		stareditinit: CodeBlock | None = None
		disable: CodeBlock | None = None
		burrow: CodeBlock | None = None
		unburrow: CodeBlock | None = None
		enable: CodeBlock | None = None

		commands_parsed: dict[CodeCommandDefinition, int] = {}
		while True:
			token = parse_context.lexer.next_token()
			if isinstance(token, ICELexer.HeaderToken) and token.raw_value == '.headerend':
				break
			if not isinstance(token, Tokens.IdentifierToken):
				raise parse_context.error('Parse', "Expected a script header command, got '%s' instead" % token.raw_value)
			line = parse_context.lexer.state.line
			cmd_def = self.cmd_defs[token.raw_value]
			command = cmd_def.parse(parse_context)
			if command.definition in commands_parsed:
				raise parse_context.error('Parse', f"Duplicate script header command '{command.definition.name}'")
			commands_parsed[command.definition] = line
			if command.definition == CodeCommands.IsId:
				script_id = command.params[0]
			elif command.definition == CodeCommands.Type:
				script_type = command.params[0]
			if command.definition == CodeCommands.Init:
				init = command.params[0]
				if init is None:
					raise parse_context.error('Parse', f"'{command.definition.name}' must refer to a label and not '[NONE]'")
			elif command.definition == CodeCommands.Death:
				death = command.params[0]
			elif command.definition == CodeCommands.Gndattkinit:
				gndattkinit = command.params[0]
			elif command.definition == CodeCommands.Airattkinit:
				airattkinit = command.params[0]
			elif command.definition == CodeCommands.Unused1:
				unused1 = command.params[0]
			elif command.definition == CodeCommands.Gndattkrpt:
				gndattkrpt = command.params[0]
			elif command.definition == CodeCommands.Airattkrpt:
				airattkrpt = command.params[0]
			elif command.definition == CodeCommands.Castspell:
				castspell = command.params[0]
			elif command.definition == CodeCommands.Gndattktoidle:
				gndattktoidle = command.params[0]
			elif command.definition == CodeCommands.Airattktoidle:
				airattktoidle = command.params[0]
			elif command.definition == CodeCommands.Unused2:
				unused2 = command.params[0]
			elif command.definition == CodeCommands.Walking:
				walking = command.params[0]
			elif command.definition == CodeCommands.Walkingtoidle:
				walkingtoidle = command.params[0]
			elif command.definition == CodeCommands.Specialstate1:
				specialstate1 = command.params[0]
			elif command.definition == CodeCommands.Specialstate2:
				specialstate2 = command.params[0]
			elif command.definition == CodeCommands.Almostbuilt:
				almostbuilt = command.params[0]
			elif command.definition == CodeCommands.Built:
				built = command.params[0]
			elif command.definition == CodeCommands.Landing:
				landing = command.params[0]
			elif command.definition == CodeCommands.Liftoff:
				liftoff = command.params[0]
			elif command.definition == CodeCommands.Isworking:
				isworking = command.params[0]
			elif command.definition == CodeCommands.Workingtoidle:
				workingtoidle = command.params[0]
			elif command.definition == CodeCommands.Warpin:
				warpin = command.params[0]
			elif command.definition == CodeCommands.Unused3:
				unused3 = command.params[0]
			elif command.definition == CodeCommands.Stareditinit:
				stareditinit = command.params[0]
			elif command.definition == CodeCommands.Disable:
				disable = command.params[0]
			elif command.definition == CodeCommands.Burrow:
				burrow = command.params[0]
			elif command.definition == CodeCommands.Unburrow:
				unburrow = command.params[0]
			elif command.definition == CodeCommands.Enable:
				enable = command.params[0]

		if script_id is None:
			raise parse_context.error('Parse', f"Header missing '{CodeCommands.IsId.name}' command", line=headerstart_line)
		if script_type is None:
			raise parse_context.error('Parse', f"Header with ID '{script_id}' is missing '{CodeCommands.Type.name}' command", line=headerstart_line)
		all_label_commands = [
			CodeCommands.Init,
			CodeCommands.Death,
			CodeCommands.Gndattkinit,
			CodeCommands.Airattkinit,
			CodeCommands.Unused1,
			CodeCommands.Gndattkrpt,
			CodeCommands.Airattkrpt,
			CodeCommands.Castspell,
			CodeCommands.Gndattktoidle,
			CodeCommands.Airattktoidle,
			CodeCommands.Unused2,
			CodeCommands.Walking,
			CodeCommands.Walkingtoidle,
			CodeCommands.Specialstate1,
			CodeCommands.Specialstate2,
			CodeCommands.Almostbuilt,
			CodeCommands.Built,
			CodeCommands.Landing,
			CodeCommands.Liftoff,
			CodeCommands.Isworking,
			CodeCommands.Workingtoidle,
			CodeCommands.Warpin,
			CodeCommands.Unused3,
			CodeCommands.Stareditinit,
			CodeCommands.Disable,
			CodeCommands.Burrow,
			CodeCommands.Unburrow,
			CodeCommands.Enable,
		]
		entry_point_count = IType.TYPE_TO_ENTRY_POINT_COUNT_MAP[script_type]
		required_label_commands = all_label_commands[:entry_point_count]
		for command_def in required_label_commands:
			if not command_def in commands_parsed:
				raise parse_context.error('Parse', f"Header with ID '{script_id}' is missing '{command_def.name}' command (required for '{CodeCommands.Type.name}' {script_type})", line=headerstart_line)
		invalid_label_commands = all_label_commands[entry_point_count:]
		for command_def in invalid_label_commands:
			if command_def in commands_parsed:
				raise parse_context.error('Parse', f"Header with ID '{script_id}' has extra '{command_def.name}' command (invalid for '{CodeCommands.Type.name}' {script_type})", line=commands_parsed[command_def])

		assert init is not None
		script = IScript(
			id = script_id,
			type = script_type,
			init = init,
			death = death,
			gndattkinit = gndattkinit,
			airattkinit = airattkinit,
			unused1 = unused1,
			gndattkrpt = gndattkrpt,
			airattkrpt = airattkrpt,
			castspell = castspell,
			gndattktoidle = gndattktoidle,
			airattktoidle = airattktoidle,
			unused2 = unused2,
			walking = walking,
			walkingtoidle = walkingtoidle,
			specialstate1 = specialstate1,
			specialstate2 = specialstate2,
			almostbuilt = almostbuilt,
			built = built,
			landing = landing,
			liftoff = liftoff,
			isworking = isworking,
			workingtoidle = workingtoidle,
			warpin = warpin,
			unused3 = unused3,
			stareditinit = stareditinit,
			disable = disable,
			burrow = burrow,
			unburrow = unburrow,
			enable = enable,
		)
		for entry_point,_ in script.get_entry_points():
			parse_context.add_block_owner(entry_point, script)
		parse_context.scripts[script_id] = (script, line)

		return True
