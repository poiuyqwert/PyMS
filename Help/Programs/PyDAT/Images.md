# Images Tab
The Images tab of [PyDAT](/Help/Programs/PyDAT.md) edits [images.dat](/Help/Files/DAT/images.dat.md), which defines the games images — each pairs a [GRP](/Help/Files/GRP.md) graphic with an [IScript](/Help/Files/iscript.bin.md) animation and drawing settings. Images are displayed by [Sprites](/Help/Programs/PyDAT/Sprites.md).

## Image
The **GRP** field is the graphics file, referenced by its index in `images.tbl` (the dropdown shows the file paths). The **Iscript ID** is the [IScript](/Help/Files/iscript.bin.md) entry that animates the image — unused IScript IDs are marked in the dropdown.
Each field has a **Check** button, which fills the [Used By](/Help/Programs/PyDAT.md#used-by) panel with every image sharing that GRP or IScript ID — useful for checking what else you would affect by editing them.

## General Properties
- **Graphics Turns**: The game picks (and mirrors) animation frames based on the direction the sprite faces.
- **Draw If Cloaked**: The image is still drawn while the unit is cloaked.
- **Clickable**: The image can be clicked with the mouse cursor to select its unit.
- **Use Full Iscript**: Allows the image to run IScript animations other than its initial and death animations — needed for units to move, attack, and cast spells with animations.

## Drawing Properties
The **Function** chooses how the image is drawn — normal, shadow, cloaking effects, selection circle, remapped colors, and so on. When the function is remapping, **Remapping** chooses the color remap (ofire, gfire, bfire).

## Extra Overlay Placements
The Attack, Damage, Special, Landing Dust, and Lift-Off Dust overlays are `images.tbl` references to the [LO files](/Help/Files/LO.md) that position extra overlay images (like where a Wraiths attack flashes appear). The Shield overlay is the same for the shield hit effect, with a dropdown to pick the standard None/Small/Medium/Large shield overlays.

## Preview
The Preview renders the images GRP with its drawing function applied, using the palettes and MPQs from your [settings](/Help/Programs/PyDAT.md#data-files).

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the image as their construction animation, and the sprites using it as their image.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [images.dat](/Help/Files/DAT/images.dat.md)
