# Portdata Tab
The Portdata tab of [PyDAT](/Help/Programs/PyDAT.md) edits [portdata.dat](/Help/Files/DAT/portdata.dat.md), which contains the settings for the unit portraits shown in the bottom center of the game screen.
Each portrait entry has two sets of [SMK](/Help/Files/SMK.md) videos — the **Idle Portrait** (fidget videos 0–3) played normally, and the **Talking Portrait** (talking videos 0–2) played when the unit speaks.

- **SMK Prefix**: The folder and start of the file name of the videos, referenced by its index in `portdata.tbl` (the dropdown shows the strings). The game adds the video number and `.smk`: `tmarine\TMaFid0` gives `portrait\tmarine\TMaFid00.smk` to `TMaFid03.smk`. If a video is missing, the next lower number is played. Talking videos are picked at random, never the same one twice in a row.
- **Fidget 0–3 Chance**: How likely each fidget video is to be picked, out of 101. The file stores four fidget chances and none for talking; PyDAT shows fidget 0 and 2 in the Idle Portrait box and fidget 1 and 3 in the Talking Portrait box. The game rolls 0–100 and adds the chances up in order 0, 1, 2, 3 until the total reaches the roll, so the four should add up to at least 100 (a roll above the total most likely crashes the game). The shipped portraits use 85/5/5/5, or 100/0/0/0 for fidget 0 only.

With the portrait setting below full animation, only video 0 is played.

## Used By
The [Used By](/Help/Programs/PyDAT.md#used-by) panel lists the units using the portrait.

## See Also
- [PyDAT](/Help/Programs/PyDAT.md)
- [portdata.dat](/Help/Files/DAT/portdata.dat.md)
- [SMK](/Help/Files/SMK.md)
