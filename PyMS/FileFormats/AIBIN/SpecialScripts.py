
from enum import Enum

class SpecialScriptPlayers(Enum):
	any_player = 'Runs on any player (computer, neutral, human)'
	computer_and_neutral = 'Runs on computer and neutral players'

# Script IDs StarCraft hardcodes to run on players other than just computers
SPECIAL_SCRIPTS: dict[str, SpecialScriptPlayers] = {
	'EnBk': SpecialScriptPlayers.any_player,
	'EnTr': SpecialScriptPlayers.any_player,
	'ExTr': SpecialScriptPlayers.any_player,
	'DWHe': SpecialScriptPlayers.any_player,
	'PB3F': SpecialScriptPlayers.any_player,
	'+Vi0': SpecialScriptPlayers.any_player,
	'+Vi1': SpecialScriptPlayers.any_player,
	'+Vi2': SpecialScriptPlayers.any_player,
	'+Vi3': SpecialScriptPlayers.any_player,
	'+Vi4': SpecialScriptPlayers.any_player,
	'+Vi5': SpecialScriptPlayers.any_player,
	'+Vi6': SpecialScriptPlayers.any_player,
	'+Vi7': SpecialScriptPlayers.any_player,
	'-Vi0': SpecialScriptPlayers.any_player,
	'-Vi1': SpecialScriptPlayers.any_player,
	'-Vi2': SpecialScriptPlayers.any_player,
	'-Vi3': SpecialScriptPlayers.any_player,
	'-Vi4': SpecialScriptPlayers.any_player,
	'-Vi5': SpecialScriptPlayers.any_player,
	'-Vi6': SpecialScriptPlayers.any_player,
	'-Vi7': SpecialScriptPlayers.any_player,
	'Rscu': SpecialScriptPlayers.computer_and_neutral,
}

def special_script_players(script_id: str) -> SpecialScriptPlayers | None:
	return SPECIAL_SCRIPTS.get(script_id)
