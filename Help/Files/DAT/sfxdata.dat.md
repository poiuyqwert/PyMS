# sfxdata.dat
`sfxdata.dat` contains the settings for all the sounds in the game, and a reference to a string in [sfxdata.tbl](/Help/Files/TBL.md#sfxdatatbl) which contains the path to the [WAV](/Help/Files/WAV.md) file in the [MPQ's](/Help/Files/MPQ.md).

Edited by [PyDAT](/Help/Programs/PyDAT.md) on the [Sfxdata Tab](/Help/Programs/PyDAT/Sfxdata.md)

## Format
The file has 1144 entries, one per sound ID. Each entry holds the sound file reference, priority, flags (preload, unit speech, one at a time, never preempt), portrait length adjust, and minimum volume — see the [Sfxdata Tab](/Help/Programs/PyDAT/Sfxdata.md) for the full breakdown.

## References
- A reference to a string in [sfxdata.tbl](/Help/Files/TBL.md#sfxdatatbl), which contains the path in the [MPQ's](/Help/Files/MPQ.md) for the [WAV](/Help/Files/WAV.md) file played by the sound

## Names
Sounds have no name setting — PyDAT names them after their [WAV](/Help/Files/WAV.md) file path.

## Expanded
An expanded `sfxdata.dat` (see [Expanded DAT Files](/Help/Programs/PyDAT.md#expanded-dat-files)) can have at most 65536 entries.
