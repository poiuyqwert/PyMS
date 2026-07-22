# aiscript.bin
`aiscript.bin` contains the AI Scripts used by computers players in melee and campaign maps, as well as for use in map triggers (like "Junkyard Dog"). Because the file has a limit of 65535 bytes, [bwscript.bin](#bwscriptbin) was introduce in BroodWar to allow more scripts to be included.

Edited by [PyAI](/Help/Programs/PyAI.md).

## bwscript.bin
`bwscript.bin` uses the exact same format as `aiscript.bin`, it was introduce in BroodWar to get around the 65535 byte file size limit.

Edited by [PyAI](/Help/Programs/PyAI.md).

## Format
`aiscript.bin` and `bwscript.bin` share the same overall layout, and every value is stored little-endian. A file is made up of three parts, in order:

1. A `u32` offset (from the start of the file) to the script header table.
2. The bytecode of all the scripts.
3. The script header table.

All bytecode addresses (in the script headers and in commands that jump to a block of code) are offsets from the start of the file. Standard files store block references in commands as `u16` offsets, which is what limits the file to 65535 bytes (see [Expanded files](#expanded-files) for how that limit can be raised).

### Script header table
The header table is an array of script headers, terminated by a `u32` with value 0 where the next header would begin.

Each header in `aiscript.bin` contains the following fields:

1. `id` — A 4 character ID for the script (`char[4]`).
2. `address` — A `u32` offset to the script's bytecode entry point. An address of 0 means the script's bytecode is stored in [bwscript.bin](#bwscriptbin) instead, in the entry with the same ID.
3. `string_id` — A `u32` 1-based index of the entry in [stat_txt.tbl](/Help/Files/TBL.md#stat_txttbl) used as the script's name.
4. `flags` — A `u32` bitfield: `0x1` = requires a location (the script is run on a location by a map trigger), `0x2` = hidden from StarEdit's script list, `0x4` = BroodWar only.

Each header in `bwscript.bin` contains only the first two fields (`id` and `address`), and an address of 0 is not valid.

### Expanded files
To get around the 65535 byte size limit, files can be "expanded", which requires the AISE plugin for the game to load them (see [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)). An expanded file is detected by its header table offset being `0x10000` or higher.

In an expanded file the `goto` command and the AISE commands store their block offsets as `u32` instead of `u16`, and immediately after the `u32` header table offset (at file offset 4) there is a run of consecutive long-jump `goto` commands (each a `u8` opcode 0 followed by its `u32` target offset), ending at the first byte that is not a `goto` opcode. The other standard commands still store block references as `u16` offsets, so any block they reference is given a long-jump `goto` in this run, and the command's `u16` offset points at that `goto`, which in turn jumps to the block's real offset.