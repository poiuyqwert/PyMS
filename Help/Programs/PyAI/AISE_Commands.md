# AISE Commands
AISE (AI Script Extension) is a third party plugin for the game which extends the AI language with new commands, and allows `aiscript.bin`/`bwscript.bin` to be "expanded" past the normal 65535 byte size limit. Search for "AISE Plugin" to find and learn more about the plugin itself.
Using any of these commands (or expanding a file) makes the saved files require the AISE plugin to be installed in the game — PyAI will ask for confirmation before compiling changes that add the requirement (see [Plugins](/Help/Programs/PyAI.md#plugins)).
Signatures are shown in the parenthesis command style, using the AISE parameter types listed in [Parameter Types](#parameter-types) (plus the core types from the [Command Reference](/Help/Programs/PyAI/Command_Reference.md#parameter-types)). Some commands are not documented yet — for those, the signature simply lists the type of each parameter.

## Commands

### `attack_to`
`attack_to(prepare_point, attack_point)` — Prepare an attack at the region of `prepare_point` and attack to the region of `attack_point`.

### `attack_timeout`
`attack_timeout(dword)` — Not yet documented.

### `ai_order`
`ai_order(order, count, units, area, target_area, target_units, flags)` — Issue order `order` for at most `count` units owned by the current player matching type `units` at `area`, targeting `target_area` with target unit type `target_units` and `flags`.

### `deaths`
`deaths(player, modifier, count, units, block)` — Either jump to `block` based on comparing the deaths suffered by `player` of `units` to `count` using `modifier`, or modify the said deaths.

### `idle_orders`
`idle_orders(order, rate, max_count, units, max_distance, targets, priority, flags)` — Set idle order `order` for the AI controlled units matching `units` targeting `targets`, executed every `rate` frames, with a maximum of `max_count` units targeting a single target and a maximum distance of `max_distance`. `priority` sets the priority relative to other idle orders.

### `if_attacking`
`if_attacking(block)` — Jumps to `block` if the AI is currently preparing an attack.

### `unstart_campaign`
`unstart_campaign()` — Clears the campaign flag.

### `max_workers`
`max_workers(count)` — Sets the maximum workers for the current town. 255 to restore the default logic.

### `under_attack`
`under_attack(attack_mode)` — Sets the mode for the AI-under-attack variable.

### `aicontrol`
`aicontrol(ai_control)` — Not yet documented (see the `ai_control` type for the available settings).

### `bring_jump`
`bring_jump(player, comparison, count, units, area, block)` — Identical to the "Bring" trigger condition, jumps as the action.

### `create_script`
`create_script(block, player, area, town, resarea)` — Creates a new thread running at `block` with the given player, area, town, and resource area. To use the values from the current thread, pass `player` = 255, `area` = (65534, 65534), `town` = 255, `resarea` = 255.

### `player_jump`
`player_jump(string, block)` — Not yet documented.

### `aise_kills`
`aise_kills(byte, byte, compare_trig, dword, unit_group, block)` — Not yet documented.

### `wait_rand`
`wait_rand(dword, dword)` — Not yet documented.

### `upgrade_jump`
`upgrade_jump(byte, compare_trig, upgrade, byte, block)` — Not yet documented.

### `tech_jump`
`tech_jump(byte, compare_trig, technology, byte, block)` — Not yet documented.

### `random_call`
`random_call(byte, block)` — Not yet documented.

### `attack_rand`
`attack_rand(byte, byte, military)` — Not yet documented.

### `supply`
`supply(byte, compare_trig, word, supply, unit_group, race, block)` — Not yet documented.

### `time`
`time(compare_trig, dword, time_type, block)` — Not yet documented.

### `resources`
`resources(byte, compare_trig, resource, dword, block)` — Not yet documented.

### `set_id`
`set_id(byte)` — Not yet documented.

### `remove_build`
`remove_build(byte, unit_group, byte)` — Not yet documented.

### `guard`
`guard(unit, point, byte, byte, byte)` — Not yet documented.

### `base_layout_old`
`base_layout_old(unit, layout_action, area, byte, byte)` — Not yet documented.

### `print`
`print(message)` — Print `message`.

### `attacking`
`attacking(bool_compare, block)` — Not yet documented.

### `base_layout`
`base_layout(unit, layout_action, area, byte, byte, byte)` — Not yet documented.

### `unit_avail`
`unit_avail(byte, compare_trig, availability, unit, block)` — Not yet documented.

### `load_bunkers`
`load_bunkers(area, unit, byte, unit, byte, byte)` — Not yet documented.

### `ping`
`ping(word, word, byte)` — Not yet documented.

### `reveal_area`
`reveal_area(byte, area, word, reveal_type)` — Not yet documented.

### `tech_avail`
`tech_avail(byte, compare_trig, technology, byte, block)` — Not yet documented.

### `remove_creep`
`remove_creep(area)` — Not yet documented.

### `save_bank`
`save_bank(string)` — Not yet documented.

### `load_bank`
`load_bank(string)` — Not yet documented.

### `bank_data_old`
`bank_data_old(compare_trig, string, string, dword, block)` — Not yet documented.

### `unit_name`
`unit_name(byte, unit, area, string, layout_action)` — Not yet documented.

### `bank_data`
`bank_data(compare_trig, dword, string, string, block)` — Not yet documented.

### `lift_land`
`lift_land(unit, byte, area, area, byte, byte)` — Not yet documented.

### `queue`
`queue(byte, unit, unit, byte, queue_flags, area, byte)` — Not yet documented.

### `aise_debug`
`aise_debug(string)` — Not yet documented.

### `replace_unit`
`replace_unit(unit, unit)` — Not yet documented.

### `defense`
`defense(word, unit, defense_type, defense_direction, defense_direction)` — Not yet documented.

### `bw_kills`
`bw_kills(byte, compare_trig, dword, unit_group, block)` — Not yet documented.

### `build_at`
`build_at(unit_group, build_at_point, build_at_flags)` — Not yet documented.

### `debug_name`
`debug_name(string)` — Not yet documented.

## Parameter Types
AISE commands use the core parameter types (see the [Command Reference](/Help/Programs/PyAI/Command_Reference.md#parameter-types)) plus the following:

### Point Type
`point` — A point, either `(x, y)`, `Loc.{location id}`, or `ScriptArea`.

### Order Type
`order` — An order ID from 0 to 188, or an order name (like `AttackMove` or `Patrol`).

### Unit ID Type
`unit_id` — Same as the `unit` type, but also accepts: `None` (228), `Any` (229), `Group_Men` (230), `Group_Buildings` (231), `Group_Factories` (232).

### Unit Group Type
`unit_group` — Same as `unit_id`, but allows multiple separated with `|`.

### Area Type
`area` — An area in the form `point ~ radius` (the `~ radius` part is optional).

### Issue Order Flags Type
`issue_order_flags` — An integer/hex flag, or any of: `Enemies`, `Own`, `Allied`, `SingleUnit`, `EachAtMostOnce`, `IgnoreDatReqs`.

### Compare Trig Type
`compare_trig` — One of: `AtLeast`, `AtMost`, `Set`, `Add`, `Subtract`, `Exactly`, `Randomize`, `AtLeast_Call`, `AtMost_Call`, `Exactly_Call`, `AtLeast_Wait`, `AtMost_Wait`, `Exactly_Wait`.

### Idle Order Type
`idle_order` — An order ID from 0 to 188, an order name, or `DisableBuiltin`/`EnableBuiltin`.

### Idle Order Flags Type
`idle_order_flags` — Any of: `NotEnemies`, `Own`, `Allied`, `Unseen`, `Invisible`, `RemoveSilentFail`, `Remove`.

### Attack Mode Type
`attack_mode` — The state of whether the AI is under attack, one of: `Always`, `Default`, `Never`.

### AI Control Type
`ai_control` — One of: `wait_request_resources`, `dont_wait_request_resources`, `build_gas`, `dont_build_gas`, `retaliation`, `no_retaliation`, `focus_disabled_units`, `dont_focus_disabled_units`, `global_enable_spell_focus`, `global_disable_spell_focus`, `global_enable_acid_spore_focus`, `global_disable_acid_spore_focus`, `global_enable_carrier_focus`, `global_disable_carrier_focus`.

### Supply Type
`supply` — One of: `Provided`, `Used`, `Max`, `InUnits`.

### Race Type
`race` — One of: `Zerg`, `Terran`, `Protoss`, `Any_Total`, `Any_Max`.

### Time Type
`time_type` — One of: `Frames` or `Minutes`.

### Resource Type
`resource` — One of: `Ore`, `Gas`, or `Any`.

### Layout Action Type
`layout_action` — One of: `Set` or `Remove`.

### Bool Compare Type
`bool_compare` — One of: `False`, `True`, `False_Wait`, `True_Wait`, `False_Call`, `True_Call`.

### Availability Type
`availability` — One of: `Disabled`, `Enabled`, `Researched`.

### Reveal Type
`reveal_type` — One of: `Reveal` or `RevealFog`.

### Queue Flags Type
`queue_flags` — One of: `Local` or `Global`.

### Defense Type
`defense_type` — One of: `Use` or `Build`.

### Defense Direction Type
`defense_direction` — One of: `Ground` or `Air`.

### Build At Point Type
`build_at_point` — A point, either `(x, y)`, `Loc.{location id}`, `ScriptArea`, or `TownCenter`.

### Build At Flags Type
`build_at_flags` — Any of: `AllowUnreachableRegions`, `NotSafe`, `AnyElevation`, `NearResourceBuildings`, `NearResources`, `DontSpreadOut`, `DontPreferUnpowered`, `IgnoreExtraSpace`, `PreferUnpowered`, `Remove`.

## See Also
- [Command Reference](/Help/Programs/PyAI/Command_Reference.md)
- [AI Language](/Help/Programs/PyAI/AI_Language.md)
