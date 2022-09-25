
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
		('farms_notiming','Build necessary farms only when it hits the maximum supply available.'),
		('farms_timing','Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.'),
		('start_areatown','Starts the AI Script for area town management.'),
		('start_campaign','Starts the AI Script for Campaign.'),
		('start_town','Starts the AI Script for town management.'),
		('transports_off','Tells the AI to not worry about managing transports until check_transports is called.'),
	]),
	('Build/Attack/Defense order',[
		('attack_add','Add Byte Military to the current attacking party.'),
		('attack_clear','Clear the attack data.'),
		('attack_do','Attack the enemy with the current attacking party.'),
		('attack_prepare','Prepare the attack.'),
		('build','Build Building until it commands Byte(1) of them, at priority Byte(2).'),
		('defensebuild_aa','Build Byte Military to defend against enemy attacking air units, when air units are attacked.'),
		('defensebuild_ag','Build Byte Military to defend against enemy attacking air units, when ground units are attacked.'),
		('defensebuild_ga','Build Byte Military to defend against enemy attacking ground units, when air units are attacked.'),
		('defensebuild_gg','Build Byte Military to defend against enemy attacking ground units, when ground units are attacked.'),
		('defenseclear_aa','Clear defense against enemy attacking air units, when air units are attacked.'),
		('defenseclear_ag','Clear defense against enemy attacking air units, when ground units are attacked.'),
		('defenseclear_ga','Clear defense against enemy attacking ground units, when air units are attacked.'),
		('defenseclear_gg','Clear defense against enemy attacking ground units, when ground units are attacked.'),
		('defenseuse_aa','Use Byte Military to defend against enemy attacking air units, when air units are attacked.'),
		('defenseuse_ag','Use Byte Military to defend against enemy attacking air units, when ground units are attacked.'),
		('defenseuse_ga','Use Byte Military to defend against enemy attacking ground units, when air units are attacked.'),
		('defenseuse_gg','Use Byte Military to defend against enemy attacking ground units, when ground units are attacked.'),
		('guard_resources','Send units of type Military to guard as many resources spots as possible(1 per spot).'),
		('easy_attack',"""This command functions the same as attack_add, but only if the "AI Diffiulty" value is 0. Otherwise it doesn't do anything.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2."""),
		('eval_harass',"""This command will initiate an attack if it has not (without waiting for grouping), and then it will calculate the strength of its own attack force and enemy units in 32-tile range around the target region. If either the ground or air strength of the attack force is larger than the respective enemy strength, the script will jump to Block.

eval_harass will cause the grouping and attack to commence as usual, but it also can be canceled with attack_clear if you just want to use it for control flow instead of causing attacks."""),
		('harass_factor',"""This command can be used to scale attacks based on enemy strength. It calculates the total strength of all enemy units (including buildings), then multiplies the current attack force by
((enemy_strength - 1) / Word) - 1
Division is rounded down, multiplication is limited to range from 1 (no change) to 3."""),
		('prep_down',"""This command is similar to attack_add, but it can be used to add more units if the AI commands more of them. It is essentially:
attack_add max(unit_count(Military) - Byte(1), Byte(2)) Military"""),
		('tech','Research technology Technology, at priority Byte.'),
		('train','Train Military until it commands Byte of them.'),
		('do_morph','Train Military if it commands less than Byte of them.'),
		('upgrade','Research upgrade Upgrade up to level Byte(1), at priority Byte(2).'),
		('wait','Wait for Word tenths of second in normal game speed.'),
		('wait_finishattack','Wait until attacking party has finished to attack.'),
		('wait_build','Wait until computer commands Byte Building.'),
		('wait_buildstart','Wait until construction of Byte Unit has started.'),
		('wait_train','Wait until computer commands Byte Unit.'),
		('clear_combatdata','Clear previous combat data.'),
		('nuke_rate','Tells the AI to launch nukes every Byte minutes.'),
	]),
	('Flow control',[
		('call','Call Block as a sub-routine.'),
		('enemyowns_jump','If enemy has a Unit, jump to Block.'),
		('enemyresources_jump','If enemy has at least Word(1) minerals and Word(2) gas then jump in Block.'),
		('goto','Jump to Block.'),
		('groundmap_jump','If it is a ground map(in other words, if the enemy is reachable without transports), jump to Block.'),
		('killable','Allows the current thread to be killed by another one.'),
		('kill_thread','Kill the current thread.'),
		('notowns_jump','If computer doesn\'t have a Unit, jump to Block.'),
		('race_jump','According to the enemy race, jump in Block(1) if enemy is Terran, Block(2) if Zerg or Block(3) if Protoss.'),
		('random_jump','There is Byte chances out of 256 to jump to Block.'),
		('resources_jump','If computer has at least Word(1) minerals and Word(2) gas then jump in Block.'),
		('return','Return to the flow point of the call command.'),
		('stop','Stop script code execution. Often used to close script blocks called simultaneously.'),
		('time_jump','Jumps to Block if Byte normal game minutes have passed in the game.'),
		('region_size','Something to do with an enemy being in an unknown radius of the computer.'),
		('panic','Appears to trigger Block if attacked. Still unclear.'),
		('rush','Depending on Byte, it detects combinations of units and buildings either built or building, and jumps to Block'),
		('debug','Show debug string String and continue in Block.'),
	]),
	('Multiple threads',[
		('expand','Run code at Block for expansion number Byte.'),
		('multirun','Run simultaneously code (so in another thread) at Block.'),
	]),
	('Miscellaneous',[
		('create_nuke','Create a nuke. Should only be used in campaign scripts.'),
		('create_unit','Create Unit at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('define_max','Define maximum number of Unit to Byte.'),
		('give_money','Give 2000 ore and gas if owned resources are low. Should only be used in campaign scripts.'),
		('if_dif',"""This command will jump to Block if the "AI Difficulty" is LessThan/GreaterThan (Compare) Byte.
It seems that AI difficulty is mostly an unused concept. The AI Difficulty now is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow AI to mine more than 8 resources per trip if the difficulty was ever 2."""),
		('nuke_pos','Launch a nuke at map position (x,y) where x = Word(1) and y = Word(2). Should only be used in campaign scripts.'),
		('send_suicide','Send all units to suicide mission. Byte determines which type, 0 = Strategic suicide; 1 = Random suicide.'),
		('set_randomseed','Set random seed to DWord(1).'),
		('switch_rescue','Switch computer to rescuable passive mode.'),
		('help_iftrouble','Ask allies for help if ever in trouble.'),
		('check_transports','Used in combination with header command transports_off, the AI will build and keep as many transports as was set by the define_max (max 5?) and use them for drops and expanding.'),
		('creep','Effects the placement of towers (blizzard always uses 3 or 4 for Byte, see link below)'),
		('get_oldpeons','Pull Byte existing workers from the main base to the expansion, but the main base will train the workers to replace the ones you took. Useful if you need workers as quickly as possible at the expansion.'),
	]),
	('StarEdit',[
		('disruption_web','Disruption Web at selected location. (STAREDIT)'),
		('enter_bunker','Enter Bunker in selected location. (STAREDIT)'),
		('enter_transport','Enter in nearest Transport in selected location. (STAREDIT)'),
		('exit_transport','Exit Transport in selected location. (STAREDIT)'),
		('harass_location','AI Harass at selected location. (STAREDIT)'),
		('junkyard_dog','Junkyard Dog at selected location. (STAREDIT)'),
		('make_patrol','Make units patrol in selected location. (STAREDIT)'),
		('move_dt','Move Dark Templars to selected location. (STAREDIT)'),
		('nuke_location','Nuke at selected location. (STAREDIT)'),
		('player_ally','Make selected player ally. (STAREDIT)'),
		('player_enemy','Make selected player enemy. (STAREDIT)'),
		('recall_location','Recall at selected location. (STAREDIT)'),
		('sharedvision_off','Disable Shared Vision for selected player. (STAREDIT)'),
		('sharedvision_on','Enable Shared vision for selected player. (STAREDIT)'),
		('value_area','Value this area higher. (STAREDIT)'),
		('set_gencmd','Set generic command target. (STAREDIT)'),
	]),
	('Unknown',[
		('allies_watch','The use of this command is unknown. Takes Byte and Block as parameters.'),
		('capt_expand','The use of this command is unknown. Takes no parameter.'),
		('default_min','The use of this command is unknown. Takes Byte as parameter.'),
		('defaultbuild_off','The use of this command is unknown. Takes no parameter.'),
		('fake_nuke','The use of this command is unknown. Takes no parameters.'),
		('guard_all','The use of this command is unknown. Takes no parameters.'),
		('if_owned','The use of this command is unknown. Takes Unit and Block as parameters.'),
		('max_force','The use of this command is unknown. Takes Word as parameter.'),
		('place_guard','The use of this command is unknown. Takes Unit and Byte as parameters.'),
		('player_need','The use of this command is unknown. Takes Byte and Building as parameters.'),
		('scout_with','This command is unused.'),
		('set_attacks','The use of this command is unknown. Takes Byte as parameter.'),
		('target_expansion','The use of this command is unknown. Takes no parameter.'),
		('try_townpoint','The use of this command is unknown. Takes Byte and Block as parameters.'),
		('wait_force','The use of this command is unknown. Takes Byte and Unit as parameters.'),
	]),
	('Undefined',[
		('build_bunkers','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('build_turrets','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('default_build','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('fatal_error','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('if_towns','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('implode','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('quick_attack','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_bunkers','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_secure','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_turrets','The definition of this command is unknown. It is never used in Blizzard scripts.'),
		('wait_upgrades','The definition of this command is unknown. It is never used in Blizzard scripts.'),
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
