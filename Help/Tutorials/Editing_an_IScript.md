# Editing an IScript
This tutorial walks through editing an animation script with [PyICE](/Help/Programs/PyICE.md) — from finding the script that controls a unit, to changing it and getting it into your mod. As an example, we will change the sound the Marine plays when it fires. See the [IScript Language](/Help/Programs/PyICE/IScript_Language.md) page for the language the scripts are written in.

## Opening the Scripts
1. Open PyICE. It needs the games data files to show names and validate your code — the defaults load from the MPQs bundled with PyMS, and the settings dialog will open automatically if anything fails to load (see [Data Files](/Help/Programs/PyICE.md#data-files)).
2. Press **Open Default Scripts** (`Ctrl+D`) to open the default StarCraft `iscript.bin` (or **Open** (`Ctrl+O`) to open the `iscript.bin` from your mod).

## Finding the Script
1. You could scroll the IScript Entries list to find the entry named Marine, but you usually know the unit, not the script — so scroll the **Units** list to Terran Marine and select it instead. PyICE resolves the unit through its flingy, sprite, and image to the script that animates it, and the status bar shows the result: `IScript ID's Selected: 78`.
2. Press **Edit IScript entries** (`Ctrl+E`) to decompile the entry into the [IScript Editor](/Help/Programs/PyICE/Code_Editor.md).

## Reading the Code
At the top is the script's header, listing its [animations](/Help/Files/iscript.bin.md#animations) and the block each one starts at — the ground attack animations are `GndAttkInit` (starting at the block labelled `Marine_GndAttkInit`) and `GndAttkRpt` (the repeated attack, at `Marine_GndAttkRpt`). Find the `Marine_GndAttkRpt:` label in the code; the firing itself happens in these lines:

```
	playsnd          	69	# Bullet\TMaFir00.wav
	attackwith       	1
```

`playsnd` plays the gunfire sound, and `attackwith 1` applies the ground weapon's damage. The `playfram`/`wait` lines around them alternate between frame sets 2 and 3 (aiming and muzzle flash) to animate the burst. Hover any command to see a tooltip describing it — the full list is in the [Command Reference](/Help/Programs/PyICE/Command_Reference.md).

## Making the Change
1. Put the cursor on the `playsnd` line and press **Sound Previewer** (`Ctrl+Q`) — it opens with sound 69 selected (see [Previewers](/Help/Programs/PyICE/Previewers.md#sound-previewer)).
2. Pick a different sound from the dropdown, and press the play button to hear it.
3. Check **Overwrite**, then press **ID** — the sound ID on the `playsnd` line is replaced with your chosen sound.
4. Press **Test Code** (`Ctrl+T`) to check the code compiles, then **Save** (`Ctrl+S`) to compile it into the loaded file, and close the editor.

## Saving and Using It In the Game
1. Back in the main window, press **Save As...** (`Ctrl+Alt+A`) to save your `iscript.bin` (don't overwrite the default scripts bundled with PyMS).
2. To use the scripts in the game they need to be in the MPQ your mod loads, at the path `scripts\iscript.bin`. Use [PyMPQ](/Help/Programs/PyMPQ.md) to add the saved file to your mods MPQ.

## Going Further
- Edit the animation itself: add more `playfram`/`wait`/`attackwith` lines to lengthen the burst, or change the `wait` values to alter its timing.
- Use the [Graphics Previewer](/Help/Programs/PyICE/Previewers.md#graphics-previewer) (`Ctrl+W`) to browse the Marine's GRP frames and find frame sets to play.
- Use the [Code Generator](/Help/Programs/PyICE/Code_Generator.md) (`Ctrl+G`) to generate long `playfram` sequences instead of typing them by hand.

## See Also
- [PyICE](/Help/Programs/PyICE.md)
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [Command Reference](/Help/Programs/PyICE/Command_Reference.md)
- [iscript.bin](/Help/Files/iscript.bin.md)
- [PyMPQ](/Help/Programs/PyMPQ.md)
