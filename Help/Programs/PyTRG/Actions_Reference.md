# Actions Reference
This page documents every action that can be used in the `Actions:` section of a trigger, and the [briefing actions](#briefing-actions) used in `BriefingTrigger` blocks (see [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)). The same documentation is shown as tooltips when hovering an action in the [Code Editor](/Help/Programs/PyTRG/Code_Editor.md).
The names in each signature are the types of the parameters, listed in [Parameter Types](#parameter-types). "Current player" means each player the trigger runs for.

## Actions

### NoAction
`NoAction()` — No action. A trigger with no actions decompiles with a `NoAction()`, and they are dropped when compiling.

### Victory
`Victory()` — End scenario in victory for current player.

### Defeat
`Defeat()` — End scenario in defeat for current player.

### PreserveTrigger
`PreserveTrigger()` — Preserve the trigger, so it can run again instead of only firing once.

### Wait
`Wait(Time)` — Wait for `Time` milliseconds.

### PauseGame
`PauseGame()` — Pause the game.

### UnpauseGame
`UnpauseGame()` — Unpause the game.

### Transmission
`Transmission(String, Display, WAV, Time(1), Unit, Location, Modifier, Time(2))` — Send transmission to current player from `Unit` at `Location`. Play `WAV` with duration `Time(1)`. Modify transmission duration: `Modifier` `Time(2)` milliseconds. Display `String` when `Display`.

### PlayWAV
`PlayWAV(WAV, Time)` — Play `WAV` with duration `Time`.

### DisplayTextMessage
`DisplayTextMessage(String, Display)` — Display `String` for current player when `Display`.

### CenterView
`CenterView(Location)` — Center view for current player at `Location`.

### CreateUnitWithProperties
`CreateUnitWithProperties(Player, Quantity, Unit, Location, Properties)` — Create `Quantity` `Unit` at `Location` for `Player`. Apply `Properties` (see [Unit Properties](/Help/Programs/PyTRG/TRG_Language.md#unit-properties)).

### SetMissionObjectives
`SetMissionObjectives(String)` — Set mission objectives to `String`.

### SetSwitch
`SetSwitch(Switch, SwitchAction)` — Modify switch: `SwitchAction` `Switch`.

### SetCountdownTimer
`SetCountdownTimer(Modifier, Time)` — Modify countdown timer: `Modifier` `Time` seconds.

### RunAIScript
`RunAIScript(AIScript)` — Execute AI Script `AIScript`.

### RunAIScriptAtLocation
`RunAIScriptAtLocation(AIScript, Location)` — Execute AI Script `AIScript` at `Location`.

### LeaderboardControl
`LeaderboardControl(String, TUnit)` — Show Leader Board for most control of `TUnit`. Display label `String`.

### LeaderboardControlAtLocation
`LeaderboardControlAtLocation(String, TUnit, Location)` — Show Leader Board for most control of `TUnit` at `Location`. Display label `String`.

### LeaderboardResources
`LeaderboardResources(String, ResType)` — Show Leader Board for accumulation of most `ResType`. Display label `String`.

### LeaderboardKills
`LeaderboardKills(String, TUnit)` — Show Leader Board for accumulation of most kills of `TUnit`. Display label `String`.

### LeaderboardPoints
`LeaderboardPoints(String, ScoreType)` — Show Leader Board for accumulation of most `ScoreType` points. Display label `String`.

### KillUnit
`KillUnit(Player, TUnit)` — Kill all `TUnit` for `Player`.

### KillUnitsAtLocation
`KillUnitsAtLocation(Player, Quantity, TUnit, Location)` — Kill `Quantity` `TUnit` for `Player` at `Location`.

### RemoveUnit
`RemoveUnit(Player, TUnit)` — Remove all `TUnit` for `Player`.

### RemoveUnitsAtLocation
`RemoveUnitsAtLocation(Player, Quantity, TUnit, Location)` — Remove `Quantity` `TUnit` for `Player` at `Location`.

### SetResources
`SetResources(Player, Modifier, Number, ResType)` — Modify resources for `Player`: `Modifier` `Number` of `ResType`.

### SetScore
`SetScore(Player, Modifier, Number, ScoreType)` — Modify score for `Player`: `Modifier` `Number` of `ScoreType`.

### MinimapPing
`MinimapPing(Location)` — Show minimap ping for current player at `Location`.

### TalkingPortrait
`TalkingPortrait(Unit, Time)` — Show `Unit` talking to current player for `Time` milliseconds.

### MuteUnitSpeech
`MuteUnitSpeech()` — Mute all non-trigger unit sounds for current player.

### UnmuteUnitSpeech
`UnmuteUnitSpeech()` — Unmute all non-trigger unit sounds for current player.

### LeaderboardComputerPlayers
`LeaderboardComputerPlayers(StateAction)` — Set use of computer players in leaderboard calculations to `StateAction`.

### LeaderboardGoalControl
`LeaderboardGoalControl(String, Number, TUnit)` — Show Leader Board for player closest to control of `Number` of `TUnit`. Display label `String`.

### LeaderboardGoalControlAtLocation
`LeaderboardGoalControlAtLocation(String, Number, TUnit, Location)` — Show Leader Board for player closest to control of `Number` of `TUnit` at `Location`. Display label `String`.

### LeaderboardGoalResources
`LeaderboardGoalResources(String, Number, ResType)` — Show Leader Board for player closest to accumulation of `Number` `ResType`. Display label `String`.

### LeaderboardGoalKills
`LeaderboardGoalKills(String, Number, TUnit)` — Show Leader Board for player closest to `Number` kills of `TUnit`. Display label `String`.

### LeaderboardGoalPoints
`LeaderboardGoalPoints(String, Number, ScoreType)` — Show Leader Board for player closest to `Number` of `ScoreType`. Display label `String`.

### MoveLocation
`MoveLocation(Player, TUnit, Location(1), Location(2))` — Center location `Location(1)` on `TUnit` owned by `Player` at `Location(2)`.

### MoveUnit
`MoveUnit(Player, Quantity, TUnit, Location(1), Location(2))` — Move `Quantity` `TUnit` for `Player` at `Location(2)` to `Location(1)`.

### LeaderboardGreed
`LeaderboardGreed(Number)` — Show Greed Leader Board for player closest to accumulation of `Number` ore and gas.

### SetNextScenario
`SetNextScenario(String)` — Load scenario `String` after completion of current game.

### SetDoodadState
`SetDoodadState(Player, TUnit, Location, StateAction)` — Set doodad state for `TUnit` for `Player` at `Location` to `StateAction`.

### SetInvincibility
`SetInvincibility(Player, TUnit, Location, StateAction)` — Set invincibility for `TUnit` owned by `Player` at `Location` to `StateAction`.

### CreateUnit
`CreateUnit(Player, Quantity, Unit, Location)` — Create `Quantity` `Unit` at `Location` for `Player`.

### SetDeaths
`SetDeaths(Player, TUnit, Modifier, Number)` — Modify death counts for `Player`: `Modifier` `Number` for `TUnit`.

### Order
`Order(Player, TUnit, Location(1), Order, Location(2))` — Issue order to all `TUnit` owned by `Player` at `Location(1)`: `Order` to `Location(2)`.

### Comment
`Comment(String)` — Comment: `String`.

### GiveUnitsToPlayer
`GiveUnitsToPlayer(Player(1), Player(2), Quantity, TUnit, Location)` — Give `Quantity` `TUnit` owned by `Player(1)` at `Location` to `Player(2)`.

### ModifyUnitHitPoints
`ModifyUnitHitPoints(Player, Quantity, TUnit, Location, Percentage)` — Set hit points for `Quantity` `TUnit` owned by `Player` at `Location` to `Percentage`.

### ModifyUnitEnergy
`ModifyUnitEnergy(Player, Quantity, TUnit, Location, Percentage)` — Set energy points for `Quantity` `TUnit` owned by `Player` at `Location` to `Percentage`.

### ModifyUnitShieldPoints
`ModifyUnitShieldPoints(Player, Quantity, TUnit, Location, Percentage)` — Set shield points for `Quantity` `TUnit` owned by `Player` at `Location` to `Percentage`.

### ModifyUnitResourceAmount
`ModifyUnitResourceAmount(Player, Quantity, Location, Number)` — Set resource amount for `Quantity` resource sources owned by `Player` at `Location` to `Number`.

### ModifyUnitHangerCount
`ModifyUnitHangerCount(Player, Quantity, TUnit, Location, Number)` — Add at most `Number` to hangar for `Quantity` `TUnit` at `Location` owned by `Player`.

### PauseTimer
`PauseTimer()` — Pause the countdown timer.

### UnpauseTimer
`UnpauseTimer()` — Unpause the countdown timer.

### Draw
`Draw()` — End the scenario in a draw for all players.

### SetAllianceStatus
`SetAllianceStatus(Player, AllyStatus)` — Set `Player` to `AllyStatus`.

### DisableDebugMode
`DisableDebugMode()` — Disable debug mode (does nothing?).

### EnableDebugMode
`EnableDebugMode()` — Enable debug mode (does nothing?).

### SetMemory
`SetMemory(Memory, Modifier, Number, Mask)` — Modify the value at memory address `Memory`: `Modifier` `Number`, masked with `Mask`. This is an extended form of the SetDeaths action (see [Memory and Raw Values](/Help/Programs/PyTRG/TRG_Language.md#memory-and-raw-values)).

### RawAction
`RawAction(Long(1), Long(2), Long(3), Long(4), Long(5), Long(6), Short, Byte(1), Byte(2))` — Create an action directly from its raw field values (see [Memory and Raw Values](/Help/Programs/PyTRG/TRG_Language.md#memory-and-raw-values)).

## Briefing Actions
These actions are used in `BriefingTrigger` blocks (see [Mission Briefings](/Help/Programs/PyTRG/TRG_Language.md#mission-briefings)). Portraits are shown in one of four slots on the briefing screen.

### NoAction (Briefing)
`NoAction()` — No action.

### Wait (Briefing)
`Wait(Time)` — Wait for `Time` milliseconds.

### PlayWAV (Briefing)
`PlayWAV(WAV, Time)` — Play `WAV` with duration `Time`.

### DisplayTextMessage (Briefing)
`DisplayTextMessage(String, Time)` — Display `String` for current player for `Time` milliseconds.

### SetMissionObjectives (Briefing)
`SetMissionObjectives(String)` — Set mission objectives to `String`.

### ShowPortrait
`ShowPortrait(Unit, Slot)` — Show portrait of `Unit` in `Slot`.

### HidePortrait
`HidePortrait(Slot)` — Hide portrait in `Slot`.

### DisplaySpeakingPortrait
`DisplaySpeakingPortrait(Slot, Time)` — Display speaking portrait in `Slot` for `Time` milliseconds.

### Transmission (Briefing)
`Transmission(String, Slot, WAV, Time(1), Modifier, Time(2))` — Send transmission to current player in `Slot`. Play `WAV` with duration `Time(1)`. Modify transmission duration: `Modifier` `Time(2)` milliseconds. Display `String`.

### SkipTutorialEnabled
`SkipTutorialEnabled()` — Show the Skip Tutorial button in the briefing UI.

### RawAction (Briefing)
`RawAction(Long(1), Long(2), Long(3), Long(4), Long(5), Long(6), Short, Byte(1), Byte(2))` — Create a briefing action directly from its raw field values.

## Parameter Types

### Number Type
`Number` — Any number in the range 0 to 4294967295.

### Player Type
`Player` — A number in the range 0 to 255 (with or without the keyword `Player` before it), or any keyword from this list: `Current Player`, `Foes`, `Allies`, `Neutral Players`, `All Players`, `Force 1` to `Force 4`, `Unused 1` to `Unused 4`, `Non Allied Victory Players`.

### TUnit Type
`TUnit` — A unit ID from 0 to 227 (and extended unit IDs 233 to 65535), a full unit name from `stat_txt.tbl`, or a type from the list: `None`, `Any Unit`, `Men`, `Buildings`, `Factories`.

### Unit Type
`Unit` — A unit ID from 0 to 227 (and extended unit IDs 233 to 65535), or a full unit name from `stat_txt.tbl`.

### Location Type
`Location` — A number in the range 0 to 254 (with or without the keyword `Location` before it), or the keyword `Anywhere` (which is location 63).

### ResType Type
`ResType` — One of the keywords: `Ore`, `Gas`, `Ore and Gas`.

### ScoreType Type
`ScoreType` — One of the keywords: `Total`, `Units`, `Buildings`, `Units and Buildings`, `Kills`, `Razings`, `Kills and Razings`, `Custom`.

### Switch Type
`Switch` — A number in the range 0 to 255 (with or without the keyword `Switch` before it).

### Time Type
`Time` — Any number in the range 0 to 4294967295.

### String Type
`String` — A number corresponding to a string index (with or without the keyword `String` before it), or the keyword `No String`. Strings are defined in [String blocks](/Help/Programs/PyTRG/TRG_Language.md#strings).

### Modifier Type
`Modifier` — One of the keywords: `Set To`, `Add`, `Subtract`.

### WAV Type
`WAV` — A number corresponding to a WAV string index (with or without the keyword `WAV` before it), or the keyword `No WAV`.

### Display Type
`Display` — Either the keyword `Always Display`, or `Only With Subtitles`.

### Quantity Type
`Quantity` — Any number in the range 1 to 4294967295, or the keyword `All`.

### Properties Type
`Properties` — A number corresponding to a [Unit Properties](/Help/Programs/PyTRG/TRG_Language.md#unit-properties) id from 1 to 64 (with or without the keyword `Properties` before it).

### SwitchAction Type
`SwitchAction` — One of the keywords: `Set`, `Clear`, `Toggle`, `Randomize`.

### StateAction Type
`StateAction` — One of the keywords: `Set`, `Clear`, `Toggle`.

### AIScript Type
`AIScript` — The four character ID of an AI script (autocomplete in the [Code Editor](/Help/Programs/PyTRG/Code_Editor.md) suggests the IDs from your `aiscript.bin`/`bwscript.bin`).

### Order Type
`Order` — One of the keywords: `Move`, `Patrol`, `Attack`.

### Percentage Type
`Percentage` — A number from 0 to 100 (with or without a trailing `%`).

### AllyStatus Type
`AllyStatus` — One of the keywords: `Enemy`, `Ally`, `Allied Victory`.

### Slot Type
`Slot` — A number from 1 to 4 (with or without the keyword `Slot` before it).

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
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md)
- [Code Editor](/Help/Programs/PyTRG/Code_Editor.md)
