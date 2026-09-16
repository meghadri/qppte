from threading import Lock
from typing import override

import tree_sitter_python
from PySide6.QtGui import QPalette, QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit, QWidget
from tree_sitter import Language, Node, Parser, Point, Query, QueryCursor

from qppte.style import STYLES

PY_LANGUAGE = Language(tree_sitter_python.language())
PYTHON_PARSER = Parser(PY_LANGUAGE)
HIGHLIGHTER_QUERY = Query(
    PY_LANGUAGE,
    """
        (function_definition
          name: (identifier) @function_definition)

        (function_definition (identifier) @special_function (#eq? @special_function "__init__"))
        ("." (identifier) @special_function (#eq? @special_function "__init__"))

        (type) @type

        (class_definition
          name: (identifier) @class_definition_name)

        (call (identifier) @function_call)
        (decorator "@" (identifier)) @decorator 
        (decorator "@" (call (identifier) @decorator))  
        (decorator ("@" @decorator))

        (string_start) @string
        (string_content) @string
        (string_end) @string

        ["def" "return" "if" "else" "class" "assert" "async" "await" "break" "continue" "del" "elif" 
         "else" "except" "finally" "for" "global" "lambda" "pass" "raise" "nonlocal" "return" "try" 
         "while" "yield" "as" "with" "import" "from" "match" "case"] @keyword

        (true) @keyword
        (false) @keyword

        (integer) @number
        (float) @number

        (keyword_argument (identifier) @keyword_argument) 

        ((identifier) @self (#eq? @self "self"))

        (comment) @line_comment
    """,
)


class QPythonPlainTextEdit(QPlainTextEdit):
    def __init__(
        self, parent: QWidget | None = None, highlightStyle: str = "default", enableSyntaxHighlighting: bool = True
    ):
        super().__init__(parent)
        self.__syntax_highlighting_enabled = enableSyntaxHighlighting
        self.__working = False

        self.setAutoFillBackground(True)
        self.__highlightStyle = highlightStyle
        self.__setBackground()

        self.__lock = Lock()
        self.__highlight_done_once = False
        self.__signal_connected = False

    def __setBackground(self):
        palette = QPalette()
        palette.setColor(QPalette.ColorRole.Base, STYLES[self.__highlightStyle]["QPlainTextEdit_background_color"])
        self.setPalette(palette)

    def __highlight(self) -> None:
        if not self.__syntax_highlighting_enabled:
            return

        cursor: QTextCursor = self.textCursor()

        text = self.toPlainText()
        lines = text.splitlines()

        def get_offset(p: Point) -> int:
            return sum([len(line) for line in lines[0 : p.row]]) + p.column + p.row

        input_text = text.encode()
        tree = PYTHON_PARSER.parse(input_text)
        query_cursor = QueryCursor(HIGHLIGHTER_QUERY)

        matches: list[tuple[int, dict[str, list[Node]]]] = query_cursor.matches(tree.root_node)
        matches.sort(key=lambda m: m[0])
        for _, m in matches:
            for capture_name, nodes in m.items():
                for node in nodes:
                    cursor.setPosition(get_offset(node.start_point))
                    cursor.setPosition(get_offset(node.end_point), QTextCursor.MoveMode.KeepAnchor)
                    cursor.setCharFormat(STYLES[self.__highlightStyle][capture_name])

        self.__highlight_done_once = True

    def __rehighlight(self):
        with self.__lock:
            if self.__working:
                return
            else:
                self.__working = True

        try:
            if self.isReadOnly() and self.__highlight_done_once:
                return

            # clear all formatting first
            cursor: QTextCursor = self.textCursor()
            cursor.setPosition(0)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(QTextCharFormat())

            self.__highlight()
            self.__highlight_done_once = True
        finally:
            self.__working = False

    @override
    def setPlainText(self, text: str, /) -> None:
        self.__highlight_done_once = False
        super().setPlainText(text)
        self.__rehighlight()
        if not self.__signal_connected:
            self.textChanged.connect(self.__rehighlight)
            self.__signal_connected = True

    def setHighlightStyle(self, highlightStyle: str) -> None:
        """
        Sets new highlight style. This will trigger re-rendering of text.
        Note that this is a NO-OP if syntax highlighting is disabled
        """
        if self.__highlightStyle != highlightStyle:
            self.__highlightStyle = highlightStyle
            self.__setBackground()
            self.setPlainText(self.toPlainText())

    def getHighlightStyle(self) -> str:
        """Returns highlight style currently in use"""
        return self.__highlightStyle

    def setEnableSyntaxHighlighting(self, enableSyntaxHighlighting: bool) -> None:
        """
        Following will trigger clearing of existing highlighting style and application of new style if any.
        Note that if you are disabling syntax highlighting and previous style affected background color,
        then this operation will not affect background color.
        """
        if self.__syntax_highlighting_enabled != enableSyntaxHighlighting:
            self.__syntax_highlighting_enabled = enableSyntaxHighlighting
            self.setPlainText(self.toPlainText())

    @staticmethod
    def listHighlightStyles() -> list[str]:
        """Returns list of available highlight styles that can be used with QPythonPlainTextEdit class"""
        return STYLES.keys()
