# Palettes
Palettes contain the colors used by StarCraft. A palette always holds exactly 256 colors, matching the games 8-bit indexed color graphics, with each color made up of red, green, and blue components (0 to 255 each).

Edited by [PyPAL](/Help/Programs/PyPAL.md)

Besides the palette file formats below, palettes are also embedded in indexed color images — PyPAL can extract the palette from [.pcx](/Help/Files/PCX.md) and 8-bit [.bmp](/Help/Files/BMP.md) files.

## RIFF .pal
A palette stored in Microsoft's RIFF container format, used by Windows programs. The file has a header identifying it as palette data, followed by the colors stored as 4 bytes each (red, green, and blue plus an unused byte).

## JASC .pal
A plain text palette format from Paint Shop Pro. The file starts with a `JASC-PAL` header, followed by one line per color listing its red, green, and blue values separated by spaces.

## StarCraft .pal
A raw palette with no header: the colors are stored as 3 bytes each (red, green, and blue), for a total of 768 bytes. Since there is no header, the format is recognized purely by its file size. The palettes bundled with PyMS in its `Palettes` folder (like `Units.pal` and `Icons.pal`) are in this format.

## Terrain .wpe
A raw palette with no header, used by the [tilesets](/Help/Files/Tilesets/Tilesets.md) to color the terrain: the colors are stored as 4 bytes each (red, green, and blue plus an unused byte), for a total of 1024 bytes.

## Adobe Color Table .act
Adobe's palette format, used by programs like Photoshop. Its contents are identical to a [StarCraft .pal](#starcraft-pal) — a raw palette at 3 bytes per color — only the file extension differs.
