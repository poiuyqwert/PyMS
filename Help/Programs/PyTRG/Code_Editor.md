# Code Editor
The Code Editor fills the main window of [PyTRG](/Help/Programs/PyTRG.md), and is where you write and edit trigger code (see [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)). It is enabled once a TRG is created or opened.

## Editor Features
- **Syntax highlighting**: Comments, section headers, keywords, condition names, action names, numbers, TBL formatted characters (like `<3>`), and operators each have their own style. **Color Settings** (`Ctrl+Alt+C`) customizes the styles, including the ones used for selected text and for highlighted errors and warnings.
- **Autocomplete**: Press `Tab` to complete the word being typed, and keep pressing `Tab` to cycle through the matches. Suggestions include condition and action names, unit property names, keywords, unit names from your `stat_txt.tbl`, and the IDs and names of the AI scripts in your `aiscript.bin`/`bwscript.bin` (see [Data Files](/Help/Programs/PyTRG.md#data-files)).
- **Tooltips**: Hovering over a condition or action name shows its parameters and a description of what it does — the same documentation as the [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md) and [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md).
- **Find/Replace** (`Ctrl+F`): Opens the Find/Replace dialog. `F3` repeats the last find.

## Editing Shortcuts
- `Ctrl+]` and `Ctrl+[`: Indent and dedent the current line or selection (`Shift+Tab` also dedents).
- `Ctrl+/`: Comment or uncomment the current line or selection.
- `Alt+Up` and `Alt+Down`: Jump to the previous/next trigger header.
- `Alt+Left` and `Alt+Right`: Jump to the previous/next highlighted error or warning (after using **Test Code**, or a failed save).

## See Also
- [TRG Language](/Help/Programs/PyTRG/TRG_Language.md)
- [Conditions Reference](/Help/Programs/PyTRG/Conditions_Reference.md)
- [Actions Reference](/Help/Programs/PyTRG/Actions_Reference.md)
