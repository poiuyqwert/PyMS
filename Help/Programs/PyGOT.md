# PyGOT
PyGOT is a tool used for editing the Game Template [.got](/Help/Files/GOT.md) files, which contain the settings for the game modes listed in StarCraft, like `Melee`, `Free For All`, and `Greed`. If you are new to game templates, start with the [Creating a Game Template](/Help/Tutorials/Creating_a_Game_Template.md) tutorial.

## Main Window
The window is a single fixed-size form that edits one Game Template at a time. The form is split into three groups — [Template Info](#template-info), [Variation Info](#variation-info), and [Settings](#settings) — and every field is disabled until a template is created or opened. The status bar at the bottom shows status messages and an indicator for unsaved changes.

## Managing Files
- **New** (`Ctrl+N`): Creates a new Game Template with default settings.
- **Open** (`Ctrl+O`): Opens a `.got` file.
- **Save** (`Ctrl+S`) and **Save As** (`Ctrl+Alt+A`): Saves the template to a `.got` file.
- **Export Game Template** (`Ctrl+E`): Saves the template as an editable text file, with a reference at the top listing the options for each setting.
- **Import Game Template** (`Ctrl+I`): Loads the text format produced by **Export Game Template** as a new unsaved template.
- **Close** (`Ctrl+W`): Closes the template.
- **Set as default `.got` editor** (Windows Only): Associates `.got` files with PyGOT, so they open in PyGOT when double clicked.

Creating, opening, importing, closing, or exiting asks to save any unsaved changes first.

## Template Info
- **Name**: The name of the Game Template listed in StarCraft. It must fit in 32 bytes when encoded as UTF-8, which is checked when saving.
- **ID**: An ID (0 to 31) used to define the order of the Game Template when it is listed in StarCraft.
- **League ID**: An additional ID (0 to 255) — its exact use by the game is not well understood.

## Variation Info
Some game modes come in multiple variations of the same template — for example `Greed` has a variation for each mineral target. Each variation is its own `.got` file, sharing the same Template Info as the others.

- **Name**: The label for the variation (for example, the one to set the greed amount). This should be the same for each variation of a template, and like the template Name it must fit in 32 bytes when encoded as UTF-8.
- **Display**: The value defining the variation amount (for example, the mineral count for `Greed` or the amount of teams for `Team Vs`).
- **ID**: An ID (0 to 7) used to define the order of the variation when it is listed in StarCraft.
- **Label**: An additional value (0 to 65535) — its exact use by the game is not well understood.
- **Value**: An additional value (0 to 4294967295) — its exact use by the game is not well understood.

## Settings
Each setting is a dropdown. **Victory Conditions** and **Resource Type** also have a value field next to them, which is greyed out unless the selected option uses it.

- **Victory Conditions**: Map Default, Melee, Highest Score, Resources, Capture the Flag, Sudden Death, Slaughter, or One on One. **Resources** and **Slaughter** use the value field for their target amount.
- **Resource Type**: The players starting resources — Map Default, Fixed Value, Low, Medium, High, or Income. **Fixed Value** and **Income** use the value field for their amount.
- **Unit Stats**: Map Default or Standard.
- **Fog of War**: Off, Warcraft 1 Style, or On.
- **Starting Units**: Map Default, Workers Only, or Workers and Center.
- **Starting Positions**: Random or Fixed.
- **Player Types**: Whether the game type allows single player games and/or AI players — No Single, No AI; No Single, AI; Single, No AI; or Single, AI.
- **Allies**: Not Allowed or Allowed.
- **Team Mode**: Off, 2 Teams, 3 Teams, or 4 Teams.
- **Cheat Codes**: Off or On.
- **Tournament Mode**: Off or On.

## TRG Conversion
Game modes are initialized by [.trg](/Help/Files/TRG.md) trigger files, which the game stores in a special headerless "GOT compatible" format alongside its templates. PyGOT converts between the two formats:

- **Convert `*.trg` to GOT compatible** (`Ctrl+T`): Converts a normal `.trg` file (like one made with [PyTRG](/Help/Programs/PyTRG.md)) into the GOT compatible format.
- **Revert GOT compatible `*.trg`** (`Ctrl+Alt+T`): Converts a GOT compatible `.trg` file back into the normal format, so it can be edited with PyTRG.

## Settings Dialog
**Manage Settings** (`Ctrl+M`) opens the settings dialog, where you can change the PyMS window [theme](/Help/Programs/Themes.md).

## Command Line
PyGOT can also be used from the command line to decompile `.got` files to the editable text format and compile them back:

```
PyGOT [options] <inp> [out]
```

- `-d`, `--decompile`: Decompile a GOT file (the default).
- `-c`, `--compile`: Compile a GOT file.
- `-t TRIG`, `--trig TRIG`: When compiling, also compile the given TRG file to a GOT compatible TRG file.
- `-r`, `--reference`: When decompiling, put a reference for the settings at the top of the file (default: Off).
- `--gui FILE`: Opens a file with the GUI.

## See Also
- [GOT](/Help/Files/GOT.md)
- [TRG](/Help/Files/TRG.md)
- [PyTRG](/Help/Programs/PyTRG.md)
- [Creating a Game Template](/Help/Tutorials/Creating_a_Game_Template.md)
