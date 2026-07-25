# AI Language
StarCraft's AI script language is a procedural scripting language, similar in structure to assembly: code is organized into labelled blocks, executes top-down, and jumps/calls between blocks. PyAI decompiles the binary scripts in [aiscript.bin](/Help/Files/aiscript.bin.md) into this text language, and compiles it back. For the concepts behind AI scripting itself, see the [AI Basics](/Help/Tutorials/AI_Basics.md) tutorial.
A source file contains one or more scripts. Each script is declared with a `script` header, and its code lives in blocks.

## Script Headers
A script header declares a script and its properties:

```
script MyAI {
    name_string 5
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point MyAI_entry
}
```

The value after `script` is the scripts 4 character AI ID (it cannot contain commas, parenthesis, or colons). The header commands are:

- `name_string`: The index of the scripts name string in `stat_txt.tbl` (the name displayed in StarEdit). This is the index as shown in PyAI, for example by the Insert String ID tool in the [Code Editor](/Help/Programs/PyAI/Code_Editor.md).
- `bin_file`: Which file the script is saved in — either `aiscript` or `bwscript`.
- `broodwar_only`: Set to `1` if the script should only be available in BroodWar, otherwise `0`.
- `staredit_hidden`: Set to `1` if the script should be hidden in StarEdit, otherwise `0`.
- `requires_location`: Set to `1` if the script requires a location, otherwise `0`.
- `entry_point`: The name of the block where the script starts executing.

## Blocks
A block is a named label that code can jump to. Blocks can be written in two styles (both are always accepted; the [Decompiling Format](/Help/Programs/PyAI.md#exporting-and-importing) setting chooses which one PyAI outputs):

```
--MyBlock--
:MyBlock
```

Block names can contain letters, numbers, and underscores. Code execution falls through from one block into the next, unless a command like `goto`, `stop`, or `return` ends the flow. Scripts can reference blocks belonging to other scripts in the same file — when exporting a script that does this, PyAI exports the referenced scripts too.

## Commands
Each line of code is a single command with zero or more parameters. Commands can be written in two styles (both are always accepted):

```
build 5 "Zerg Drone" 80
build(5, Zerg Drone, 80)
```

Every command and its parameters is documented in the [Command Reference](/Help/Programs/PyAI/Command_Reference.md), and the [Code Editor](/Help/Programs/PyAI/Code_Editor.md) shows the same documentation in tooltips when hovering a command.
Parameters that take a unit, upgrade, or technology can be written either as the numeric ID or as the full name from `stat_txt.tbl` (like `Zerg Drone` above). A name containing spaces must be quoted (`"Zerg Drone"`) when the command is not written with parenthesis. Inside parenthesis the quotes can be left off, since the comma or closing parenthesis ends the name — unless the name itself contains a comma/parenthesis, which needs quotes even inside parenthesis (`build(5, "Zerg, Drone", 80)`).
String parameters (like the message of a `debug` command) use TBL string formatting for special characters: `<44>` for a comma, `<40>` and `<41>` for parenthesis, and so on.

## Comments
Comments run from a `#` or `;` to the end of the line (both are always accepted):

```
wait(120) # Wait 5 seconds on Fastest
wait(120) ; Wait 5 seconds on Fastest
```

## Directives
Directives start with `@` and give instructions to the compiler itself rather than to the game:

- `@suppress_all(warning)`: Suppress all warnings with the given warning ID.
- `@suppress_next_line(warning)`: Suppress warnings with the given warning ID on the next line.
- `@expand_units(count)`: Set the maximum unit id to `count` (for use with expanded DAT files).
- `@expand_upgrades(count)`: Set the maximum upgrade id to `count` (for use with expanded DAT files).
- `@expand_tech(count)`: Set the maximum technology id to `count` (for use with expanded DAT files).

### Warning IDs
These are the warning IDs that can be suppressed with `@suppress_all` and `@suppress_next_line`:

- `building` — A [building type](/Help/Programs/PyAI/Command_Reference.md#building-type) parameter was given a unit that is not a Building, Resource Miner, or Overlord.
- `military` — A [military type](/Help/Programs/PyAI/Command_Reference.md#military-type) parameter was given a unit that is a building.
- `gg_military` — A [gg military type](/Help/Programs/PyAI/Command_Reference.md#gg-military-type) parameter was given a unit that has no ground weapon and is not marked as a `@spellcaster` (so it can't defend your ground units against an enemy ground attacker).
- `ag_military` — An [ag military type](/Help/Programs/PyAI/Command_Reference.md#ag-military-type) parameter was given a unit that has no air weapon and is not marked as a `@spellcaster` (so it can't defend your ground units against an enemy air attacker).
- `ga_military` — A [ga military type](/Help/Programs/PyAI/Command_Reference.md#ga-military-type) parameter was given a unit that has no ground weapon and is not marked as a `@spellcaster` (so it can't defend your air units against an enemy ground attacker).
- `aa_military` — An [aa military type](/Help/Programs/PyAI/Command_Reference.md#aa-military-type) parameter was given a unit that has no air weapon and is not marked as a `@spellcaster` (so it can't defend your air units against an enemy air attacker).
- `block_unused` — A block was defined but is never used, so it will be discarded when compiling.
- `raw_flag_unknown` — A flags parameter was given a raw integer/hex value that does not match any known flag.

## Variables
A variable gives a meaningful name to a value. Variables are defined as `type name = value`:

```
military attacker = Zerg Zergling
byte attack_amount = 10
```

Once defined, the variable name can be used anywhere a parameter of that type is expected (see the parameter types in the [Command Reference](/Help/Programs/PyAI/Command_Reference.md#parameter-types)). Variables can be defined in your source code, or in external definition files.

## External Definitions
External definition files are text files containing variable definitions, managed with **Manage External Definition Files** (`Ctrl+X`) in the main window. They are applied every time scripts are compiled or decompiled: when compiling, the variables are available to your code, and when decompiling, values are replaced by their matching variable names — so you can keep one set of meaningful names across all your work.
External definition files can also contain these directives:

- `@spellcaster(variable)`: Mark the unit variable as a spellcaster, so it can be used with the `defenseuse_xx`/`defensebuild_xx` commands without warning that the unit doesn't have an attack.
- `@expand_units(count)`, `@expand_upgrades(count)`, `@expand_tech(count)`: Same as in source code (see [Directives](#directives)).

## Plugins
The commands in the core language are the ones supported by the unmodded game. Plugins add extra commands — PyAI supports the **AISE** plugin, which adds many new commands (see [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)) and allows files to be "expanded" past the normal 65535 byte size limit. Files that use plugin features require the plugin to be installed in the game (see [Plugins](/Help/Programs/PyAI.md#plugins)).

## See Also
- [Command Reference](/Help/Programs/PyAI/Command_Reference.md)
- [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)
- [AI Basics](/Help/Tutorials/AI_Basics.md)
- [Creating Your First AI Script](/Help/Tutorials/Creating_Your_First_AI_Script.md)
