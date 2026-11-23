# Sfxdata Tab
The Sfxdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md), which contains the settings for all the games sounds.

## Sound
The **Sound File** is the [WAV](/Help/Files/WAV.md) file the sound plays, referenced by its index in `sfxdata.tbl` (the dropdown shows the file paths). The play button next to the dropdown plays the sound (loaded from your MPQs, so it requires MPQ support and your [MPQ settings](/Help/Programs/PyDAT.md#data-files) to be set up).

## General Properties
- **Priority**: Which sound wins when all 8 sound channels are busy: a new sound stops the playing sound with the lowest priority that is strictly lower than its own, or is not played if there is none.
- **Portrait Length Adjust**: Milliseconds (signed) added to how long the talking portrait plays for unit speech, on top of the sound's length rounded down to whole seconds.
- **Minimum Volume**: The lowest volume the sound fades to at a distance, on the game's 0–99 volume scale (not a percentage). Sounds quieter than 11 are not played, so 10 or less has no effect.

## Flags
- **Preload**: The sound is loaded ahead of time and kept loaded.
- **Unit Speech**: The sound won't play while a sound with this flag is playing for a unit of the same unit type. Set for all unit speech; the speech settings and muting do not depend on it.
- **One at a Time**: The sound won't play if an instance of it is already playing.
- **Never Preempt**: The sound is not interrupted by new sounds when all the sound channels are in use.

Bits 0x04 and 0x08 of the flags are used by the game itself while it runs and are not shown.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the sound in their Ready, What, Yes, and Annoyed sounds.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md)
- [WAV](/Help/Files/WAV.md)
