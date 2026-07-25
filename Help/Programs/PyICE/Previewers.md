# Previewers
The [IScript Editor](/Help/Programs/PyICE/Code_Editor.md) has two previewer dialogs for browsing the games graphics and sounds, and inserting their IDs (or whole commands) into your code. Both previewers need the games files to work: graphics and sounds are loaded from your [MPQs](/Help/Files/MPQ.md), and the graphics previewer draws with the [palettes](/Help/Files/Palettes.md) chosen in the settings (see [Data Files](/Help/Programs/PyICE.md#data-files)).

## Graphics Previewer
The **Insert/Preview Window** (`Ctrl+W`) previews [GRP](/Help/Files/GRP.md) frames, and inserts frames or image/sprite/flingy IDs. If the cursor is on a command that takes a frame, image, sprite, or flingy parameter when it is opened, the previewer opens with that command and entry selected.

### Choosing What to Preview
The radio buttons on the left choose the entry to preview, and the command to insert for it:

- **Current IScript's images**: The [images.dat](/Help/Files/DAT/images.dat.md) entries that use the script the cursor is inside (only available when the cursor is in a script with a valid `IsId`). The command dropdown holds the commands that take a Frame parameter, and inserting inserts the previewed frame.
- **Images.dat entries**: Any `images.dat` entry, with the commands that take an ImageID parameter.
- **Sprites.dat entries**: Any [sprites.dat](/Help/Files/DAT/sprites.dat.md) entry (previewing its image), with the commands that take a SpriteID parameter.
- **Flingy.dat entries**: Any [flingy.dat](/Help/Files/DAT/flingy.dat.md) entry (previewing its sprite's image), with the commands that take a FlingyID parameter.

The preview draws the entry's GRP using the palette the game would use (based on the images.dat draw settings — for example the fire remapping palettes, or the terrain palette for tileset doodad graphics).

### Browsing Frames
The frame counter shows the current frame and the total frame count of the GRP. The toolbar buttons jump to the first/last frame, jump 1 or 17 frames (one [frameset](/Help/Programs/PyICE/IScript_Language.md#frames-and-framesets)) in either direction, and play/stop playback of every frame or every 17th frame in either direction. Below the preview are playback options: the speed (in milliseconds per frame), whether to loop, and the range of frames to play between.

### Inserting
- **ID**: Inserts just the value — the previewed frame number (for **Current IScript's images**), or the previewed entry's ID (for the other modes) — at the cursor.
- **Command**: Inserts the command selected in the dropdown, with the previewed frame/ID as its parameter (any other parameters are inserted as 0 for you to fill in).
- **Overwrite**: Instead of inserting at the cursor, replaces the value (or whole command) on the current line — only if the line already holds one of the commands from the dropdown.
- **Close after**: Closes the previewer after inserting.

## Sound Previewer
The **Sound Previewer** (`Ctrl+Q`) previews the sounds in [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md), and inserts sound IDs or `playsnd` commands. If the cursor is on a `playsnd` command when it is opened, the previewer opens with that sound selected.
Choose a sound in the dropdown and press the play button to hear it. **ID** inserts the sound's ID at the cursor, and **Command** inserts a full `playsnd` command. The **Overwrite** and **Close after** options work like in the [Graphics Previewer](#inserting) (Overwrite replaces the sound ID on a `playsnd` line).

## See Also
- [IScript Editor](/Help/Programs/PyICE/Code_Editor.md)
- [Command Reference](/Help/Programs/PyICE/Command_Reference.md)
- [GRP](/Help/Files/GRP.md)
- [Palettes](/Help/Files/Palettes.md)
