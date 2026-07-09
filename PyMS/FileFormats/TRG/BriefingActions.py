
from __future__ import annotations

from .ActionDefinition import ActionDefinition, BasicActionDefinition, RawActionDefinition
from .Parameters import ModifierParameter, SlotParameter, StringParameter, TimeParameter, UnitParameter, WAVParameter
from .Action import Action
from .Constants import ActionType, BriefingActionType, Matches

definitions_registry: list[ActionDefinition] = [
	BasicActionDefinition(name='NoAction', description='No action', action_type=BriefingActionType.no_action),
    BasicActionDefinition(name='Wait', description='Wait for {1} milliseconds.', action_type=BriefingActionType.wait, parameters=(TimeParameter(),)),
    BasicActionDefinition(name='PlayWAV', description='Play {0} with duration {2}.', action_type=BriefingActionType.play_wav, parameters=(WAVParameter(), TimeParameter())),
    BasicActionDefinition(name='DisplayTextMessage', description='Display {0} for current player when {1}.', action_type=BriefingActionType.text_message, parameters=(StringParameter(), TimeParameter())),
    BasicActionDefinition(name='SetMissionObjectives', description='Set mission objectives to {0}.', action_type=ActionType.set_mission_objectives, parameters=(StringParameter(),)),
    BasicActionDefinition(name='ShowPortrait', description='Show portrait of {0} in {1}.', action_type=BriefingActionType.show_portrait, parameters=(UnitParameter(), SlotParameter())),
    BasicActionDefinition(name='HidePortrait', description='Hide portrait in {1}.', action_type=BriefingActionType.hide_portrait, parameters=(SlotParameter(),)),
    BasicActionDefinition(name='DisplaySpeakingPortrait', description='Display speaking portrait in {0} for {1} milliseconds.', action_type=BriefingActionType.display_speaking_portrait, parameters=(SlotParameter(), TimeParameter())),
    BasicActionDefinition(name='Transmission', description='Send transmission to current player for {1}. Play {2} with duration {3}. Modify transmission duration: {4} {5} milliseconds. Display {0}.', action_type=BriefingActionType.transmission, parameters=(StringParameter(), SlotParameter(), WAVParameter(), TimeParameter(), ModifierParameter(), TimeParameter(transmission=True))),
	BasicActionDefinition(name='SkipTutorialEnabled', description='Show the Skip Tutorial button in the briefing UI.', action_type=BriefingActionType.skip_tutorial_enabled),

	RawActionDefinition()
]

def register_definition(definition: ActionDefinition) -> None:
	definitions_registry.append(definition)

def get_definition(action: Action) -> ActionDefinition:
	result_definition: ActionDefinition
	result_matches = Matches.no
	for definition in definitions_registry:
		matches = definition.matches(action)
		if matches > result_matches:
			result_definition = definition
			result_matches = matches
	return result_definition

def get_definition_named(name: str) -> (ActionDefinition | None):
	for definition in definitions_registry:
		if definition.name == name:
			return definition
	return None
