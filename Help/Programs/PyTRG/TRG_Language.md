# TRG Language
[PyTRG](/Help/Programs/PyTRG.md) decompiles the binary triggers in a [.trg](/Help/Files/TRG.md) file into this text language, and compiles it back. A source file contains one or more `Trigger` blocks (or `BriefingTrigger` blocks for [mission briefings](#mission-briefings)), plus the [String](#strings) and [Unit Properties](#unit-properties) blocks their actions refer to.
Comments run from a `#` to the end of the line.

## Triggers
A trigger declares the players it runs for, the conditions that must be met, and the actions executed when they are:

```
Trigger(Player 1, Force 2):
  Conditions:
    Accumulate(Player 1, At Least, 100, Ore)
  Actions:
    DisplayTextMessage(String 1, Always Display)
    PreserveTrigger()
```

The list of players can contain player numbers (`0` to `26`, with or without the keyword `Player` before them) or the equivalent keywords: `Player 1` to `Player 12`, `Current Player`, `Foes`, `Allies`, `Neutral Players`, `All Players`, `Force 1` to `Force 4`, `Unused 1` to `Unused 4`, and `Non Allied Victory Players`. Each player can only be listed once, and a trigger with no players compiles with a warning (it will never run).
The `Conditions:` section holds up to 16 conditions, and the trigger fires when all of them are met. The `Actions:` section holds up to 64 actions, executed in order. Each condition and action is written as its name followed by its parameters in parenthesis, separated by commas.
Every condition and action is documented in the [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md) and [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md), and the [Code Editor](/Help/Programs/PyTRG/Code_Editor.md) shows the same documentation in tooltips when hovering a name.

## Disabling Conditions and Actions
Prefixing a condition or action with a `-` marks it as disabled — it is kept in the trigger but ignored by the game:

```
Trigger(Player 1):
  Conditions:
    -Switch(Switch 0, Set)
  Actions:
    -Victory()
```

## Parameters
The reference pages describe the [parameter types](/Help/Programs/PyTRG/Conditions_Reference.md#parameter-types) each condition and action takes. Some general rules:

- Units can be written as their full name from `stat_txt.tbl` (like `Terran Marine`) or as their unit ID. Conditions and most actions also accept the group keywords `None`, `Any Unit`, `Men`, `Buildings`, and `Factories`.
- Locations are numbers from `0` to `254`, with or without the keyword `Location` before them, or the keyword `Anywhere` (which is location 63).
- Switches, strings, WAVs, and unit properties are referenced by number, with an optional keyword before it: `Switch 3`, `String 1`, `WAV 2`, `Properties 1`. Strings and WAVs also accept `No String`/`No WAV`.
- Choice parameters are keywords, like `At Least`/`Exactly`/`At Most` for comparisons and `Set To`/`Add`/`Subtract` for modifiers.

## Strings
Actions that display text (or play sounds) refer to strings by index, and each string is defined in its own `String` block:

```
String(1):
  This text is displayed by actions using String 1.
  It can span multiple lines.
```

The text lines must be indented — the indentation of the first line sets the level, and the string ends at the first line that doesn't match it. String index 0 means "no string", so real strings start at index 1, and each index can only be defined once. Special characters are written as [TBL](/Help/Files/TBL.md) format codes like `<3>` (the codes are highlighted in the editor).

## Unit Properties
The CreateUnitWithProperties action applies one of 64 unit property slots to the units it creates. Each slot is defined in a `UnitProperties` block with an id from `1` to `64`:

```
UnitProperties(1):
  Owner(1)
  Health(50)
  Cloaked()
```

Properties with a value: `Owner`, `Health`, `Shields`, and `Energy` (`0` to `255`), `Resources` (`0` to `4294967295`), and `HangerCount` (`0` to `65535`). Properties that are flags take no value: `Cloaked()`, `Burrowed()`, `InTransit()`, `Hallucinated()`, and `Invincible()`.

## Mission Briefings
The triggers for a mission briefing screen are written as `BriefingTrigger` blocks. A briefing trigger has no `Conditions:` or `Actions:` sections — it holds only actions, listed directly under the header line, drawn from a separate set of [briefing actions](/Help/Programs/PyTRG/Actions_Reference.md#briefing-actions):

```
BriefingTrigger():
    ShowPortrait(Terran Marine, Slot 1)
    Transmission(String 1, Slot 1, No WAV, 2000, Set To, 4000)
```

A file contains either normal triggers or briefing triggers — the two cannot be mixed.

## Memory and Raw Values
For advanced use, triggers can work with values outside the normal parameter ranges:

- The Memory condition and SetMemory action read/modify a value at a memory address (an extended form of the Deaths condition and SetDeaths action). Addresses are written in hex (prefixed with `0x`) or decimal, and must be a multiple of 4.
- RawCondition and RawAction build a condition or action directly from its raw field values, for anything the named conditions and actions can't express.

See the [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md) and [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md) for their parameters.

## See Also
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md)
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md)
- [Code Editor](/Help/Programs/PyTRG/Code_Editor.md)
- [Creating Your First Trigger](/Help/Tutorials/Creating_Your_First_Trigger.md)
