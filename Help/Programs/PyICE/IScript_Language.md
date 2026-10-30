# IScript Language
StarCraft's IScript language is a procedural scripting language, similar in structure to assembly: code is organized into labelled blocks, executes top-down, and jumps/calls between blocks. PyICE decompiles the binary scripts in [iscript.bin](/Help/Files/iscript.bin.md) into this text language, and compiles it back.
An IScript entry has two parts: a [header](#script-headers), which gives the entry its ID and lists the entry points for its [animations](/Help/Files/iscript.bin.md#animations), and the [blocks](#blocks) of code those entry points refer to. A decompiled entry looks like this:

```
# This header is used by images.dat entries:
#   4 Scourge Explosion (zerg\zavExplo.grp)
.headerstart
IsId             	3	# Scourge Explosion
Type             	1
Init             	Scourge_Explosion_Init
Death            	Scourge_Explosion_Death
.headerend

Scourge_Explosion_Init:
	playfram         	0x00	# Frame set 0
	wait             	1
	playfram         	1
	wait             	1
	end

Scourge_Explosion_Death:
	wait             	1
	end
```

## Script Headers
A header starts with `.headerstart` and ends with `.headerend`. Inside it are header commands, one per line:

- `IsId` sets the ID of the entry. This is the ID that [images.dat](/Help/Files/DAT/images.dat.md) entries reference to use the script.
- `Type` sets the type of the entry, which determines exactly which [animations](/Help/Files/iscript.bin.md#animations) the header contains.
- The remaining commands are the animation entry points (`Init`, `Death`, `GndAttkInit`, etc.), each naming the block where that animation starts, or `[NONE]` if the animation has no code (`Init` must always name a block).

The valid types, and the animations a header of that type must contain, are:

- Type 0 or 1: The first 2 animations (`Init` and `Death`)
- Type 2: The first 4 animations
- Type 12 or 13: The first 14 animations
- Type 14 or 15: The first 16 animations
- Type 20 or 21: The first 22 animations
- Type 23: The first 24 animations
- Type 24: The first 26 animations
- Type 26, 27, 28, or 29: All 28 animations

Every animation for the entry's type must be present in the header (using `[NONE]` for unused animations), no others can be present, and no command can be repeated. When decompiling, PyICE adds a comment above each header listing the `images.dat` entries that use it, and a name comment next to the `IsId`.

## Blocks
A block is a label name followed by a colon, on its own line. The commands after a label belong to that block, and execution simply flows from one command to the next — including through the next label — until it reaches a command that ends the flow (like `goto`, `end`, or `return`). Animation entry points in headers, and commands like `goto`, `call`, and the conditional jumps, refer to blocks by their label name. Multiple headers can reference the same blocks, which is how the default `iscript.bin` shares code between similar entries.

## Commands
Each command is on its own line: the command name followed by its parameters, separated by whitespace. Parameters can also be wrapped in parenthesis and separated by commas (`playfram(0x00)`) — both styles compile the same. Numbers can be given in decimal or hexadecimal (`17` or `0x11`). Comments start with `#` and run to the end of the line; the decompiler adds comments giving the names of images, sprites, sounds, weapons, and frame sets used in commands.
Every command, and each one's parameters, are documented in the [Command Reference](/Help/Programs/PyICE/Command_Reference.md). The same documentation is shown as tooltips when hovering a command in the [IScript Editor](/Help/Programs/PyICE/Code_Editor.md).

## Frames and Framesets
Commands like `playfram` display a frame of the image's [GRP](/Help/Files/GRP.md) by its index. The frames of GRPs for things that can face different directions are organized into **framesets** of 17 frames each: frame set N covers frames `N*17` to `N*17+16`, with one frame for each of the 17 facing directions from up (0) clockwise to down (16) — the game mirrors these frames for the 15 directions facing left.
Giving `playfram` the first frame of a frameset (a multiple of 17) displays the frame within that frameset matching the sprite's current direction. The decompiler writes those values in hexadecimal with a `Frame set N` comment (`0x00` is frame set 0, `0x11` is frame set 1, `0x22` is frame set 2, etc.), and the [Graphics Previewer](/Help/Programs/PyICE/Previewers.md#graphics-previewer) has buttons to step through frames 17 at a time to preview framesets. GRPs for things that don't turn (like explosions) don't use framesets, and their frames are just played by plain index.

## See Also
- [Command Reference](/Help/Programs/PyICE/Command_Reference.md)
- [IScript Editor](/Help/Programs/PyICE/Code_Editor.md)
- [iscript.bin](/Help/Files/iscript.bin.md)
- [Editing an IScript](/Help/Tutorials/Editing_an_IScript.md)
