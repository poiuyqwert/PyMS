# Command Reference
This page documents every command in the core AI language (the commands supported by the unmodded game). Commands added by the AISE plugin are documented on the [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md) page. The same documentation is shown as tooltips when hovering a command in the [Code Editor](/Help/Programs/PyAI/Code_Editor.md).
Signatures are shown in the parenthesis command style — the flat style is equally valid (see [AI Language](/Help/Programs/PyAI/AI_Language.md#commands)). The parameter names used in the signatures are descriptive; what matters is each parameter's type, listed in [Parameter Types](#parameter-types).

## Header Commands
These commands can only be used inside a `script` header (see [Script Headers](/Help/Programs/PyAI/AI_Language.md#script-headers)):

### `name_string`
`name_string(tbl_string)` — Set the name displayed in StarEdit for this script to the string with the given index in `stat_txt.tbl`.

### `bin_file`
`bin_file(bin_file)` — Set which file this script is saved in, either `aiscript` or `bwscript`.

### `broodwar_only`
`broodwar_only(bool)` — Set the flag for if this script is only available in BroodWar.

### `staredit_hidden`
`staredit_hidden(bool)` — Set the flag for if this script is hidden in StarEdit.

### `requires_location`
`requires_location(bool)` — Set the flag for if this script requires a location.

### `entry_point`
`entry_point(block)` — Set the block where the script will start.

## Town and Expansion

### `start_town`
`start_town()` — Starts the AI Script for town management.

### `start_areatown`
`start_areatown()` — Starts the AI Script for area town management.

### `expand`
`expand(expansion, block)` — Run code at `block` for expansion number `expansion`.

### `allies_watch`
`allies_watch(resarea, block)` — Expands at resource area number `resarea` using `block`. If `resarea` is below 9, it is a player's start location, otherwise it's a map's base location. Does nothing if the resource area is occupied.

### `try_townpoint`
`try_townpoint(count, block)` — Jump to `block` if the AI doesn't own at least `count` expansions (includes areatowns). Ignored otherwise. Used in conjunction with `expand` or `allies_watch`.

### `panic`
`panic(block)` — If the AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using `block`. If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted. Can cause crashes if any of the map's free resource areas have no resources and never had them.

### `get_oldpeons`
`get_oldpeons(count)` — Pull `count` existing workers from the main base to the expansion, but the main base will train workers to replace the ones you took. Useful if you need workers as quickly as possible at the expansion.

### `implode`
`implode()` — Changes the state of AI regions: for any region which has state 0, 1, 2 or 3 that is connected to at most one pathfinding region by ground, the region's state is changed to 4.

### `guard_all`
`guard_all()` — Sets all regions with self-owned units in them to state 5, identical on melee.

### `capt_expand`
`capt_expand()` — Creates state 4 regions around the AI's state 5 regions and other state 4 regions. If `default_min` is greater than 0, causes the AI to train first of its `defensebuild_gg` and `_aa` units until it hits a supply cap, `define_max` limit or has no resources left, at low priority. The AI then tries to distribute these units over state 4 regions, as evenly as possible.

## Building Training and Research

### `build`
`build(count, building, priority)` — Build `building` until the computer commands `count` of them, at priority `priority`.

### `upgrade`
`upgrade(level, upgrade, priority)` — Research upgrade `upgrade` up to level `level`, at priority `priority`.

### `tech`
`tech(technology, priority)` — Research technology `technology`, at priority `priority`.

### `train`
`train(count, military)` — Train `military` until the computer commands `count` of them.

### `do_morph`
`do_morph(count, military)` — Train `military` if the computer commands less than `count` of them.

### `define_max`
`define_max(count, unit)` — Define the maximum number of `unit` to `count`. 255 is none.

### `player_need`
`player_need(count, building)` — Adds a request to the town so that if the player does not own `count` number of `building` anywhere, then it rebuilds them in this town at priority 80.

### `default_build`
`default_build()` — Alters the behaviour of the AI so that if the AI has more than 600 minerals and 300 gas and no other requests, it will continuously train race specific units until it reaches the `define_max` value or gets supply capped. Usually should be disabled with `defaultbuild_off`.

### `defaultbuild_off`
`defaultbuild_off()` — Turns off `default_build`. `default_build` should realistically always be turned off.

### `default_min`
`default_min(value)` — Sets the default needed force value for state 4 and state 6 regions to `value`.

### `farms_notiming`
`farms_notiming()` — Build necessary farms only when it hits the maximum supply available.

### `farms_timing`
`farms_timing()` — Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.

### `build_bunkers`
`build_bunkers()` — Builds up to 3 bunkers around the base. Requests a Siege Tank guard in places where a bunker is built.

### `wait_bunkers`
`wait_bunkers()` — Waits for the command `build_bunkers` to finish.

### `build_turrets`
`build_turrets()` — Builds up to 6 missile turrets around the base. Requests a Ghost guard in places where a turret is built.

### `wait_turrets`
`wait_turrets()` — Waits for the command `build_turrets` to finish.

### `place_guard`
`place_guard(unit, position)` — Place one `unit` to guard the town at strategic location `position`, at priority 60. 0 is the town location center, 1 is at the mineral line, 2 and up is the vespene geyser.

### `guard_resources`
`guard_resources(military)` — Send units of type `military` to guard as many resource spots as possible (1 per spot).

### `creep`
`creep(placement)` — Effects the placement of towers (Blizzard always uses 3 or 4 for `placement`).

### `wait_build`
`wait_build(count, building)` — Wait until the computer commands `count` number of `building`.

### `wait_buildstart`
`wait_buildstart(count, unit)` — Wait until construction of `count` number of `unit` has started.

### `wait_train`
`wait_train(count, unit)` — Wait until the computer commands `count` of `unit`.

### `wait_force`
`wait_force(count, military)` — Wait until the computer commands `count` of `military`, while training them as long as it's waiting. The request is checked every 30 frames. Waits for 16 frames whenever the requirement is not fulfilled.

### `wait_upgrades`
`wait_upgrades()` — Waits until all upgrade (not tech) requests have begun researching. Only works in campaign scripts. You should wait about 30 seconds (`wait 480`) before setting the requests and calling `wait_upgrades`, so that the request log has enough time to update.

### `wait_secure`
`wait_secure()` — Waits until the AI player trains a defense unit with `defensebuild` of any type. Is usable again after going through within about 7 seconds earlygame or 37 seconds later in the game (likely after 1500 frames).

## Attacking

### `attack_clear`
`attack_clear()` — Clear the attack data.

### `attack_add`
`attack_add(count, military)` — Add `count` number of `military` to the current attacking party.

### `attack_prepare`
`attack_prepare()` — Prepare the attack.

### `attack_do`
`attack_do()` — Attack the enemy with the current prepared attacking party.

### `wait_finishattack`
`wait_finishattack()` — Wait until the attacking party has finished attacking.

### `quick_attack`
`quick_attack()` — Sets the starting attack point back far enough in time so that the deadline goes down to 5 seconds. Never use this if it would set the starting point to before the first 16 frames of the game.

### `prep_down`
`prep_down(saved, minimum, military)` — Similar to `attack_add`, but it can be used to add more units if the AI commands more of them. It adds all the units the AI commands of the type except `saved`, or `minimum` if that would be more.

### `eval_harass`
`eval_harass(block)` — Initiates an attack if it has not (without waiting for grouping), and then calculates the strength of its own attack force and enemy units in 32-tile range around the target region. If either the ground or air strength of the attack force is larger than the respective enemy strength, the script will jump to `block`. The grouping and attack commence as usual, but can be canceled with `attack_clear` if you just want to use this for control flow instead of causing attacks.

### `harass_factor`
`harass_factor(strength)` — Scales attacks based on enemy strength. It calculates the total strength of all enemy units (including buildings), then multiplies the current attack force by `((enemy_strength - 1) / strength) - 1` (division rounded down, multiplication limited to the range from 1 to 3).

### `target_expansion`
`target_expansion()` — Executes an expansion attack with a deadline of 1 second (requires the units to be trained beforehand and practically has no grouping). Expansion attacks never choose bases built around start locations before 1500 in-game seconds. They can acquire those bases as targets afterwards, but they will still prefer to target expansions.

### `set_attacks`
`set_attacks(count)` — Sets the number of attacks possible to execute with `target_expansion` to `count`. Cannot be used if the campaign flag is set.

### `send_suicide`
`send_suicide(type)` — Send all units on a suicide mission. `type` determines which kind: 0 = Strategic suicide, 1 = Random suicide.

### `nuke_rate`
`nuke_rate(minutes)` — Tells the AI to launch nukes every `minutes` minutes.

### `fake_nuke`
`fake_nuke()` — Resets the AI nuke timer.

## Defense
The defense commands come in four variants, one for each combination of the enemy unit type attacking and your unit type being attacked: `gg` = enemy ground attacker against your ground units, `ag` = enemy air attacker against your ground units, `ga` = enemy ground attacker against your air units, and `aa` = enemy air attacker against your air units.

### `defensebuild_gg`
`defensebuild_gg(count, gg_military)` — Build `count` of the unit to defend against enemy attacking ground units, when ground units are attacked.

### `defensebuild_ag`
`defensebuild_ag(count, ag_military)` — Build `count` of the unit to defend against enemy attacking air units, when ground units are attacked.

### `defensebuild_ga`
`defensebuild_ga(count, ga_military)` — Build `count` of the unit to defend against enemy attacking ground units, when air units are attacked.

### `defensebuild_aa`
`defensebuild_aa(count, aa_military)` — Build `count` of the unit to defend against enemy attacking air units, when air units are attacked.

### `defenseuse_gg`
`defenseuse_gg(count, gg_military)` — Use `count` of the unit to defend against enemy attacking ground units, when ground units are attacked.

### `defenseuse_ag`
`defenseuse_ag(count, ag_military)` — Use `count` of the unit to defend against enemy attacking air units, when ground units are attacked.

### `defenseuse_ga`
`defenseuse_ga(count, ga_military)` — Use `count` of the unit to defend against enemy attacking ground units, when air units are attacked.

### `defenseuse_aa`
`defenseuse_aa(count, aa_military)` — Use `count` of the unit to defend against enemy attacking air units, when air units are attacked.

### `defenseclear_gg`
`defenseclear_gg()` — Clear defense against enemy attacking ground units, when ground units are attacked.

### `defenseclear_ag`
`defenseclear_ag()` — Clear defense against enemy attacking air units, when ground units are attacked.

### `defenseclear_ga`
`defenseclear_ga()` — Clear defense against enemy attacking ground units, when air units are attacked.

### `defenseclear_aa`
`defenseclear_aa()` — Clear defense against enemy attacking air units, when air units are attacked.

### `max_force`
`max_force(force)` — Lets the AI use up to `force` worth of units to defend any given defensible region. Force is determined for every unit using the standard calculation (see PyDAT's AI Actions tab under [units.dat](/Help/Files/DAT/units.dat.md)).

### `clear_combatdata`
`clear_combatdata()` — Clear previous combat data.

### `help_iftrouble`
`help_iftrouble()` — Ask allies for help if ever in trouble.

## Flow Control

### `goto`
`goto(block)` — Jump to `block`.

### `call`
`call(block)` — Call `block` as a sub-routine.

### `return`
`return()` — Return to the flow point of the `call` command.

### `stop`
`stop()` — Stop script code execution. Often used to close script blocks called simultaneously.

### `wait`
`wait(time)` — Wait for `time` tenths of a second in normal game speed.

### `multirun`
`multirun(block)` — Run code at `block` simultaneously (in another thread).

### `kill_thread`
`kill_thread()` — Kill the current thread.

### `killable`
`killable()` — Allows the current thread to be killed by another one.

### `random_jump`
`random_jump(chance, block)` — There is `chance` chances out of 256 to jump to `block`.

### `time_jump`
`time_jump(minutes, block)` — Jumps to `block` if `minutes` normal game minutes have passed in the game.

### `race_jump`
`race_jump(terran, zerg, protoss)` — According to the enemy race, jump to `terran` if the enemy is Terran, `zerg` if Zerg, or `protoss` if Protoss.

### `notowns_jump`
`notowns_jump(unit, block)` — If the computer doesn't have a `unit`, jump to `block`.

### `groundmap_jump`
`groundmap_jump(block)` — If it is a ground map (in other words, if the enemy is reachable without transports), jump to `block`.

### `resources_jump`
`resources_jump(minerals, gas, block)` — If the computer has at least `minerals` minerals and `gas` gas, then jump to `block`.

### `enemyowns_jump`
`enemyowns_jump(unit, block)` — If the enemy has a `unit`, jump to `block`.

### `enemyresources_jump`
`enemyresources_jump(minerals, gas, block)` — If the enemy has at least `minerals` minerals and `gas` gas, then jump to `block`.

### `region_size`
`region_size(size, block)` — Jump to `block` if the town this command is used in has a pathfinder region count (meaning the sum of pathfinder regions connected and pathable by ground) below 32 times `size`.

### `if_owned`
`if_owned(unit, block)` — If the player owns a `unit` (includes incomplete), then jump to `block`.

### `if_dif`
`if_dif(compare, value, block)` — Jumps to `block` if the "AI Difficulty" is LessThan/GreaterThan (`compare`) `value`. AI difficulty is mostly an unused concept: it is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow the AI to mine more than 8 resources per trip if the difficulty was ever 2.

### `easy_attack`
`easy_attack(count, military)` — Functions the same as `attack_add`, but only if the "AI Difficulty" value is 0. Otherwise it doesn't do anything (see `if_dif` about AI difficulty).

### `rush`
`rush(type, block)` — Depending on `type`, it detects combinations of units and buildings either built or building, and jumps to `block`.

### `debug`
`debug(block, message)` — Show debug string `message` and continue in `block`.

### `fatal_error`
`fatal_error()` — Crashes StarCraft with a fatal error and the message "Illegal AI script executed".

## Campaign Commands
These commands should only be used in campaign scripts:

### `start_campaign`
`start_campaign()` — Starts the AI Script for Campaign.

### `give_money`
`give_money()` — Give 2000 ore and gas if owned resources are low.

### `create_nuke`
`create_nuke()` — Creates a nuke in a free silo. Can be used multiple times as long as there are empty silos.

### `create_unit`
`create_unit(unit, x, y)` — Create `unit` at map position (`x`, `y`).

### `nuke_pos`
`nuke_pos(x, y)` — Launch a nuke at map position (`x`, `y`).

### `switch_rescue`
`switch_rescue()` — Switch the computer to rescuable passive mode.

## StarEdit Location Commands
These commands are made to be used by scripts run from map triggers with the "Run AI Script at Location" action, and operate on the location the script was run at:

### `player_enemy`
`player_enemy()` — Makes all players in the location an enemy of the trigger owner.

### `player_ally`
`player_ally()` — Makes all players in the location an ally of the trigger owner.

### `value_area`
`value_area()` — Value this area higher. Causes the computer to consider the region for defense. If the AI doesn't control any buildings in the region, it will only be defended once. Doesn't do anything if the region already has enemy units in it.

### `move_dt`
`move_dt()` — Orders the computer to move all Dark Templars, campaign and unit, to the location. Crashes if a Dark Templar is being trained.

### `enter_bunker`
`enter_bunker()` — Orders infantry units in the location to attempt entering Bunkers in the same location.

### `set_gencmd`
`set_gencmd()` — Set the location as the generic command target to be used by other commands (like `make_patrol`).

### `make_patrol`
`make_patrol()` — Make units in the location patrol to the location set using the `set_gencmd` command.

### `enter_transport`
`enter_transport()` — Orders units in the location to enter the closest transport.

### `exit_transport`
`exit_transport()` — Orders transports in the location to unload the units within.

### `sharedvision_on`
`sharedvision_on(player)` — Player number `player` gives vision to the player executing the script. Players are 0-based.

### `sharedvision_off`
`sharedvision_off(player)` — Player number `player` stops giving vision to the player executing the script. Players are 0-based.

### `nuke_location`
`nuke_location()` — Nuke at the location. Must have a Ghost and a loaded nuke silo.

### `harass_location`
`harass_location()` — AI Harass at the location.

### `junkyard_dog`
`junkyard_dog()` — Orders units in the location to Junkyard Dog (movement similar to that of a critter, but attacks nearby enemies if possible).

### `disruption_web`
`disruption_web()` — Cast a Disruption Web at the location. The player must have a Corsair with the researched tech.

### `recall_location`
`recall_location()` — Recall at the location. The player must have an Arbiter (not Danimoth) with the researched tech.

## Miscellaneous

### `transports_off`
`transports_off()` — Tells the AI to not worry about managing transports until `check_transports` is called.

### `check_transports`
`check_transports()` — Used in combination with `transports_off`, the AI will build and keep as many transports as was set by `define_max` (max 5?) and use them for drops and expanding.

### `scout_with`
`scout_with(military)` — This command is unused.

### `set_randomseed`
`set_randomseed(seed)` — Set the random seed to `seed`.

## Parameter Types

### Byte Type
`byte` — A number in the range 0 to 255.

### Word Type
`word` — A number in the range 0 to 65535.

### Dword Type
`dword` — A number in the range 0 to 4294967295.

### Block Type
`block` — The label name of a block in the code.

### Unit Type
`unit` — A unit ID from 0 to 227 (or higher if using an expanded DAT file), or a full unit name from `stat_txt.tbl`.

### Building Type
`building` — Same as `unit`, but only units that are Buildings, Resource Miners, and Overlords.

### Military Type
`military` — Same as `unit`, but only for a unit to train (not a Building, Resource Miner, or Overlord).

### GG Military Type
`gg_military` — Same as `military`, but only for defending against an enemy Ground unit attacking your Ground unit.

### AG Military Type
`ag_military` — Same as `military`, but only for defending against an enemy Air unit attacking your Ground unit.

### GA Military Type
`ga_military` — Same as `military`, but only for defending against an enemy Ground unit attacking your Air unit.

### AA Military Type
`aa_military` — Same as `military`, but only for defending against an enemy Air unit attacking your Air unit.

### Upgrade Type
`upgrade` — An upgrade ID from 0 to 60 (or higher if using an expanded DAT file), or a full upgrade name from `stat_txt.tbl`.

### Technology Type
`technology` — A technology ID from 0 to 43 (or higher if using an expanded DAT file), or a full technology name from `stat_txt.tbl`.

### String Type
`string` — A string of any characters (except for nulls: `<0>`) in TBL string formatting (use `<40>` for an open parenthesis, `<41>` for a close parenthesis, and `<44>` for a comma).

### Compare Type
`compare` — Either `LessThan` or `GreaterThan`.

### TBL String Type
`tbl_string` — The index of a string in `stat_txt.tbl`.

### Bin File Type
`bin_file` — Either `aiscript` or `bwscript`.

### Bool Type
`bool` — A value of either `true`/`1` or `false`/`0`.

## See Also
- [AI Language](/Help/Programs/PyAI/AI_Language.md)
- [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)
