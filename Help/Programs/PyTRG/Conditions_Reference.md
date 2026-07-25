# Conditions Reference
This page documents every condition that can be used in the `Conditions:` section of a trigger (see [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)). The same documentation is shown as tooltips when hovering a condition in the [Code Editor](/Help/Programs/PyTRG/Code_Editor.md).
The names in each signature are the types of the parameters, listed in [Parameter Types](#parameter-types). Conditions that check "current player" are evaluated for each player the trigger runs for.

## Conditions

### NoCondition
`NoCondition()` — No condition. A trigger with no conditions decompiles with a `NoCondition()`, and they are dropped when compiling.

### CountdownTimer
`CountdownTimer(Comparison, Number)` — Countdown timer is `Comparison` `Number` game seconds.

### Command
`Command(Player, Comparison, Number, TUnit)` — `Player` commands `Comparison` `Number` `TUnit`.

### Bring
`Bring(Player, Comparison, Number, TUnit, Location)` — `Player` brings `Comparison` `Number` `TUnit` to `Location`.

### Accumulate
`Accumulate(Player, Comparison, Number, ResType)` — `Player` accumulates `Comparison` `Number` `ResType`.

### Kill
`Kill(Player, Comparison, Number, TUnit)` — `Player` kills `Comparison` `Number` `TUnit`.

### CommandTheMost
`CommandTheMost(TUnit)` — Current player commands the most `TUnit`.

### CommandsTheMostAt
`CommandsTheMostAt(TUnit, Location)` — Current player commands the most `TUnit` at `Location`.

### MostKills
`MostKills(TUnit)` — Current player has most kills of `TUnit`.

### HighestScore
`HighestScore(ScoreType)` — Current player has highest `ScoreType`.

### MostResources
`MostResources(ResType)` — Current player has most `ResType`.

### Switch
`Switch(Switch, SwitchState)` — `Switch` is `SwitchState`.

### ElapsedTime
`ElapsedTime(Comparison, Number)` — Elapsed scenario time is `Comparison` `Number` game seconds.

### Opponents
`Opponents(Player, Comparison, Number)` — `Player` has `Comparison` `Number` opponents remaining in the game.

### Deaths
`Deaths(Player, TUnit, Comparison, Number)` — `Player` has suffered `Comparison` `Number` deaths of `TUnit`.

### CommandTheLeast
`CommandTheLeast(TUnit)` — Current player commands the least `TUnit`.

### CommandTheLeastAt
`CommandTheLeastAt(TUnit, Location)` — Current player commands the least `TUnit` at `Location`.

### LeastKills
`LeastKills(TUnit)` — Current player has least kills of `TUnit`.

### LowestScore
`LowestScore(ScoreType)` — Current player has lowest `ScoreType`.

### LeastResources
`LeastResources(ResType)` — Current player has least `ResType`.

### Score
`Score(Player, Comparison, Number, ScoreType)` — `Player` `ScoreType` score is `Comparison` `Number`.

### Always
`Always()` — Always.

### Never
`Never()` — Never.

### Memory
`Memory(Memory, Comparison, Number, Mask)` — Check the value at memory address `Memory` is `Comparison` `Number`, masked with `Mask`. This is an extended form of the Deaths condition (see [Memory and Raw Values](/Help/Programs/PyTRG/TRG_Language.md#memory-and-raw-values)).

### RawCondition
`RawCondition(Long(1), Long(2), Long(3), Short, Byte(1), Byte(2), Byte(3), Byte(4))` — Create a condition directly from its raw field values (see [Memory and Raw Values](/Help/Programs/PyTRG/TRG_Language.md#memory-and-raw-values)).

## Parameter Types

### Number Type
`Number` — Any number in the range 0 to 4294967295.

### Player Type
`Player` — A number in the range 0 to 255 (with or without the keyword `Player` before it), or any keyword from this list: `Current Player`, `Foes`, `Allies`, `Neutral Players`, `All Players`, `Force 1` to `Force 4`, `Unused 1` to `Unused 4`, `Non Allied Victory Players`.

### Comparison Type
`Comparison` — One of the keywords: `At Least`, `Exactly`, `At Most`.

### TUnit Type
`TUnit` — A unit ID from 0 to 227 (and extended unit IDs 233 to 65535), a full unit name from `stat_txt.tbl`, or a type from the list: `None`, `Any Unit`, `Men`, `Buildings`, `Factories`.

### Location Type
`Location` — A number in the range 0 to 254 (with or without the keyword `Location` before it), or the keyword `Anywhere` (which is location 63).

### ResType Type
`ResType` — One of the keywords: `Ore`, `Gas`, `Ore and Gas`.

### ScoreType Type
`ScoreType` — One of the keywords: `Total`, `Units`, `Buildings`, `Units and Buildings`, `Kills`, `Razings`, `Kills and Razings`, `Custom`.

### Switch Type
`Switch` — A number in the range 0 to 255 (with or without the keyword `Switch` before it).

### SwitchState Type
`SwitchState` — Either the keyword `Set`, or `Cleared`.

### Memory Type
`Memory` — A memory address in hex (prefixed with `0x`), or decimal. The address must be a multiple of 4.

### Mask Type
`Mask` — A value to mask against, in hex (prefixed with `0x`) or decimal, or the keyword `No Mask`.

### Long Type
`Long` — Any number in the range 0 to 4294967295.

### Short Type
`Short` — Any number in the range 0 to 65535.

### Byte Type
`Byte` — Any number in the range 0 to 255.

## See Also
- [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md)
- [Code Editor](/Help/Programs/PyTRG/Code_Editor.md)
