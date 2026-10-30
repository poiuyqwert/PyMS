# PCX
Picture Exchange `.pcx` is a general image format, used by StarCraft for UI elements, like the backgrounds of the menus used by [UI .bin](/Help/Files/UI_BIN.md) files.
The games PCX files are 256 color (8 bit indexed) images, with their [palette](/Help/Files/Palettes.md) stored at the end of the file.
The game also uses small PCX images as special palettes — for example `tfontgam.pcx`, which holds the text colors used to draw [fonts](/Help/Files/FNT.md).

Edited by [PyPCX](/Help/Programs/PyPCX.md)

Since a PCX carries its own palette, the palette can also be extracted from it — [PyPCX](/Help/Programs/PyPCX.md) can save it out to the [palette formats](/Help/Files/Palettes.md), and [PyPAL](/Help/Programs/PyPAL.md) can open a PCX directly.
