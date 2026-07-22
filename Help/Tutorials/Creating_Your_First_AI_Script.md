# Creating Your First AI Script
This tutorial walks through creating a simple AI script in [PyAI](/Help/Programs/PyAI.md), from opening files to compiling and saving. It focuses on the workflow — for the concepts behind AI scripting, read the [AI Basics](/Help/Tutorials/AI_Basics.md) tutorial, and for the language itself see [AI Language](/Help/Programs/PyAI/AI_Language.md).

## Setting Up
When PyAI starts it loads `stat_txt.tbl`, `units.dat`, `upgrades.dat`, and `techdata.dat` (see [Data Files](/Help/Programs/PyAI.md#data-files)). The defaults bundled with PyMS work fine for unmodded StarCraft — if you are making an AI for a mod, use **Manage Settings** (`Ctrl+U`) to point PyAI at your mod's files so your unit names and IDs match.

## Creating the Script
Start from the games standard scripts so they stay available alongside your new one:

1. Use **Open Default Scripts** (`Ctrl+D`) to open the default `aiscript.bin` and `bwscript.bin`.
2. Use **Add Blank Script** (`Insert`) to create a new script.
3. Give it a 4 character AI ID (this tutorial uses `MyAI`), pick a name string with Browse... if you want one, and leave the flags off (see [Script Flags](/Help/Programs/PyAI.md#script-flags) for what they do).

The new script appears in the list, containing just a `stop()` command.

## Writing the Code
Select your script and press `Ctrl+E` (or double click it) to open it in the [Code Editor](/Help/Programs/PyAI/Code_Editor.md). You'll see the decompiled script: a `script` header describing the script, and its entry point block. Replace all of it with the following simple Terran AI:

```
script MyAI {
    name_string 0
    bin_file aiscript
    broodwar_only 0
    staredit_hidden 0
    requires_location 0
    entry_point MyAI_entry
}

--MyAI_entry--
    start_town()
    farms_timing()
    build(1, Terran Command Center, 80)
    build(8, Terran SCV, 70)
    build(1, Terran Barracks, 80)
    wait_build(1, Terran Barracks)

--MyAI_attack--
    train(8, Terran Marine)
    attack_add(6, Terran Marine)
    attack_prepare()
    attack_do()
    wait_finishattack()
    attack_clear()
    wait(240)
    goto(MyAI_attack)
```

Going through it line by line:

- The `script` header declares the script and its properties (see [Script Headers](/Help/Programs/PyAI/AI_Language.md#script-headers)). `entry_point` says execution starts at the `MyAI_entry` block.
- `start_town()` starts town management for the AI, so it can process build and train requests.
- `farms_timing()` makes the AI build supply with correct timing, instead of only when it hits the supply cap.
- The `build` commands request buildings (and workers): keep 1 Command Center at priority 80, get 8 SCVs at priority 70, and build a Barracks at priority 80.
- `wait_build(1, Terran Barracks)` pauses the script until the Barracks is finished.
- After that, execution simply continues into `MyAI_attack` — a block label doesn't interrupt the flow, so when `MyAI_entry` runs out of commands the script flows straight into the next block. You only need `goto` to jump somewhere other than the next line.
- The `MyAI_attack` block trains Marines, forms an attack party of 6 of them, attacks, waits for the attack to finish, then waits 24 seconds (`wait` is in tenths of a second at normal game speed).
- `goto(MyAI_attack)` jumps back up to the `MyAI_attack` label to loop the attack cycle forever. This is where flowing isn't enough: without the `goto` the script would just run past the end of the block.

Notice you can write units by name (`Terran Marine`) — the names come from your `stat_txt.tbl`. Hover over any command to see its documentation, and press `Tab` to autocomplete names and commands.

## Testing and Saving
Press `Ctrl+T` (**Test Code**) to compile without applying — errors and warnings get highlighted right in the code. When it compiles cleanly, press `Ctrl+S` (**Save**) to compile the code into the loaded files, and close the editor.
Back in the main window, save the files with **Save As...** (`Ctrl+Alt+A`) to write `aiscript.bin` to disk, or **Save MPQ** (`Ctrl+Alt+M`) to write it straight into an MPQ as `scripts\aiscript.bin`.

## Using the Script
To run in the game, your `aiscript.bin` (and `bwscript.bin` if used) must be loaded by the game — typically by putting them in an MPQ that gets loaded by an MPQ patching tool (like MPQDraft) or by your mod's loader.
Since our script left the **Invisible in StarEdit** flag off, it will show up in map editors (with the name string you chose) as an option for the "Run AI Script" trigger actions in Use Map Settings maps. Melee computer players instead pick from the games standard race scripts, so a melee AI mod replaces the code of those existing scripts rather than adding a new one.

## Next Steps
- Read [AI Basics](/Help/Tutorials/AI_Basics.md) to understand towns, requests, flags, and the games AI behaviours (and bugs).
- Browse the [Command Reference](/Help/Programs/PyAI/Command_Reference.md) to see everything the AI can be told to do.
- Use [Export Scripts](/Help/Programs/PyAI.md#exporting-and-importing) to study the games standard scripts as examples.
