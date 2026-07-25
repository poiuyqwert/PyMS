# Creating Your First Trigger
This tutorial walks through writing a simple trigger with [PyTRG](/Help/Programs/PyTRG.md) — from setting up the game files, to writing, testing, and saving a [.trg](/Help/Files/TRG.md) file. The trigger will thank Player 1 for gathering 100 minerals, then take them away.

## Setting Up PyTRG
PyTRG loads unit names and AI scripts from the games files in your [MPQs](/Help/Files/MPQ.md), so the first step is to point it at them:

1. Open PyTRG and press **Manage `stat_txt.tbl` and `aiscript.bin` files** (`Ctrl+M`). This dialog also opens by itself on startup if any files failed to load.
2. In the **MPQ Settings** tab, add your StarCraft MPQs (for example `StarDat.mpq`, `BrooDat.mpq`, and `patch_rt.mpq` from your StarCraft folder), plus your mods MPQ if you have one.
3. The **File Settings** tab chooses the [data files](/Help/Programs/PyTRG.md#data-files) used for unit names and AI scripts. The defaults load from the MPQs you just added, so you shouldn't need to change anything.
4. Press **Ok**.

## Writing the Trigger
1. Press **New** (`Ctrl+N`) to start a new TRG. The editor is now enabled.
2. Type the following code (see the [TRG Language](/Help/Programs/PyTRG/TRG_Language.md) page for what each part means):

```
String(1):
  You gathered 100 minerals... they're mine now!

Trigger(Player 1):
  Conditions:
    Accumulate(Player 1, At Least, 100, Ore)
  Actions:
    DisplayTextMessage(String 1, Always Display)
    SetResources(Player 1, Subtract, 100, Ore)
    PreserveTrigger()
```

While typing, press `Tab` to autocomplete condition and action names, and hover over a name to see its parameters and description — the same documentation as the [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md) and [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md).
The `PreserveTrigger()` action makes the trigger fire every time Player 1 reaches 100 ore, instead of only once.

## Testing Your Code
1. Press **Test Code** (`Ctrl+T`). If there are problems, the lines are highlighted in the editor and the errors are explained — use `Alt+Left` and `Alt+Right` to jump between them.
2. Fix any problems and test again until you are told the code compiles with no errors or warnings.

## Saving Your Changes
1. Press **Save** (`Ctrl+S`) and choose where to save your `.trg` file. Saving compiles the code, so it can also report errors like **Test Code** does.

You can also share triggers as plain text with **Export TRG** (`Ctrl+E`) and **Import TRG** (`Ctrl+I`).

## Using It In the Game
A `.trg` file can be imported into a [map](/Help/Files/Maps.md) using a map editor or plugin that supports the format (like FaRTy1billion's TrigPlug for StarEdit). The other use for `.trg` files is initializing [game modes](/Help/Files/GOT.md): those are saved with **Save `*.got` Compatable `*.trg`** (`Ctrl+G`) and stored at `triggers\*.trg` in your mods MPQ, where a game template made with [PyGOT](/Help/Programs/PyGOT.md) can reference them.

## See Also
- [PyTRG](/Help/Programs/PyTRG.md)
- [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md)
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md)
- [TRG](/Help/Files/TRG.md)
- [GOT](/Help/Files/GOT.md)
