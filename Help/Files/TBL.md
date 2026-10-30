# TBL
`.tbl` files contain string content used for various aspects of the game. The strings can contain special characters (see [String Format](#string-format)) to control things like text color and layout.

Edited by [PyTBL](/Help/Programs/PyTBL.md)

## stat_txt.tbl
`stat_txt.tbl` contains most of the basic strings in the game.

## unitnames.tbl
`unitnames.tbl` contains the names of units when using an expanded [units.dat](/Help/Files/DAT/units.dat.md) file.

## images.tbl
`images.tbl` contains the paths to [GRP](/Help/Files/GRP.md) files in the [MPQs](/Help/Files/MPQ.md). The strings are referenced by [images.dat](/Help/Files/DAT/images.dat.md).

## sfxdata.tbl
`sfxdata.tbl` contains the paths to the [WAV](/Help/Files/WAV.md) files in the [MPQs](/Help/Files/MPQ.md). The strings are referenced by [sfxdata.dat](/Help/Files/DAT/sfxdata.dat.md).

## portdata.tbl
`portdata.tbl` contains the paths to the portrait [SMK](/Help/Files/SMK.md) files in the [MPQ's](/Help/Files/MPQ.md). The strings are referenced by [portdata.dat](/Help/Files/DAT/portdata.dat.md).

## mapdata.tbl
`mapdata.tbl` contains the paths to the single player campaign map [CHK](/Help/Files/Maps.md#scenariochk) files in the [MPQ's](/Help/Files/MPQ.md). The strings are referenced by [mapdata.dat](/Help/Files/DAT/mapdata.dat.md).

## String Format
Strings can contain special characters — control characters, plus `#`, `<`, and `>` — which the PyMS tools display as an escape code `<N>`, where `N` is the byte value of the character (so a newline is shown as `<10>`, and a literal `<` as `<60>`). The miscellaneous special characters are:

- `<0>` = End Substring. The game stops reading text at this character. Some strings pack multiple substrings into a single entry separated by `<0>`s — for example unit name strings in `stat_txt.tbl` contain the unit name, subunit name, and list heading.
- `<9>` = Tab
- `<10>` = Newline
- `<18>` = Right Align
- `<19>` = Center Align
- `<27>` = Escape Key
- `<35>` = A literal `#`
- `<60>` = A literal `<`
- `<62>` = A literal `>`

## Color Codes
A color code changes the color of all text after it, until the next color code. The same code produces different colors on the menu screens than it does in-game. The codes noted as disabling later color codes cause StarCraft to ignore every color code in the rest of the string.

Menu screen colors:

- `<1>` = Cyan
- `<2>` = Cyan
- `<3>` = Green
- `<4>` = Light Green
- `<5>` = Grey (disables later color codes)
- `<6>` = White
- `<7>` = Red
- `<8>` = Black (disables later color codes)
- `<11>` = Invisible (disables later color codes)
- `<12>` = Truncate
- `<14>` = Black
- `<15>` = Black
- `<16>` = Black
- `<17>` = Black
- `<20>` = Invisible (disables later color codes)
- `<21>` = Black
- `<22>` = Black
- `<23>` = Black
- `<24>` = Black
- `<25>` = Black
- `<26>` = Black/Cyan
- `<27>` = Black
- `<28>` = Black

In-game colors:

- `<1>` = Cyan
- `<2>` = Cyan
- `<3>` = Yellow
- `<4>` = White
- `<5>` = Grey (disables later color codes)
- `<6>` = Red
- `<7>` = Green
- `<8>` = Red (Player 1)
- `<11>` = Invisible (disables later color codes)
- `<12>` = Truncate
- `<14>` = Blue (Player 2)
- `<15>` = Teal (Player 3)
- `<16>` = Purple (Player 4)
- `<17>` = Orange (Player 5)
- `<20>` = Invisible (disables later color codes)
- `<21>` = Brown (Player 6)
- `<22>` = White (Player 7)
- `<23>` = Yellow (Player 8)
- `<24>` = Green (Player 9)
- `<25>` = Brighter Yellow (Player 10)
- `<26>` = Cyan (Player 12)
- `<27>` = Pinkish (Player 11)
- `<28>` = Dark Cyan
- `<29>` = Greygreen
- `<30>` = Bluegrey
- `<31>` = Turquoise

## Hotkey Types
Strings used for command button tooltips start with two special characters: the button's hotkey (for example the `m` in `m<1>Train <3>M<1>arine<0>`), followed by a hotkey type code that determines which requirements the game displays in the tooltip:

- `<0>` = Label only, no requirements
- `<1>` = Minerals, Gas, and Supply (Unit/Building)
- `<2>` = Upgrade Research
- `<3>` = Spell
- `<4>` = Technology Research
- `<5>` = Minerals and Gas (Guardian/Devourer Aspect)
