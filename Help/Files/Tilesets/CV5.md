# CV5
`.cv5` files are the "main" file of a [Tileset](/Help/Files/Tilesets/Tilesets.md), containing the MegaTile Groups. Each group references 16 MegaTiles (defined in the [.vx4](/Help/Files/Tilesets/VX4.md) file) along with the settings for how its tiles behave in the game — flags like walkability, buildability, creep, and height, plus edge/piece values used to match neighboring tile types.

Edited by [PyTILE](/Help/Programs/PyTILE.md) (see [Tile Groups](/Help/Programs/PyTILE/Tile_Groups.md))

## Doodads
Groups with type 1 are doodad groups: instead of edge/piece values they hold doodad settings — the Doodad ID (which links the groups making up one doodad, and indexes its placement data in [dddata.bin](/Help/Files/Tilesets/dddata.bin.md)), the doodads size in MegaTiles, an optional sprite/unit overlay, and a name string. See [Doodad Groups](/Help/Programs/PyTILE/Doodad_Groups.md) for editing them.
