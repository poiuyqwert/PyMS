# Code Editor
The Code Editor is where you write and edit AI script code (see [AI Language](/Help/Programs/PyAI/AI_Language.md)). It is opened with **Edit AI Script** (`Ctrl+E`) or by double clicking a script in the main window — the selected scripts are decompiled into the editor. Opening it with no scripts selected gives you an empty editor to write new scripts in.

## Toolbar
- **Save** (`Ctrl+S`): Compiles the code and applies it to the loaded files. Compile errors are shown (and highlighted in the code), and nothing is applied until the code compiles.
- **Test Code** (`Ctrl+T`): Compiles the code without applying it. Errors and warnings are highlighted in the code, or you are told the code compiles cleanly.
- **Export Code** (`Ctrl+E`) and **Export As...** (`Ctrl+Alt+A`): Saves the code in the editor to a text file.
- **Import Code** (`Ctrl+I`): Replaces the code in the editor with the contents of a text file.
- **Find/Replace** (`Ctrl+F`): Opens the Find/Replace dialog. `F3` repeats the last find.
- **Color Settings** (`Ctrl+Alt+C`): Customizes the syntax highlighting styles.
- **Insert String ID** (`Ctrl+Alt+I`): Chooses a string from `stat_txt.tbl` and inserts its index at the cursor, with the string text as a trailing comment. Used on a `name_string` line it replaces the existing index. Only available when a `stat_txt.tbl` is loaded (see [Data Files](/Help/Programs/PyAI.md#data-files)).
- **Transpile to PyAI code** (`Ctrl+Alt+P`): Converts code written for old versions of PyAI, or for ASC3 (`script_name`/`script_id` headers), into the current `script` header syntax. The old formats don't contain all of the header information, so check the generated headers afterwards (the transpiler inserts a note where it had to guess).
- **Debuggerize your code** (`Ctrl+D`): Automatically inserts `debug` commands around flow commands (`goto`, `call`, `multirun`, `stop`, and the various jumps) so that when the script runs in the game, it reports each jump it takes and what triggered it.

## Editor Features
- **Syntax highlighting**: Comments, `script` headers, AI IDs, blocks, commands, AISE commands, types, `@directives`, numbers, TBL formatted characters (like `<44>`), operators, and keywords each have their own configurable style.
- **Autocomplete**: Press `Tab` to complete the word being typed, and keep pressing `Tab` to cycle through the matches. Suggestions include commands, `@directives`, type names and keywords, unit/upgrade/technology names from your [Data Files](/Help/Programs/PyAI.md#data-files), and the block names already in your code.
- **Tooltips**: Hovering over a command, type, or `@directive` shows its parameters and a description of what it does — a built in [Command Reference](/Help/Programs/PyAI/Command_Reference.md).
- **Status bar**: Shows the IDs of the scripts being edited, an indicator for unsaved changes, and the current line, column, and selection size.

Closing the editor with unsaved changes will ask if you want to save (compile) them first.

## See Also
- [AI Language](/Help/Programs/PyAI/AI_Language.md)
- [Command Reference](/Help/Programs/PyAI/Command_Reference.md)
- [AISE Commands](/Help/Programs/PyAI/AISE_Commands.md)
