# Sfxdata Tab
The Sfxdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md), which contains the settings for all the games sounds.

## Sound
The **Sound File** is the [WAV](/Help/Files/WAV.md) file the sound plays, referenced by its index in `sfxdata.tbl` (the dropdown shows the file paths). The play button next to the dropdown plays the sound (loaded from your MPQs, so it requires MPQ support and your [MPQ settings](/Help/Programs/PyDAT.md#data-files) to be set up).

## General Properties
- **Priority**: Which sound wins when too many sounds play at once.
- **Portrait Length Adjust**: Adjusts how long the talking portrait plays for unit speech.
- **Minimum Volume %**: The lowest volume the sound fades to at a distance.

## Flags
- **Preload**: The sound is loaded ahead of time.
- **Unit Speech**: The sound respects the games unit speech settings (it won't play when unit speech is muted).
- **One at a Time**: The sound won't play if an instance of it is already playing.
- **Never Preempt**: The sound is not interrupted by new sounds when all the sound channels are in use.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the sound in their Ready, What, Yes, and Annoyed sounds.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md)
- [WAV](/Help/Files/WAV.md)
