# Sprites Tab
The Sprites tab of [PyDAT](/Help/Programs/PyDAT.md) edits [sprites.dat](/Help/Files/DAT/sprites.dat.md), which defines the games sprites — the visual objects displayed by each [Flingy](/Help/Programs/PyDAT/Flingy.md), each built from one or more [Images](/Help/Programs/PyDAT/Images.md).

## Sprite Properties
- **Image**: The primary [Image](/Help/Programs/PyDAT/Images.md) the sprite displays.
- **Is Visible** and **Unused**: Whether the sprite is visible, and an unused flag.
- **Sel. Circle**: The size of the selection circle drawn under the sprite. The size maps to one of the selection circle images, and the **Jump ->** button goes to that image entry.
- **Health Bar**: The width of the health bar, shown both as the raw value and as the resulting number of boxes.
- **Vert. Position**: The vertical offset of the selection circle and health bar below the sprite.

The selection circle and health bar settings are only stored for sprite IDs 130 and up (the sprites used by selectable units) — for other sprites those fields are disabled.

## Preview
The Preview shows the sprites image, and when the selection circle fields are enabled it also draws the selection circle and health bar so you can line them up with the Vert. Position field. Previews are rendered using the palettes and MPQs from your [settings](/Help/Programs/PyDAT.md#data-files).

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the flingies using the sprite.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [sprites.dat](/Help/Files/DAT/sprites.dat.md)
