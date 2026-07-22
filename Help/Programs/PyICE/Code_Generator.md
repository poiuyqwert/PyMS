# Code Generator
The Code Generator generates repetitive code (like long `playfram`/`wait` sequences) from a code template and a set of variables. It is opened with **Generate Code** (`Ctrl+G`) in the [IScript Editor](/Help/Programs/PyICE/Code_Editor.md).
The dialog has three areas: the list of variables on the left, the code template in the top right, and a preview of the generated code in the bottom right.

## Code Template
The template is repeated once per generation step, with variables substituted into it each time. Variables are referenced in the template as `$name` (substituted in decimal) or `%name` (substituted in hexadecimal, like `0x11`). The variable `n` is built in, and is the current step number, starting at 0.
The number of steps is determined by the largest count among the variables with a finite count (a [Range](#range), or a [List](#list) that doesn't repeat forever). At least one finite variable is required to generate.

## Variables
Variables are added with the add button (choosing the variable type), edited by double clicking them (or with the edit button), and removed with the remove button. Each variable has a name (letters, numbers, and underscores only — the name `n` is reserved) and a value that can change with each generation step. A variable's value can reference other variables with `$name`; referencing in a cycle (two variables referencing each other) is an error.

### Range
Counts from a starting number to an ending number (inclusive), increasing by a step amount — for example from 0 to 51, by adding 17. Its count is the amount of numbers it produces; past that it produces nothing.

### Math
A math expression, like `$frameset * 17`. After substituting variables, the expression can only contain numbers, `+`, `-`, `*`, `/`, parenthesis, and whitespace. It has no count of its own, so it is usually combined with a Range or List.

### List
A list of values, one per line, producing the value matching the current step. Values can reference variables with `$name`. The **Repeat** setting controls what happens after the list runs out:

- **Don't Repeat**: The count is the size of the list.
- **Once**: Plays the list twice.
- **Forever**: Repeats the list forever (no count).
- **Last Forever**: Repeats the last value forever (no count).
- **Inverted Once**: Plays the list forward then backward (like `0 1 2 1`), once.
- **Inverted Forever**: Plays the list forward then backward, forever (no count).
- **Inverted Once (Repeat End)**: Plays the list forward then backward, repeating the last value at the turn (like `0 1 2 2 1 0`), once.
- **Inverted Forever (Repeat Ends)**: Plays the list forward then backward, repeating the value at each end, forever (no count).

## Generating
**Preview** fills the bottom box with the generated code so you can check it. **Insert** generates the code, inserts it at the cursor in the editor, and closes the dialog.

## Presets
A template and its variables can be saved as a preset to reuse later. **Save Preset** saves the current template and variables under a name, and **Load Preset** loads one (the menu lists the most recent presets, with **More...**/**Manage Presets** opening the full list). The Manage Presets dialog can use, rename, reorder, remove, and import/export presets (as JSON text files, for sharing).
PyICE comes with example presets: **Play Frames** (a `playfram`/`wait` sequence over a range of frames), **Play Framesets** (the same stepping by 17 per frameset), **Play Framesets (Advanced)** (the same, using a Math variable to compute the frame from the frameset number), and **Hover Bobbing** (a `setvertpos` sequence using an inverted List to bob up and down).

## Example
The **Play Framesets** preset has a variable named `frameset`, a Range from 0 to 51 by adding 17, and this template:

```
	playfram            %frameset
	wait                2
```

Generating produces the template 4 times, with `%frameset` substituted with the hexadecimal frameset values:

```
	playfram            0x00
	wait                2
	playfram            0x11
	wait                2
	playfram            0x22
	wait                2
	playfram            0x33
	wait                2
```

## See Also
- [IScript Editor](/Help/Programs/PyICE/Code_Editor.md)
- [IScript Language](/Help/Programs/PyICE/IScript_Language.md)
