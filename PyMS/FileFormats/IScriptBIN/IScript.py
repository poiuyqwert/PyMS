
from . import IType
from .CodeHandlers import CodeCommands
from .CodeHandlers.ICESerializeContext import ICESerializeContext

from ...Utilities.CodeHandlers.CodeCommand import CodeCommand
from ...Utilities.CodeHandlers.CodeHeader import CodeHeader
from ...Utilities.CodeHandlers.CodeType import CodeBlock
from ...Utilities import Assets

from dataclasses import dataclass

@dataclass
class IScript(CodeHeader):
	id: int
	type: int

	init: CodeBlock
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

	def get_name(self) -> str:
		if self.id < len(Assets.data_cache(Assets.DataReference.IscriptIDList)):
			return Assets.data_cache(Assets.DataReference.IscriptIDList)[self.id]
		return f'UnknownScript{self.id}'

	def get_entry_points(self) -> list[tuple[CodeBlock, str | None]]:
		entry_points: list[tuple[CodeBlock | None, str]] = [
			(self.init, 'Init'),
			(self.death, 'Death'),
			(self.gndattkinit, 'GndAttkInit'),
			(self.airattkinit, 'AirAttkInit'),
			(self.unused1, 'Unused1'),
			(self.gndattkrpt, 'GndAttkRpt'),
			(self.airattkrpt, 'AirAttkRpt'),
			(self.castspell, 'CastSpell'),
			(self.gndattktoidle, 'GndAttkToIdle'),
			(self.airattktoidle, 'AirAttkToIdle'),
			(self.unused2, 'Unused2'),
			(self.walking, 'Walking'),
			(self.walkingtoidle, 'WalkingToIdle'),
			(self.specialstate1, 'SpecialState1'),
			(self.specialstate2, 'SpecialState2'),
			(self.almostbuilt, 'AlmostBuilt'),
			(self.built, 'Built'),
			(self.landing, 'Landing'),
			(self.liftoff, 'Liftoff'),
			(self.isworking, 'IsWorking'),
			(self.workingtoidle, 'WorkingToIdle'),
			(self.warpin, 'WarpIn'),
			(self.unused3, 'Unused3'),
			(self.stareditinit, 'StarEditInit'),
			(self.disable, 'Disable'),
			(self.burrow, 'Burrow'),
			(self.unburrow, 'Unburrow'),
			(self.enable, 'Enable'),
		]
		return [(block, name) for block,name in entry_points if block is not None]

	def get_entry_points_for_type(self) -> list[CodeBlock | None]:
		entry_points: list[CodeBlock | None] = [
			self.init,
			self.death,
			self.gndattkinit,
			self.airattkinit,
			self.unused1,
			self.gndattkrpt,
			self.airattkrpt,
			self.castspell,
			self.gndattktoidle,
			self.airattktoidle,
			self.unused2,
			self.walking,
			self.walkingtoidle,
			self.specialstate1,
			self.specialstate2,
			self.almostbuilt,
			self.built,
			self.landing,
			self.liftoff,
			self.isworking,
			self.workingtoidle,
			self.warpin,
			self.unused3,
			self.stareditinit,
			self.disable,
			self.burrow,
			self.unburrow,
			self.enable,
		]
		return entry_points[:IType.TYPE_TO_ENTRY_POINT_COUNT_MAP[self.type]]

# ----------------------------------------------------------------------------- #
# This header is used by images.dat entries:
# 115 Carrier Warp Flash (protoss\carrier.grp)
	def serialize(self, serialize_context: CodeCommands.SerializeContext) -> None:
		if serialize_context.formatters.indent_bodies:
			serialize_context.dedent()
		serialize_context.write('# ----------------------------------------------------------------------------- #\n')
		if isinstance(serialize_context, ICESerializeContext) and serialize_context.data_context.images_dat is not None:
			found = False
			for entry_id in range(serialize_context.data_context.images_dat.entry_count()):
				entry = serialize_context.data_context.images_dat.get_entry(entry_id)
				if not entry.iscript_id == self.id:
					continue
				if not found:
					serialize_context.write('# This header is used by images.dat entries:\n')
					found = True
				serialize_context.write(f'# {entry_id:>3} {serialize_context.data_context.image_name(entry_id)}\n')
		serialize_context.write('.headerstart\n')
		CodeCommand(CodeCommands.IsId, [self.id]).serialize(serialize_context)
		CodeCommand(CodeCommands.Type, [self.type]).serialize(serialize_context)
		commands: list[CodeCommand] = [
			CodeCommand(CodeCommands.Init, [self.init]),
			CodeCommand(CodeCommands.Death, [self.death]),
			CodeCommand(CodeCommands.Gndattkinit, [self.gndattkinit]),
			CodeCommand(CodeCommands.Airattkinit, [self.airattkinit]),
			CodeCommand(CodeCommands.Unused1, [self.unused1]),
			CodeCommand(CodeCommands.Gndattkrpt, [self.gndattkrpt]),
			CodeCommand(CodeCommands.Airattkrpt, [self.airattkrpt]),
			CodeCommand(CodeCommands.Castspell, [self.castspell]),
			CodeCommand(CodeCommands.Gndattktoidle, [self.gndattktoidle]),
			CodeCommand(CodeCommands.Airattktoidle, [self.airattktoidle]),
			CodeCommand(CodeCommands.Unused2, [self.unused2]),
			CodeCommand(CodeCommands.Walking, [self.walking]),
			CodeCommand(CodeCommands.Walkingtoidle, [self.walkingtoidle]),
			CodeCommand(CodeCommands.Specialstate1, [self.specialstate1]),
			CodeCommand(CodeCommands.Specialstate2, [self.specialstate2]),
			CodeCommand(CodeCommands.Almostbuilt, [self.almostbuilt]),
			CodeCommand(CodeCommands.Built, [self.built]),
			CodeCommand(CodeCommands.Landing, [self.landing]),
			CodeCommand(CodeCommands.Liftoff, [self.liftoff]),
			CodeCommand(CodeCommands.Isworking, [self.isworking]),
			CodeCommand(CodeCommands.Workingtoidle, [self.workingtoidle]),
			CodeCommand(CodeCommands.Warpin, [self.warpin]),
			CodeCommand(CodeCommands.Unused3, [self.unused3]),
			CodeCommand(CodeCommands.Stareditinit, [self.stareditinit]),
			CodeCommand(CodeCommands.Disable, [self.disable]),
			CodeCommand(CodeCommands.Burrow, [self.burrow]),
			CodeCommand(CodeCommands.Unburrow, [self.unburrow]),
			CodeCommand(CodeCommands.Enable, [self.enable]),
		]
		for command in commands[:IType.TYPE_TO_ENTRY_POINT_COUNT_MAP[self.type]]:
			command.serialize(serialize_context)
		serialize_context.write('.headerend\n')
		serialize_context.write('# ----------------------------------------------------------------------------- #\n')
