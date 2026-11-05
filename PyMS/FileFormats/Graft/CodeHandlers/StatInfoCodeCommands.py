from __future__ import annotations

from . import CodeTypes
from .GraftCommandDefinition import GraftCommandDefinition, number_functions

from ....Utilities.CodeHandlers.CodeCommand import CodeCommandDefinition
from ....Utilities.CodeHandlers.CodeStruct import StructBlockDefinition, StructField
from ....Utilities import Struct

# Unit stat info. The stat panel of a single selected unit is redrawn by its display function whenever its
# status function finds that what the panel shows has changed.

DebugID = CodeCommandDefinition('debug_id', 'The debug unit ID {1} (unused by the game, defaults to the unit itself)', None, (CodeTypes.UnitCodeType(limits=(0, Struct.l_u32.max)),))

ChangedNever = GraftCommandDefinition('changed_never', 'Never Changes', 'Never redraws the stat panel (it is only drawn when the unit is selected)')
ChangedUnit = GraftCommandDefinition('changed_unit', 'Unit Stats Changed', "Redraws the stat panel when the unit's HP, shields, energy, hangar count, remaining time, supply or resources change")
ChangedBuilding = GraftCommandDefinition('changed_building', 'Building Stats/Progress Changed', 'Like `changed_unit`, and also while the building is constructing, training, researching or upgrading')
ChangedTransport = GraftCommandDefinition('changed_transport', 'Transport Cargo/Stats Changed', "Like `changed_unit`, and also when the loaded units or their HP change")
ChangedHangar = GraftCommandDefinition('changed_hangar', 'Hangar Count/Training Changed', 'Like `changed_unit`, and always while building Interceptors or Scarabs')
ChangedSummon = GraftCommandDefinition('changed_summon', 'Archon Merge Progress Changed', 'Like `changed_unit`, and always while the Archon merge is in progress')
ChangedMorph = GraftCommandDefinition('changed_morph', 'Morph Progress Changed', "Always redraws the stat panel of the player's own units (enemy units are like `changed_unit`)")
ChangedSupplyTransport = GraftCommandDefinition('changed_supply_transport', 'Supply/Transport Cargo Changed', "Like `changed_transport` while carrying units, otherwise redraws when HP, shields or the player's supply change")
ChangedPowerup = GraftCommandDefinition('changed_powerup', 'Powerup HP Changed', 'Redraws the stat panel when HP changes')

DrawUnit = GraftCommandDefinition('draw_unit', 'Draw Unit Stats', 'Draws the stat icons, status, kills, HP, energy and name of the unit')
DrawBuilding = GraftCommandDefinition('draw_building', 'Draw Building Stats/Progress', "Draws the building's construction, training, add-on, research or upgrade progress, its supply or resources, or its stat icons, then its HP, energy, status and name")
DrawTransport = GraftCommandDefinition('draw_transport', 'Draw Transport Cargo/Stats', 'Draws the loaded units of an own transport, otherwise like `draw_building` or `draw_unit`')
DrawHangar = GraftCommandDefinition('draw_hangar', 'Draw Hangar Training/Stats', 'Draws the training queue while building Interceptors or Scarabs, otherwise like `draw_unit`')
DrawSummon = GraftCommandDefinition('draw_summon', 'Draw Archon Merge Progress', 'Draws the summoning progress while the Archon merge is in progress, otherwise like `draw_unit`')
DrawMorph = GraftCommandDefinition('draw_morph', 'Draw Morph Progress', 'Draws the morph progress of an own unit, otherwise like `draw_unit`')
DrawSupplyTransport = GraftCommandDefinition('draw_supply_transport', 'Draw Supply/Transport Cargo', "Draws the player's supply, or the loaded units while carrying units (enemy units are like `draw_unit`)")
DrawPowerup = GraftCommandDefinition('draw_powerup', 'Draw Powerup Stats', 'Draws the stat icons, status, HP, energy and name (without kills)')
DrawNone = GraftCommandDefinition('draw_none', 'Draw Name Only', 'Draws only the name of the unit')

# In the order of FireGraft and the hook's lookup tables in `grafting.cpp` (a unit's stat info stores the index of its functions in these lists)
status_function_commands: list[GraftCommandDefinition] = number_functions([
	ChangedNever,
	ChangedUnit,
	ChangedBuilding,
	ChangedTransport,
	ChangedHangar,
	ChangedSummon,
	ChangedMorph,
	ChangedSupplyTransport,
	ChangedPowerup,
])

display_function_commands: list[GraftCommandDefinition] = number_functions([
	DrawUnit,
	DrawBuilding,
	DrawTransport,
	DrawHangar,
	DrawSummon,
	DrawMorph,
	DrawSupplyTransport,
	DrawPowerup,
	DrawNone,
])

unit_stat_info_commands: list[CodeCommandDefinition] = [DebugID, *status_function_commands, *display_function_commands]

# Buttons.graft unit stat info struct block

UnitStatusFunctionField = StructField('status_function', tuple(status_function_commands))
UnitDisplayFunctionField = StructField('display_function', tuple(display_function_commands))

UnitStatInfoBlock = StructBlockDefinition('unit_stat_info', 'unit stat info', 'Unit stat info {0}', (CodeTypes.UnitIDCodeType(),), fields=(
	StructField(DebugID.name, (DebugID,), required=False),
	UnitStatusFunctionField,
	UnitDisplayFunctionField,
))
