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
`start_town()` — Starts the AI Script for town management. All of the computer player's buildings that are not inside of an areatown get assigned to one main town.

### `start_areatown`
`start_areatown()` — Starts the AI Script for area town management. Assigns all buildings within the location to a new AI town.

### `expand`
`expand(expansion, block)` — Run code at `block` (which has to begin with `start_town`) to create a new area town at a random unoccupied resource location. This is ignored if the computer player has more than `expansion` towns.

### `allies_watch`
`allies_watch(resarea, block)` — Expands at resource area number `resarea` using `block`. If `resarea` is below 9, it is a player's start location (unless it's not placed), otherwise it's a map's base location. Does nothing if the resource area is occupied. The maximum value for `resarea` is 250.

### `try_townpoint`
`try_townpoint(count, block)` — Jump to `block` if the AI doesn't own at least `count` expansions (includes areatowns). Ignored otherwise. Used in conjunction with `expand` or `allies_watch`.

### `panic`
`panic(block)` — If the AI has not expanded yet and total unmined minerals in the mineral line are less than 7500, then it will expand using `block`. If the AI has expanded before, the command triggers every time there are less than 7500 unmined minerals total in all owned bases, or there are less than 2 owned Refineries that are not depleted. Can cause crashes if any of the map's free resource areas have no resources and never had them.

### `get_oldpeons`
`get_oldpeons(count)` — Ask to pull `count` existing workers from other towns to the town that owns the thread this was run in.

### `implode`
`implode()` — Changes the state of AI regions: for any region which has state 0, 1, 2 or 3 that is connected to at most one pathfinding region by ground, the region's state is changed to 4.

### `guard_all`
`guard_all()` — Sets all regions with self-owned units in them to state 5, identical on melee.

### `capt_expand`
`capt_expand()` — Creates state 4 regions around the AI's state 5 regions and other state 4 regions. If `default_min` is greater than 0, causes the AI to train first of its `defensebuild_gg` and `_aa` units until it hits a supply cap, `define_max` limit or has no resources left, at low priority. The AI then tries to distribute these units over state 4 regions, as evenly as possible.

## Building Training and Research

### `build`
`build(count, building, priority)` — Build `building` until the computer commands or has started building at least `count` of them (up to 30 per town), at priority `priority`.

### `upgrade`
`upgrade(level, upgrade, priority)` — Research upgrade `upgrade` up to level `level`, at priority `priority`.

### `tech`
`tech(technology, priority)` — Research technology `technology`, at priority `priority`.

### `train`
`train(count, military)` — Continuously produce `military` and wait until the computer commands or has in production `count` of them.

### `do_morph`
`do_morph(count, military)` — Once, start producing `military` if the computer commands less than `count` of them.

### `define_max`
`define_max(count, unit)` — Define the maximum number of `unit` that can be trained or built to `count`. 255 is none. The limit takes precedence over otherwise requested train or build amounts.

### `player_need`
`player_need(count, building)` — Adds a request to the town so that if the player does not own `count` number of `building` anywhere, then it rebuilds them in this town at priority 80.

### `default_build`
`default_build()` — Alters the behaviour of the AI so that if the AI has more than 600 minerals and 300 gas and no other requests, it will continuously train race specific units until it reaches the `define_max` value or gets supply capped. Usually should be disabled with `defaultbuild_off`. Highly recommended to never include this command in campaign scripts, as it's extremely buggy.

### `defaultbuild_off`
`defaultbuild_off()` — Turns off `default_build`, disabling continuous idle production of certain race-specific units when above 600 minerals and 300 gas. Recommended to include this command in every campaign script.

### `default_min`
`default_min(value)` — Sets the default needed force value for state 4, 5 and 6 regions to `value`. The computer player will attempt to place at least that much force worth of units in those regions.

### `farms_notiming`
`farms_notiming()` — Build necessary farms only when the AI player hits exactly the maximum supply available. May prevent training if the AI requests a 2 supply unit while only having 1 available.

### `farms_timing`
`farms_timing()` — Build necessary farms with a correct timing, so nothing is paused by a maximum supply limit hit.

### `build_bunkers`
`build_bunkers()` — Builds around 5 bunkers randomly around this town. Can only be used by Terran. Requests a Siege Tank guard in places where a bunker is built.

### `wait_bunkers`
`wait_bunkers()` — Waits for the command `build_bunkers` to finish.

### `build_turrets`
`build_turrets()` — Builds around 5 missile turrets randomly around this town. Can only be used by Terran. Requests a Ghost guard in places where a turret is built.

### `wait_turrets`
`wait_turrets()` — Waits for the command `build_turrets` to finish.

### `place_guard`
`place_guard(unit, position)` — Place one `unit` to guard the town at strategic location `position`, at priority 60. 0 is the town location center, 1 is at the mineral line, 2 and up is the vespene geyser.

### `guard_resources`
`guard_resources(military)` — Send units of type `military` to guard as many resource areas as possible (1 per spot).

### `creep`
`creep(placement)` — Spread Cannons and Creep Colonies in a wide area if `placement` is 4, or a narrow area if it's anything else.

### `wait_build`
`wait_build(count, building)` — Wait until the computer commands `count` number of `building`. This does not request the building.

### `wait_buildstart`
`wait_buildstart(count, unit)` — Wait until construction of `count` number of `unit` has started. This does not request the building.

### `wait_train`
`wait_train(count, unit)` — Wait until the computer commands `count` of `unit`. This does not request the unit.

### `wait_force`
`wait_force(count, military)` — Wait until the computer commands `count` of `military`, while training them as long as it's waiting. The request is checked every 30 frames. Waits for 16 frames whenever the requirement is not fulfilled.

### `wait_upgrades`
`wait_upgrades()` — Waits until all upgrade (not tech) requests have begun researching. Only works in campaign scripts. You should wait about 30 seconds (`wait 480`) before setting the requests and calling `wait_upgrades`, so that the request log has enough time to update.

### `wait_secure`
`wait_secure()` — Waits until an AI spend cycle happens without the AI requesting additional defenders. Refreshes about every 7 normal game seconds early in the game, and every 1500 frames later on.

## Attacking

### `attack_clear`
`attack_clear()` — Clear the attack data. Resets existing state 8 AI regions to state 0 and removes attackers from the party.

### `attack_add`
`attack_add(count, military)` — Add `count` number of `military` to the current attacking party. An attacking party has a maximum size of 64 units.

### `attack_prepare`
`attack_prepare()` — Start preparing an attack with the current attacking party and set it to launch after a maximum of 120 (melee) or 180 (campaign) normal game seconds. Does not wait until grouping is complete.

### `attack_do`
`attack_do()` — Prepare an attack with the current attacking party and launch it after a maximum of 120 (melee) or 180 (campaign) normal game seconds. Waits until the attack party has finished grouping.

### `wait_finishattack`
`wait_finishattack()` — Wait until there are no state 1/2/8/9 regions for the computer player.

### `quick_attack`
`quick_attack()` — Sets the starting attack point back far enough in time so that the deadline goes down to 5 seconds. Never use this if it would set the starting point to before the first 16 frames of the game.

### `prep_down`
`prep_down(saved, minimum, military)` — Similar to `attack_add`, but it can be used to add more units if the AI commands more of them. It adds all the units the AI commands of the type except `saved`, or `minimum` if that would be more.

### `eval_harass`
`eval_harass(block)` — Initiates an attack if it has not (without waiting for grouping), and then calculates the strength of its own attack force and enemy units in 32-tile range around the target region. If either the ground or air strength of the attack force is larger than the respective enemy strength, the script will jump to `block`. The grouping and attack commence as usual, but can be canceled with `attack_clear` if you just want to use this for control flow instead of causing attacks.

### `harass_factor`
`harass_factor(strength)` — Scales attacks based on enemy strength. It calculates the total strength of all enemy units (including buildings), then multiplies the current attack force by `((enemy_strength - 1) / strength) - 1` (division rounded down, multiplication limited to the range from 1 to 3).

### `target_expansion`
`target_expansion()` — Executes an expansion attack with a deadline of 1 second (requires the units to be trained beforehand and practically has no grouping). Expansion attacks never choose bases built around start locations before 1500 in-game seconds. They can acquire those bases as targets afterwards, but they will still prefer to target expansions. If there are no expansions before then, the attack is abandoned. This type of attacking is exclusive with `attack_prepare`.

### `set_attacks`
`set_attacks(count)` — Sets the number of attacks possible to execute with `target_expansion` to `count`. Decreased by one after each expansion attack. Cannot be used if the campaign flag is set.

### `send_suicide`
`send_suicide(type)` — Send all units on a suicide mission. `type` determines which kind: 0 = Strategic suicide, 1 = Random suicide.

### `nuke_rate`
`nuke_rate(minutes)` — Tells the AI to try to launch nukes every `minutes` minutes. The timer resets only after the nuke launching procedure has started.

### `fake_nuke`
`fake_nuke()` — Resets the AI nuke timer as if a nuke was launched.

## Defense
The defense commands come in four variants, one for each combination of the enemy unit type attacking and your unit type being attacked: `gg` = enemy ground attacker against your ground units, `ag` = enemy air attacker against your ground units, `ga` = enemy ground attacker against your air units, and `aa` = enemy air attacker against your air units.

### `defensebuild_gg`
`defensebuild_gg(count, gg_military)` — Build `count` of the unit at a time to defend against enemy attacking ground units, when they are located in pathable regions.

### `defensebuild_ag`
`defensebuild_ag(count, ag_military)` — Build `count` of the unit at a time to defend against enemy attacking air units, when they are located in pathable regions.

### `defensebuild_ga`
`defensebuild_ga(count, ga_military)` — Build `count` of the unit at a time to defend against enemy units, when they are located in unpathable regions that do not contain air units.

### `defensebuild_aa`
`defensebuild_aa(count, aa_military)` — Build `count` of the unit at a time to defend against enemy attacking air units, when they are located in unpathable regions.

### `defenseuse_gg`
`defenseuse_gg(count, gg_military)` — Use `count` of the unit at a time to defend against enemy attacking ground units, when they are located in pathable regions.

### `defenseuse_ag`
`defenseuse_ag(count, ag_military)` — Use `count` of the unit at a time to defend against enemy attacking air units, when they are located in pathable regions.

### `defenseuse_ga`
`defenseuse_ga(count, ga_military)` — Use `count` of the unit at a time to defend against enemy units, when they are located in unpathable regions that do not contain air units.

### `defenseuse_aa`
`defenseuse_aa(count, aa_military)` — Use `count` of the unit at a time to defend against enemy attacking air units, when they are located in unpathable regions.

### `defenseclear_gg`
`defenseclear_gg()` — Clear the `defenseuse_gg` and `defensebuild_gg` lists.

### `defenseclear_ag`
`defenseclear_ag()` — Clear the `defenseuse_ag` and `defensebuild_ag` lists.

### `defenseclear_ga`
`defenseclear_ga()` — Clear the `defenseuse_ga` and `defensebuild_ga` lists.

### `defenseclear_aa`
`defenseclear_aa()` — Clear the `defenseuse_aa` and `defensebuild_aa` lists.

### `max_force`
`max_force(force)` — Lets the AI use up to `force` worth of units to defend any given defensible region. Force is determined for every unit using the standard calculation (see PyDAT's AI Actions tab under [units.dat](/Help/Files/DAT/units.dat.md)).

### `clear_combatdata`
`clear_combatdata()` — Clear AI military order data for all units in the location.

### `help_iftrouble`
`help_iftrouble()` — Once, set a flag that creates state 4 (help) regions around this player's buildings for all computer players allied to this player. Once they have been defended, `help_iftrouble` can be requested again.

## Flow Control

### `goto`
`goto(block)` — Jump to `block`.

### `call`
`call(block)` — Call `block` as a sub-routine. Normally only one sub-routine can be active at a time.

### `return`
`return()` — Return to the flow point of the `call` command.

### `stop`
`stop()` — Stop script code execution. Often used to close script blocks called simultaneously.

### `wait`
`wait(time)` — Wait for `time` frames. Normal game speed runs at 15 frames per second.

### `multirun`
`multirun(block)` — Run code at `block` simultaneously (in another thread). The new thread is assigned to the same town the `multirun` originates from.

### `kill_thread`
`kill_thread()` — Kill all threads marked as killable for all players.

### `killable`
`killable()` — Allows the current thread to be killed by another one.

### `random_jump`
`random_jump(chance, block)` — There is `chance` chances out of 256 to jump to `block`.

### `time_jump`
`time_jump(minutes, block)` — Jumps to `block` if `minutes` normal game minutes have passed in the game.

### `race_jump`
`race_jump(terran, zerg, protoss)` — According to the closest enemy's race, jump to `terran` if the enemy is Terran, `zerg` if Zerg, or `protoss` if Protoss.

### `notowns_jump`
`notowns_jump(unit, block)` — If the computer doesn't have a `unit`, jump to `block`.

### `groundmap_jump`
`groundmap_jump(block)` — If the closest enemy is reachable without transports (via pathable regions), jump to `block`.

### `resources_jump`
`resources_jump(minerals, gas, block)` — If the computer has at least `minerals` minerals and `gas` gas, then jump to `block`.

### `enemyowns_jump`
`enemyowns_jump(unit, block)` — If the enemy has a `unit` (unit or building), jump to `block`.

### `enemyresources_jump`
`enemyresources_jump(minerals, gas, block)` — If the closest enemy has at least `minerals` minerals and `gas` gas, then jump to `block`.

### `region_size`
`region_size(size, block)` — Jump to `block` if the town this command is used in has a pathfinder region count (meaning the sum of pathfinder regions connected and pathable by ground) below 32 times `size`.

### `if_owned`
`if_owned(unit, block)` — If the player owns a `unit` (includes incomplete), then jump to `block`.

### `if_dif`
`if_dif(compare, value, block)` — Jumps to `block` if the "AI Difficulty" is LessThan/GreaterThan (`compare`) `value`. AI difficulty is mostly an unused concept: it is always 1, unless the AI has never started a town, in which case it is 0. There is also some unused functionality which would allow the AI to mine more than 8 resources per trip if the difficulty was ever 2.

### `easy_attack`
`easy_attack(count, military)` — Functions the same as `attack_add`, but only if the "AI Difficulty" value is 0. Otherwise it doesn't do anything (see `if_dif` about AI difficulty).

### `rush`
`rush(type, block)` — Depending on `type`, it detects combinations of units and buildings owned by the closest enemy based on their race, and jumps to `block`.

### `debug`
`debug(block, message)` — Print debug string `message` and continue in `block`.

### `fatal_error`
`fatal_error()` — Crashes StarCraft with a fatal error and the message "Illegal AI script executed".

## Campaign Commands
These commands should only be used in campaign scripts:

### `start_campaign`
`start_campaign()` — Sets a Campaign flag for the AI script which modifies AI behaviour. Note that Campaign is always set by default in UMS maps.

### `give_money`
`give_money()` — Give up to 2000 ore and gas if owned resources are low.

### `create_nuke`
`create_nuke()` — Creates a nuke in a free silo. Can be used multiple times as long as there are empty silos.

### `create_unit`
`create_unit(unit, x, y)` — Create `unit` at map position (`x`, `y`).

### `nuke_pos`
`nuke_pos(x, y)` — Order a free Ghost to launch a nuke at map position (`x`, `y`).

### `switch_rescue`
`switch_rescue()` — Switch the computer to rescuable passive mode.

## StarEdit Location Commands
These commands are made to be used by scripts run from map triggers with the "Run AI Script at Location" action, and operate on the location the script was run at:

### `player_enemy`
`player_enemy()` — Makes all players in the location an enemy of the trigger owner.

### `player_ally`
`player_ally()` — Makes all players in the location an ally of the trigger owner.

### `value_area`
`value_area()` — Value this area higher. Causes the computer to consider the region in the center of the location for defense. If the AI doesn't control any buildings in the region, it will only be defended once. Doesn't do anything if the region already has enemy units in it.

### `move_dt`
`move_dt()` — Orders the computer to move its Hero Dark Templars to the location. Can crash the game if any Dark Templars are being trained.

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
`harass_location()` — This command is unused.

### `junkyard_dog`
`junkyard_dog()` — Orders units in the location to Junkyard Dog (movement similar to that of a critter, but attacks nearby enemies if possible).

### `disruption_web`
`disruption_web()` — Cast a Disruption Web at the location. The player must have a Corsair with the researched tech.

### `recall_location`
`recall_location()` — Recall at the location. The player must have an Arbiter (not Danimoth) with the researched tech.

## Miscellaneous

### `transports_off`
`transports_off()` — Sets a flag that prevents the AI from building transports or Protoss Observers.

### `check_transports`
`check_transports()` — The AI will request transports and Protoss Observers up to the `define_max` limit (max 5). Otherwise, it only trains up to 3.

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
