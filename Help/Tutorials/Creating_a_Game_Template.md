# Creating a Game Template
This tutorial walks through creating a custom game mode with [PyGOT](/Help/Programs/PyGOT.md) — from setting up the template and its variations, to getting the files into the game. It creates a `Greed` style game type called `Mineral Rush` as the example, where the first player to gather a target amount of minerals wins.

## Creating the Template
1. Open PyGOT and press **New** (`Ctrl+N`). The fields enable, editing a fresh template.
2. In **Template Info**, set **Name** to `Mineral Rush` — the name the game type is listed under in StarCraft.
3. Set **ID** to a value not used by another game type — it defines where the game type appears in the list.
4. In **Variation Info**, set **Name** to `Mineral Target` — the label for the value that varies between variations. It stays the same for every variation of the template.
5. Set **Display** to `5000` (the variation amount shown in StarCraft), and leave the variation **ID** at `0` so this is the first variation listed.

## Choosing the Settings
1. Set **Victory Conditions** to `Resources`. The value field next to the dropdown enables — set it to `5000`, the amount of resources to gather to win.
2. Set **Resource Type** to `Fixed Value` and its value field to `500`, so every player starts with the same fixed resources.
3. Pick the rest to taste — for example **Starting Units** to `Workers and Center` and **Allies** to `Allowed`. Notice the unsaved changes indicator light up in the status bar as you edit.

## Saving the Variations
1. Press **Save** (`Ctrl+S`) and save the file as `mineral rush(1).got` in a working folder. The games own templates are named like this — for example `greed(1).got` through `greed(4).got` are the variations of `Greed`.
2. To add more variations, change the variation **Display** and the victory condition value to the next target (for example `10000`), set the variation **ID** to `1`, and **Save As** (`Ctrl+Alt+A`) `mineral rush(2).got`.
3. Repeat for as many variations as you want (variation IDs run from 0 to 7).

## Game Triggers
Game modes are initialized by [TRG](/Help/Files/TRG.md) trigger files stored in a special "GOT compatible" format — for example the `Greed` variations use trigger files like `greed5000.trg`. To make one for your game type:

1. Create your triggers with [PyTRG](/Help/Programs/PyTRG.md) and save the `.trg` file.
2. In PyGOT, press **Convert `*.trg` to GOT compatible** (`Ctrl+T`), pick your `.trg` file, then choose where to save the converted file.
3. If you need to edit a converted file later, **Revert GOT compatible `*.trg`** (`Ctrl+Alt+T`) converts it back to the normal format PyTRG edits.

## Using It In the Game
To use the game type in the game, the files need to be in the MPQ your mod loads: the templates at their `templates\` paths (for example `templates\mineral rush(1).got`) and the trigger files at their `triggers\` paths. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add them to your mods MPQ. The next game you play with your mod, `Mineral Rush` will be listed with the standard game types when creating a multiplayer game.

## See Also
- [PyGOT](/Help/Programs/PyGOT.md)
- [GOT](/Help/Files/GOT.md)
- [TRG](/Help/Files/TRG.md)
- [PyTRG](/Help/Programs/PyTRG.md)
- [MPQ](/Help/Files/MPQ.md)
