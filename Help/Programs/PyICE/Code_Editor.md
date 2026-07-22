# IScript Editor
The IScript Editor is where you write and edit IScript code (see [IScript Language](/Help/Programs/PyICE/IScript_Language.md)). It is opened with **Edit IScript entries** (`Ctrl+E`) in the [main window](/Help/Programs/PyICE.md#main-window) — the selected entries are decompiled into the editor. Opening it with no entries selected gives you an empty editor to write new entries in.

## Toolbar
- **Save** (`Ctrl+S`): Compiles the code and applies it to the loaded file. Compile errors are shown (and highlighted in the code), and nothing is applied until the code compiles. Compiled entries with the same ID as an existing entry replace the existing entry.
- **Test Code** (`Ctrl+T`): Compiles the code without applying it. Errors and warnings are highlighted in the code, or you are told the code compiles cleanly.
- **Export Code** (`Ctrl+E`) and **Export As...** (`Ctrl+Alt+A`): Saves the code in the editor to a text file.
- **Import Code** (`Ctrl+I`): Replaces the code in the editor with the contents of a text file.
- **Find/Replace** (`Ctrl+F`): Opens the Find/Replace dialog. `F3` repeats the last find.
- **Color Settings** (`Ctrl+Alt+C`): Customizes the syntax highlighting styles.
- **Generate Code** (`Ctrl+G`): Opens the [Code Generator](/Help/Programs/PyICE/Code_Generator.md), for generating repetitive code from a template.
- **Insert/Preview Window** (`Ctrl+W`): Opens the [Graphics Previewer](/Help/Programs/PyICE/Previewers.md#graphics-previewer), for previewing GRP frames and images/sprites/flingys and inserting their IDs or commands. If the cursor is on a command that takes a frame, image, sprite, or flingy parameter, the previewer opens with that entry selected.
- **Sound Previewer** (`Ctrl+Q`): Opens the [Sound Previewer](/Help/Programs/PyICE/Previewers.md#sound-previewer), for listening to sounds and inserting their IDs or `playsnd` commands. If the cursor is on a `playsnd` command, the previewer opens with that sound selected.

## Editor Features
- **Syntax highlighting**: Comments, `.headerstart`/`.headerend` headers, header commands, blocks, commands, numbers, operators, and keywords each have their own configurable style.
- **Autocomplete**: Press `Tab` to complete the word being typed, and keep pressing `Tab` to cycle through the matches. Suggestions include commands, header commands, and the block names already in your code.
- **Tooltips**: Hovering over a command or header command shows its parameters and a description of what it does — a built in [Command Reference](/Help/Programs/PyICE/Command_Reference.md).
- **Status bar**: Shows the IDs of the entries being edited, an indicator for unsaved changes, and the current line, column, and selection size.

Closing the editor with unsaved changes will ask if you want to save (compile) them first.

## See Also
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
- [Command Reference](/Help/Programs/PyICE/Command_Reference.md)
- [Code Generator](/Help/Programs/PyICE/Code_Generator.md)
- [Previewers](/Help/Programs/PyICE/Previewers.md)
