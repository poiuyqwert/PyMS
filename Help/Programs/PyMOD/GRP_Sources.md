# GRP Sources
A folder whose name ends with `.grp` is compiled by [PyMOD](/Help/Programs/PyMOD.md) into a [.grp](/Help/Files/GRP.md) graphic of the same name, from the `.bmp` files inside it. The BMPs must be 8-bit paletted images, the same thing [PyGRP](/Help/Programs/PyGRP.md) exports.
Frames have a maximum size of 256x256, and every frame in a GRP is the same size.

## Frame Modes
How the BMPs in the folder become frames is set with a `config.json`:

- `frames_mode` (default `separate_bmps`): Either `separate_bmps`, `single_vertical`, or `single_framesets`. See below.
- `frame_count`: How many frames the image holds. Required by the two single-image modes, and ignored by `separate_bmps`.
- `uncompressed` (default `false`): Saves the GRP uncompressed. Larger, but the game loads it slightly faster.

`separate_bmps` is one BMP per frame. The frames are ordered by filename, so name them so they sort correctly — `frame 000.bmp`, `frame 001.bmp`, and so on, which is exactly what PyGRP's export produces. Every BMP has to be the same size as the first one, and the build fails naming the first file that isn't.
`single_vertical` is one BMP holding every frame stacked in a single column, the layout the SFGrpConv tool uses. The frame height is the image height divided by `frame_count`.
`single_framesets` is one BMP holding every frame laid out in rows of 17, matching the [framesets](/Help/Files/GRP.md#framesets) a rotating graphic is made of. The frame width is the image width divided by 17, and the frame height is the image height divided by the number of rows.
Both single-image modes need exactly one `.bmp` in the folder; more than one fails the build. A folder with no `.bmp` files at all fails the build too, in every mode.

```
{
	"frames_mode": "single_framesets",
	"frame_count": 229
}
```

## Palette
A GRP stores palette indexes rather than colors, so the palette of your BMPs is what decides how the frames are interpreted. Index 0 is the transparent color. The game colors the GRP with whichever [palette](/Help/Files/Palettes.md) it draws that graphic with, so your BMPs need to use the palette the game will use — for a unit that is `Units.pal`, and PyGRP and [PyPAL](/Help/Programs/PyPAL.md) can help you get an image into it.

## See Also
- [PyMOD](/Help/Programs/PyMOD.md)
- [MPQ Packages](/Help/Programs/PyMOD/MPQ_Packages.md)
- [Building](/Help/Programs/PyMOD/Building.md)
- [PyGRP](/Help/Programs/PyGRP.md)
- [GRP](/Help/Files/GRP.md)
- [Editing a GRP](/Help/Tutorials/Editing_a_GRP.md)
