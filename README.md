QPPTE - QPythonPlainTextEdit
============================

A poor-main text editor for editing and viewing Python code to be used with [PySide6](https://pypi.org/project/PySide6/)
library. It supports basic syntax highlighting using [tree-sitter](https://github.com/tree-sitter/py-tree-sitter) and
keystrokes common to code editors. Highlighting styles can be customized and expanded. Likewise, keystrokes can be
customized by the user.

When syntax highlighting is enabled we synchronously reparse the whole source code tree and re-highlight entire text.
This is suboptimal and could result in slowing down of the text update but is adequate for relatively small files.

## Adding qptte to your code

```shell
uv add git+https://github.com/priimak/qppte.git@v0.4.0
```

## Running demo GUI

```shell
uv tool run --from git+https://github.com/priimak/qppte.git@v0.4.0 qppte_demo
```

## Supported additional editor operations

* Line or block indent
    * Press `Tab` to indent a line or a selected block by a Tab width number of spaces. Tab is always converted into
      space (default 4).
* Undo and Redo
    * `Ctrl-Z` and `Ctrl-R`
* Unindent line or block
    * Press `Shift-Tab` to unindent a line or a selected block by a Tab width number of spaces.
* Delete line or block.
    * `Ctrl-Y` will delete a line or all lines in a selected block.
* Duplicate line
    * `Ctrl-D` will duplicate current line and move cursor down.
* Move line up and down
    * `Ctrl-Shift-ArrowUp` and `Ctrl-Shift-ArrowDown` will move current line up and down respectively.
* Toggle commenting line or block.
    * `Ctrl-/` will toggle commenting out a line or all lines included in the selected block.