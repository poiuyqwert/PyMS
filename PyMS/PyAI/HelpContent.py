
from collections import OrderedDict

_types = [
	('byte','A number in the range 0 to 255'),
	('word','A number in the range 0 to 65535'),
	('dword','A number in the range 0 to 4294967295'),
	('unit','A unit ID from 0 to 227, or a full unit name from stat_txt.tbl'),
	('building','Same as unit type, but only units that are Buildings, Resource Miners, and Overlords'),
	('military','Same as unit type, but only for a unit to train (not a Building, Resource Miners, or Overlords)'),
	('gg_military','Same as Military type, but only for defending against an enemy Ground unit attacking your Ground unit'),
	('ag_military','Same as Military type, but only for defending against an enemy Air unit attacking your Ground unit'),
	('ga_military','Same as Military type, but only for defending against an enemy Ground unit attacking your Air unit'),
	('aa_military','Same as Military type, but only for defending against an enemy Air unit attacking your Air unit'),
	('upgrade','An upgrade ID from 0 to 60, or a full upgrade name from stat_txt.tbl'),
	('technology','An technology ID from 0 to 43, or a full technology name from stat_txt.tbl'),
	('string',"A string of any characters (except for nulls: <0>) in TBL string formatting (use <40> for an open parenthesis '(', <41> for a close parenthesis ')', and <44> for a comma ',')"),
	('block','The label name of a block in the code'),
	('compare','Either LessThan or GreaterThan')
]
TYPE_HELP = OrderedDict()
for t,h in _types:
	TYPE_HELP[t] = h

_cmds = [
	('Header',[
		('farms_notiming','Build necessary farms only when the AI player hits exactly the maximum supply available. May prevent training if the AI requests a 2 supply unit while only having 1 available.'),
		('farms_timing','Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.'),
		('start_areatown','Starts the AI Script for area town management - assigns all buildings within a location to a new AI town.'),
		('start_campaign','Sets a Campaign flag for the AI script which modifies AI behaviour. Note that Campaign is always set by default in UMS maps.'),
		('start_town','Starts the AI Script for town management. All of the computer players buildings that are not inside of an areatown get assigned to one main town.'),
		('transports_off','Sets a flag that prevents the AI from building transports or Protoss Observers.'),
	]),
	('Build/Attack/Defense order',[
		('attack_add','Add Byte Military to the current attacking party. An attacking party has a maximum size of 64 units.'),
		('attack_clear','Clear the attack data - resets existing State 8 AI regions to State 0 and removes attackers from party.'),
		('attack_do','Prepare an attack with current attacking party and launch it after a maximum of 120 (melee) or 180 (campaign) normal game seconds. Waits until the attack party finished grouping.'),
		('attack_prepare','Start preparing an attack with current attacking party and set it to launch after a maximum of 120 (melee) or 180 (campaign) normal game seconds. Does not wait until grouping is complete.'),
		('build','Build Building until it commands + started building at least Byte(1) of them (up to 30 per town), at priority Byte(2).'),
		('defensebuild_aa','Build Byte Military at a time to defend against enemy attacking air units, when they are located in unpathable regions.'),
		('defensebuild_ag','Build Byte Military at a time to defend against enemy attacking air units, when they are located in pathable regions.'),
		('defensebuild_ga','Build Byte Military at a time to defend against enemy units, when they are located in unpathable regions that do not contain air units.'),
		('defensebuild_gg','Build Byte Military at a time to defend against enemy attacking ground units, when they are located in pathable regions.'),
		('defenseclear_aa','Clear the _aa defense _use and _build lists.'),
		('defenseclear_ag','Clear the _ag defense _use and _build lists.'),
		('defenseclear_ga','Clear the _ga defense _use and _build lists.'),
		('defenseclear_gg','Clear the _gg defense _use and _build lists.'),
		('defenseuse_aa','Use Byte Military at a time to defend against enemy attacking air units, when they are located in unpathable regions.'),
		('defenseuse_ag','Use Byte Military at a time to defend against enemy attacking air units, when they are located in pathable regions.'),
		('defenseuse_ga','Use Byte Military at a time to defend against enemy units, when they are located in unpathable regions that do not contain air units.'),
		('defenseuse_gg','Use Byte Military at a time to defend against enemy attacking ground units, when they are located in pathable regions.'),
		('guard_resources','Send units of type Military to guard as many resource areas as possible(1 per spot).'),
		('easy_attack',"""This command functions the same as attack_add, but only if the "AI Diffiulty" value is 0. Otherwise it doesn't do anything.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2."""),
		('eval_harass',"""Jump to Block if the AI is currently preparing an attack."""),
		('harass_factor',"""This command can be used to scale attacks based on enemy strength. It calculates the total strength of all enemy units (including buildings) in a targeted attack region, then multiplies the current attack force by ((Word + enemy_strength - 1) / Word) - 1.
Division is rounded down, multiplication is limited to range from 1 (no change) to 3."""),
		('prep_down',"""This command is similar to attack_add, but it can be used to add more units if the AI commands more of them. It is essentially:
attack_add max(unit_count(Military) - Byte(1), Byte(2)) Military"""),
		('tech','Research technology Technology, at priority Byte.'),
		('train','Continuously produce Military and wait until it commands + has in production Byte of them.'),
		('do_morph','Once, start producing Military if it commands less than Byte of them.'),
		('upgrade','Research upgrade Upgrade up to level Byte(1), at priority Byte(2).'),
		('wait','Wait for Word frames. Normal is 15 frames per second.'),
		('wait_finishattack','Wait until there are no State 1/2/8/9 regions for the Computer player.'),
		('wait_build','Wait until computer commands Byte Building. This does not request the Building.'),
		('wait_buildstart','Wait until construction of Byte Unit has started. This does not request the Building.'),
		('wait_train','Wait until computer commands Byte Unit. This does not request the Unit.'),
		('clear_combatdata','Clear AI military order data for all units in location.'),
		('nuke_rate','Tells the AI to try to launch nukes every Byte minutes. The timer resets only after Nuke launching procedure started.'),
	]),
	('Flow control',[
		('call','Call Block as a sub-routine. Normally only one sub-routine can be active at a time.'),
		('enemyowns_jump','If enemy has a Unit (or building), jump to Block.'),
		('enemyresources_jump','If the closest enemy has at least Word(1) minerals and Word(2) gas then jump to Block.'),
		('goto','Jump to Block.'),
		('groundmap_jump','If the closest enemy is reachable without transports (via pathable regions), jump to Block.'),
		('killable','Allows the current thread to be killed by another one.'),
		('kill_thread','Kill all threads marked as killable for all players.'),
		('notowns_jump','If computer doesn\'t have a Unit, jump to Block.'),
		('race_jump','According to the closest enemy race, jump in Block(1) if enemy is Terran, Block(2) if Zerg or Block(3) if Protoss.'),
		('random_jump','There is Byte chances out of 256 to jump to Block.'),
		('resources_jump','If computer has at least Word(1) minerals and Word(2) gas then jump in Block.'),
		('return','Return to the flow point of the call command.'),
		('stop','Stop script code execution. Often used to close script blocks called simultaneously.'),
		('time_jump','Jumps to Block if Byte Normal game minutes have passed in the game.'),
		('region_size','Jump to Block if the town this command is used in has a pathfinder region count (meaning the sum of pathfinder regions connected and pathable by ground) below 32 times Byte.'),
		('panic','If AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using Block. If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted.'),
		('rush','Depending on Byte, it detects combinations of units and buildings owned by the closest enemy based on their race, and jumps to Block'),
		('debug','Print debug string String and jump to Block.'),
	]),
	('Multiple threads',[
		('expand','Run code at Block (that has to begin with start_town) to create a new area town at a random unoccupied resource location. This is ignored if the Computer player has more than Byte towns.'),
		('multirun','Run simultaneously code (spawn in another thread) at Block. The new thread is assigned to the same town the multirun originates from.'),
	]),
	('Miscellaneous',[
		('create_nuke','Create a nuke if an unoccupied Silo exists for player. Should only be used in campaign scripts.'),
		('create_unit','Create Unit at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('define_max','Define maximum number of Unit that can be trained or built to Byte. The limit takes precedence over otherwise requested train or build amounts.'),
		('give_money','Give up to 2000 ore and gas if owned resources are low. Should only be used in campaign scripts.'),
		('if_dif',"""This command will jump to Block if the "AI Difficulty" is LessThan/GreaterThan (Compare) Byte.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2."""),
		('nuke_pos','Order a free Ghost to launch a nuke at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('send_suicide','Send all units to suicide mission. Byte determines which type, 0 = Strategic suicide; 1 = Random suicide.'),
		('set_randomseed','Set random seed to DWord(1).'),
		('switch_rescue','Switch computer to rescuable passive mode.'),
		('help_iftrouble','Once, set a flag that creates State 4 (help) regions around this players buildings for all Computer players allied to this player. Once they have been defended, help_iftrouble can be requested again.'),
		('check_transports','The AI will request up to define_max limit (max 5) transports and Protoss Observers. Otherwise, it only trains up to 3.'),
		('creep','Spread Cannons and Creep Colonies in a wide area if Byte == 4, or a narrow area if it\'s anything else.'),
		('get_oldpeons','Ask to pull Byte existing workers from other towns to the town that owns the thread this was ran in.'),
	]),
	('StarEdit',[
		('disruption_web','Disruption Web at selected location. (STAREDIT)'),
		('enter_bunker','Enter Bunker in selected location. (STAREDIT)'),
		('enter_transport','Enter in nearest Transport in selected location. (STAREDIT)'),
		('exit_transport','Exit Transport in selected location. (STAREDIT)'),
		('harass_location','Unused. (STAREDIT)'),
		('junkyard_dog','Junkyard Dog at selected location. (STAREDIT)'),
		('make_patrol','Make units in selected location patrol to generic command target. (STAREDIT)'),
		('move_dt','Move Hero Dark Templars to selected location. Can crash the game if any are in training. (STAREDIT)'),
		('nuke_location','Nuke at selected location. (STAREDIT)'),
		('player_ally','Make selected player ally. (STAREDIT)'),
		('player_enemy','Make selected player enemy. (STAREDIT)'),
		('recall_location','Recall at selected location. (STAREDIT)'),
		('sharedvision_off','Disable Shared Vision for selected player. (STAREDIT)'),
		('sharedvision_on','Enable Shared vision for selected player. (STAREDIT)'),
		('value_area','Defend a region in the center of the specified location. (STAREDIT)'),
		('set_gencmd','Set generic command target. (STAREDIT)'),
	]),
	('Unknown',[
		('allies_watch','Expands at resource area number Byte using Block. Note: If Byte is less than 9 then it is a player\'s start location (unless it\'s not placed), otherwise it is a map\'s base location. Does nothing if the expansion is occupied (Resarea flag = 1). The maximum value for Byte is 250.'),
		('capt_expand','Creates state 4 regions around the AI\'s state 5 regions and around other state 4 regions. If default_min is greater than 0, causes the AI to train first of it\'s defensebuild_gg and _aa units until it hits a supply cap, define_max limit or has no resources left.'),
		('default_min','The Computer player will attempt to place at least Byte force worth of units in state 4, 5 and 6 regions.'),
		('defaultbuild_off','Disable continuous idle production of certain race-specific units when above 600 minerals and 300 gas. Recommended to include this command in every Campaign script.'),
		('fake_nuke','Reset AI nuke timer as if a Nuke was launched.'),
		('guard_all','Set all regions that contain AI units to a Town state, even for non-buildings.'),
		('if_owned','If Unit is owned by Computer player, jump to Block.'),
		('max_force','Computer player will attempt to use no more than Word force to defend a single attacked region.'),
		('place_guard','Place Unit at location determined by Byte. 0-town center, 1-minerals in resarea, 2+ - gas in resarea.'),
		('player_need','The player needs at least Byte Buildings between all their towns, and this town will try to make sure this stays true.'),
		('scout_with','This command is unused.'),
		('set_attacks','Set available expansion attacks to Byte. Decreased by one after each expansion attack.'),
		('target_expansion','Order current attacking party to immediately attack an expansion (a base with no Start Location), or abandon the attack if the time is less than 1500 Normal seconds and there are no expansions. This type of attacking is exclusive with attack_prepare, and requires all attackers to be ready beforehand.'),
		('try_townpoint','Jump to Block if the AI does not own at least Byte expansions.'),
		('wait_force','Continuously produce Military and wait until it commands Byte of them.'),
	]),
	('Undefined',[
		('build_bunkers','Build around 5 Bunkers randomly around this town. Can only be used by Terran.'),
		('build_turrets','Build around 5 randomly around this town. Can only be used by Terran.'),
		('default_build','Enable continuous idle production of certain race-specific units when above 600 minerals and 300 gas. Highly recommended to never include this command in Campaign scripts, as it\'s extremely buggy.'),
		('fatal_error','Instantly crash the game and send a bug report if available.'),
		('if_towns','This command is unused.'),
		('implode','Create state 4 regions in state 0, 1, 2, 3 regions that are connected to at most 1 ground region.'),
		('quick_attack','Set the current attack preparation timer to 5 seconds.'),
		('wait_bunkers','Wait for build_bunkers to finish.'),
		('wait_secure','Wait until an AI spend cycle happens without the AI requesting additional defenders. Refreshes every 7 Normal seconds early into the game and every 1500 frames later on.'),
		('wait_turrets','Wait for build_turrets to finish.'),
		('wait_upgrades','Only works if the Campaign flag is set. Wait until all Upgrade requests in queue have began researching.'),
	]),
]
CMD_HELP = OrderedDict()
for s,cmdl in _cmds:
	CMD_HELP[s] = OrderedDict()
	for c,h in cmdl:
		CMD_HELP[s][c] = h

DIRECTIVE_HELP = {
	'@spellcaster': """@spellcaster(Military):
  Mark a Military unit as a spellcaster so it can be used with defenseuse_xx/defensebuild_xx without
  warning that the unit doesn't have an attack.""",
	'@supress_all': """@supress_all(Type):
  Supress all warnings of a specific Type.""",
	'@suppress_next_line': """@supress_next_line(Type):
  Supress warnings of a specific Type on the next line of code."""
}
