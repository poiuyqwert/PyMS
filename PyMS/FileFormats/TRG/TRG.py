
from .Trigger import Trigger
from .UnitProperties import UnitProperties, properties_definitions, PropertyFieldDefinition, PropertyStateDefinition
from .Constants import ConditionType, ConditionFlag, ActionType, ActionFlag
from .CodeHandler import TRGLexer
from .Parameters import PlayerParameter, PlayerGroup
from . import Conditions
from . import Actions
from .Condition import Condition

from ...FileFormats import TBL
from ...FileFormats.AIBIN import AIBIN

from ...Utilities import IO
from ...Utilities.PyMSError import PyMSError
from ...Utilities.PyMSWarning import PyMSWarning
from ...Utilities.BytesScanner import BytesScanner
from ...Utilities import Struct
from ...Utilities.CodeHandlers import Tokens
from ...Utilities.CodeHandlers.Lexer import Stop

import enum, re

class Format(enum.Enum):
	normal = 0
	briefing = 1
	got = 2

class TRG:
	HEADER = b'qw\x986\x18\x00\x00\x00'

	def __init__(self, stat_txt: TBL.TBL | None = None, aiscript: AIBIN.AIBIN | None = None) -> None:
		self.triggers: list[Trigger] = []
		self.strings: dict[int, str] = {}
		self.unit_properties: dict[int, UnitProperties] = {}
		self.format = Format.normal

		self.stat_txt: TBL.TBL | None = stat_txt
		self.aiscript: AIBIN.AIBIN | None = aiscript

	STRING_STRUCT = Struct.l_str(2048)
	def load(self, input: IO.AnyInputBytes, format: Format = Format.normal) -> None:
		with IO.InputBytes(input) as f:
			data = f.read()
		scanner = BytesScanner(data)
		if format != Format.got and not scanner.matches(TRG.HEADER):
			raise PyMSError('Load', 'Not a valid .trg file (missing header), could possibly be a GOT .trg file')
		triggers: list[Trigger] = []
		strings: dict[int, str] = {}
		unit_properties: dict[int, UnitProperties] = {}
		try:
			while not scanner.at_end():
				trigger = scanner.scan(Trigger)
				triggers.append(trigger)
				if format != Format.got:
					for action in trigger.actions:
						if action.string_index:
							strings[action.string_index] = scanner.scan(TRG.STRING_STRUCT)
						if action.flags & ActionFlag.unit_property_used:
							props = scanner.scan(UnitProperties)
							unit_properties[action.unit_properties_index] = props
		except Exception as e:
			raise PyMSError('Load', 'Unsupported TRG file, could possibly be corrupt')
		self.triggers = triggers
		self.strings = strings
		self.unit_properties = unit_properties
		self.format = format

	def save(self, output: IO.AnyOutputBytes, format: Format | None = None) -> list[PyMSWarning]:
		save_format = self.format if format is None else format
		warnings: list[PyMSWarning] = []
		is_missiong_briefing: bool | None = None
		with IO.OutputBytes(output) as f:
			if save_format != Format.got:
				f.write(TRG.HEADER)
			for trigger in self.triggers:
				f.write(trigger.pack())
				if is_missiong_briefing is None:
					is_missiong_briefing = trigger.is_missing_briefing
				elif trigger.is_missing_briefing != is_missiong_briefing:
					warnings.append(PyMSWarning('Save', 'There is a mix of missing briefing and normal triggers'))
				for action in trigger.actions:
					if action.string_index:
						string: str
						if action.string_index in self.strings:
							string = self.strings[action.string_index]
						else:
							string = ''
							warnings.append(PyMSWarning('Save', f'String {action.string_index} is missing, saving an empty string'))
						f.write(TRG.STRING_STRUCT.pack(string))
					if action.flags & ActionFlag.unit_property_used:
						properties: UnitProperties
						if action.flags & ActionFlag.unit_property_used:
							properties = self.unit_properties[action.unit_properties_index]
						else:
							properties = UnitProperties()
							warnings.append(PyMSWarning('Save', f'Unit properties {action.unit_properties_index} is missing, saving empty properties'))
						f.write(properties.pack())
		return warnings

	RE_NEWLINES = re.compile(r'(\r\n|\r|\n)')
	def decompile(self, output: IO.AnyOutputText, reference: bool = False) -> None:
		with IO.OutputText(output) as f:
			for string_index,raw_string in self.strings.items():
				string = TRG.RE_NEWLINES.sub('\\1  ', TBL.decompile_string(raw_string, '\r\n'))
				f.write(f'String({string_index}):\n  {string}\n\n')
			for properties_index,properties in self.unit_properties.items():
				properties.decompile(properties_index + 1, f)
				f.write('\n\n')
			for trigger in self.triggers:
				trigger.decompile(self, f)
				f.write('\n\n')

	# TODO: Compile
	def compile(self, input: IO.AnyInputText) -> list[PyMSWarning]:
		with IO.InputText(input) as f:
			code = f.read()
		format: Format | None = None
		triggers: list[Trigger] = []
		strings: dict[int, str] = {}
		unit_properties: dict[int, UnitProperties] = {}
		warnings: list[PyMSWarning] = []

		lexer = TRGLexer(code)

		def process_conditions(trigger: Trigger) -> Tokens.Token:
			nonlocal warnings
			token = lexer.skip(Tokens.NewlineToken)
			while trigger.conditions_free:
				enabled = True
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == '-':
					enabled = False
					token = lexer.next_token()
				if not isinstance(token, Tokens.IdentifierToken):
					raise PyMSError('Compile', f"Expected a condition, got '{token.raw_value}' instead", lexer.line)
				definition = Conditions.get_definition_named(token.raw_value)
				if not definition:
					raise PyMSError('Compile', f"Unknown condition name '{token.raw_value}'", lexer.line)
				token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
					raise PyMSError('Compile', f"Expected '(' to start parameters, got '{token.raw_value}' instead", lexer.line)
				condition = definition.new_condition()
				if not enabled:
					condition.flags |= ConditionFlag.disabled
				token = lexer.check_token(TRGLexer.ParameterToken)
				for parameter in definition.parameters:
					if not isinstance(token, TRGLexer.ParameterToken):
						raise PyMSError('Compile', f"Expected a '{parameter.name()}' parameter, got '{token.raw_value}' instead", lexer.line)
					try:
						if warning := parameter.condition_compile(token.raw_value, condition, self):
							warnings.append(warning)
					except PyMSError as e:
						e.line = lexer.line
						raise e
					except:
						raise PyMSError('Compile', f"Couldn't parse '{token.raw_value}' as parameter", lexer.line)
					token = lexer.next_token()
					if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
						token = lexer.check_token(TRGLexer.ParameterToken)
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
					raise PyMSError('Compile', f"Expected ')' to end parameters, got '{token.raw_value}' instead", lexer.line)
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', f"Expected end of line, got '{token.raw_value}' instead", lexer.line)
				if condition.condition_type != ConditionType.no_condition:
					trigger.add_condition(condition)
				token = lexer.skip(Tokens.NewlineToken)
				if isinstance(token, TRGLexer.KeywordsToken):
					break
			return token

		def process_actions(trigger: Trigger) -> Tokens.Token:
			nonlocal warnings
			token = lexer.skip(Tokens.NewlineToken)
			while trigger.actions_free:
				enabled = True
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == '-':
					enabled = False
					token = lexer.next_token()
				if not isinstance(token, Tokens.IdentifierToken):
					raise PyMSError('Compile', f"Expected an action, got '{token.raw_value}' instead", lexer.line)
				definition = Actions.get_definition_named(token.raw_value)
				if not definition:
					raise PyMSError('Compile', f"Unknown action name '{token.raw_value}'", lexer.line)
				token = lexer.next_token()
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
					raise PyMSError('Compile', f"Expected '(' to start parameters, got '{token.raw_value}' instead", lexer.line)
				action = definition.new_action()
				if not enabled:
					action.flags |= ActionFlag.disabled
				token = lexer.check_token(TRGLexer.ParameterToken)
				for parameter in definition.parameters:
					if not isinstance(token, TRGLexer.ParameterToken):
						raise PyMSError('Compile', f"Expected a '{parameter.name()}' parameter, got '{token.raw_value}' instead", lexer.line)
					try:
						if warning := parameter.action_compile(token.raw_value, action, self):
							warnings.append(warning)
					except PyMSError as e:
						e.line = lexer.line
						raise e
					except:
						raise PyMSError('Compile', f"Couldn't parse '{token.raw_value}' as parameter", lexer.line)
					token = lexer.next_token()
					if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
						token = lexer.check_token(TRGLexer.ParameterToken)
				if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
					raise PyMSError('Compile', f"Expected ')' to end parameters, got '{token.raw_value}' instead", lexer.line)
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', f"Expected end of line, got '{token.raw_value}' instead", lexer.line)
				if action.action_type != ActionType.no_action:
					trigger.add_action(action)
				token = lexer.skip(Tokens.NewlineToken)
				if isinstance(token, (TRGLexer.KeywordsToken, Tokens.EOFToken)):
					break
			return token

		def process_trigger() -> Tokens.Token:
			nonlocal triggers
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
				raise PyMSError('Compile', "Expected a '(' to start the list of players for trigger", lexer.line)
			trigger = Trigger()
			triggers.append(trigger)
			player_param = PlayerParameter()
			token = lexer.check_token(TRGLexer.ParameterToken)
			found_players = False
			while isinstance(token, TRGLexer.ParameterToken):
				try:
					player = player_param._compile(token.raw_value)
				except PyMSError as e:
					e.line = lexer.line
					raise e
				except:
					raise PyMSError('Compile', f"Couldn't parse '{token.raw_value}' as parameter", lexer.line)
				if player > PlayerGroup.non_allied_victory_players:
					raise PyMSError('Compile', f"'{token.raw_value}' is an invalid player for a trigger", lexer.line)
				if trigger.execution.player_groups[player]:
					raise PyMSError('Compile', f"'{token.raw_value}' already specified for trigger", lexer.line)
				trigger.execution.player_groups[player] = 1
				found_players = True
				token = lexer.next_token()
				if isinstance(token, TRGLexer.SymbolToken) and token.raw_value == ',':
					token = lexer.check_token(TRGLexer.ParameterToken)
			if not found_players:
				warnings.append(PyMSWarning('Trigger', 'There are no player groups applied to trigger', lexer.line))
				# raise PyMSError('Compile', f"Expected player for trigger, got '{token.raw_value}' instead", lexer.line)
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', f"Expected ')' to end player list, got '{token.raw_value}' instead", lexer.line)
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', f"Expected ':' to start trigger body", lexer.line)
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', f"Expected end of line, got '{token.raw_value}' instead", lexer.line)
			token = lexer.skip(Tokens.NewlineToken)
			if format == Format.normal:
				if not isinstance(token, TRGLexer.KeywordsToken) or token.raw_value != 'Conditions:':
					raise PyMSError('Compile', f"Expected 'Conditions:' to start list of conditions", lexer.line)
				token = lexer.next_token()
				if not isinstance(token, Tokens.NewlineToken):
					raise PyMSError('Compile', f"Expected end of line, got '{token.raw_value}' instead", lexer.line)
				token = process_conditions(trigger)
			else:
				trigger.add_condition(Condition.mission_briefing())
			if not isinstance(token, TRGLexer.KeywordsToken) or token.raw_value != 'Actions:':
				raise PyMSError('Compile', f"Expected 'Actions:' to start list of actions", lexer.line)
			token = process_actions(trigger)
			return token

		def process_string():
			nonlocal strings
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
				raise PyMSError('Compile', "Expected a '(' to start the string id", lexer.line)
			id_token = lexer.get_token(Tokens.IntegerToken)
			if not id_token:
				raise PyMSError('Compile', 'Expected a numeric string id', lexer.line)
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', f"Expected ')' to end string id, got '{token.raw_value}' instead", lexer.line)
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', f"Expected ':' to start string definition", lexer.line)
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', f"Expected end of line, got '{token.raw_value}' instead", lexer.line)
			string_id = int(id_token.raw_value)
			if string_id in strings:
				raise PyMSError('Compile', f"String with id {string_id} already defined", lexer.line)
			string = ''
			indent_token = lexer.get_token(Tokens.WhitespaceToken)
			if not indent_token:
				raise PyMSError('Compile', 'Expected indentation for string', lexer.line)
			while True:
				string_token = lexer.read_open_string(lambda token: Stop.include if isinstance(token, Tokens.NewlineToken) else Stop.proceed)
				whitespace_token = lexer.get_token(Tokens.WhitespaceToken)
				if not whitespace_token or not whitespace_token.raw_value.startswith(indent_token.raw_value):
					string += string_token.raw_value.rstrip('\r\n')
					break
				string += string_token.raw_value
			strings[string_id] = string

		def process_properties() -> Tokens.Token:
			nonlocal unit_properties
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
				raise PyMSError('Compile', "Expected a '(' to start the unit properties id", lexer.line)
			id_token = lexer.get_token(Tokens.IntegerToken)
			if not id_token:
				raise PyMSError('Compile', 'Expected a properties id', lexer.line)
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
				raise PyMSError('Compile', 'Expected closing parenthesis', lexer.line)
			token = lexer.next_token()
			if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ':':
				raise PyMSError('Compile', 'Expected start of properties', lexer.line)
			token = lexer.next_token()
			if not isinstance(token, Tokens.NewlineToken):
				raise PyMSError('Compile', 'Expected end of line', lexer.line)
			properties_id = int(id_token.raw_value) - 1
			if properties_id < 0 or properties_id > 63:
				raise PyMSError('Compile', 'Properties id is not valid', lexer.line)
			if properties_id in unit_properties:
				raise PyMSError('Compile', 'Properties with id already defined', lexer.line)
			properties = UnitProperties()
			token = lexer.next_token()
			property_found = False
			while isinstance(token, Tokens.IdentifierToken):
				for definition in properties_definitions:
					if token.raw_value == definition.name:
						if isinstance(definition, PropertyFieldDefinition):
							if properties.fields_available_flags & definition.flag:
								raise PyMSError('Compile', 'Property already defined', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
								raise PyMSError('Compile', 'Expected open parenthesis', lexer.line)
							value_token = lexer.get_token(Tokens.IntegerToken)
							if not value_token:
								raise PyMSError('Compile', 'Expected an integer parameter', lexer.line)
							value = int(value_token.raw_value)
							if value < 0 or definition.parameter.max < value:
								raise PyMSError('Compile', 'Integer parameter too large', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
								raise PyMSError('Compile', 'Expected closing parenthesis', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, Tokens.NewlineToken):
								raise PyMSError('Compile', 'Expected end of line', lexer.line)
							setattr(properties, definition.attr, value)
							properties.fields_available_flags |= definition.flag
							property_found = True
						elif isinstance(definition, PropertyStateDefinition):
							if properties.state_flags & definition.flag:
								raise PyMSError('Compile', 'Property already defined', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != '(':
								raise PyMSError('Compile', 'Expected open parenthesis', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, TRGLexer.SymbolToken) or token.raw_value != ')':
								raise PyMSError('Compile', 'Expected closing parenthesis', lexer.line)
							token = lexer.next_token()
							if not isinstance(token, Tokens.NewlineToken):
								raise PyMSError('Compile', 'Expected end of line', lexer.line)
							properties.state_flags |= definition.flag
							property_found = True
						break
				else:
					raise PyMSError('Compile', 'Expected a property', lexer.line)
				token = lexer.next_token()
			if not property_found:
				raise PyMSError('Compile', 'No properties defined for Properties', lexer.line)
			unit_properties[properties_id] = properties
			return token

		token = lexer.skip(Tokens.NewlineToken)
		while True:
			if isinstance(token, Tokens.EOFToken):
				break
			if not isinstance(token, TRGLexer.KeywordsToken):
				raise PyMSError('Compile', 'Expected start of Trigger, String, or UnitProperties', lexer.line)
			if token.raw_value == 'Trigger' or token.raw_value == 'BriefingTrigger':
				trigger_format = Format.briefing if token.raw_value == 'BriefingTrigger' else Format.normal
				if format == None:
					format = trigger_format
				elif format != trigger_format:
					raise PyMSError('Compile', 'Invalid mix of Triggers and BriefingTriggers', lexer.line)
				token = process_trigger()
			elif token.raw_value == 'String':
				process_string()
				token = lexer.skip(Tokens.NewlineToken)
			elif token.raw_value == 'UnitProperties':
				token = process_properties()
			else:
				raise PyMSError('Compile', 'Expected start of Trigger, String, or UnitProperties', lexer.line)
		if not triggers:
			raise PyMSError('Compile', 'No triggers')
		
		# TODO: Check for missing Strings/UnitProperties
		self.triggers = triggers
		self.strings = strings
		self.unit_properties = unit_properties
		assert format is not None
		self.format = format
		return warnings

	def __eq__(self, other) -> bool:
		if not isinstance(other, TRG):
			return False
		if other.format != self.format:
			return False
		if other.triggers != self.triggers:
			return False
		if other.strings != self.strings:
			return False
		if other.unit_properties != self.unit_properties:
			return False
		return True
