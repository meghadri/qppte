from threading import Lock

import tree_sitter_python
from PySide6.QtGui import QTextCharFormat, QTextCursor
from PySide6.QtWidgets import QPlainTextEdit
from tree_sitter import Language, Parser, Point, Query, QueryCursor

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

        (decorator "@" @decorator)  
        (decorator "@" (identifier)) @decorator 

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

        (call (identifier) @function_call)

        (keyword_argument (identifier) @keyword_argument) 

        ((identifier) @self (#eq? @self "self"))

        (comment) @line_comment
    """,
)


class QPythonPlainTextEdit(QPlainTextEdit):
    def __init__(self, style: str = "default"):
        super().__init__()
        self.working = False
        self.style = style
        self.lock = Lock()
        self.highlight_done_once = False
        self.signal_connected = False

    def highlight(self) -> None:
        cursor: QTextCursor = self.textCursor()

        text = self.toPlainText()
        lines = text.splitlines()

        def get_offset(p: Point) -> int:
            return sum([len(line) for line in lines[0 : p.row]]) + p.column + p.row

        input_text = text.encode()
        tree = PYTHON_PARSER.parse(input_text)
        query_cursor = QueryCursor(HIGHLIGHTER_QUERY)
        captures = query_cursor.captures(tree.root_node)

        for capture_name in captures:
            for node in captures[capture_name]:
                cursor.setPosition(get_offset(node.start_point))
                cursor.setPosition(get_offset(node.end_point), QTextCursor.MoveMode.KeepAnchor)
                cursor.setCharFormat(STYLES[self.style][capture_name])

        self.highlight_done_once = True

    def rehighlight(self):
        with self.lock:
            if self.working:
                return
            else:
                self.working = True

        try:
            if self.isReadOnly() and self.highlight_done_once:
                return

            cursor: QTextCursor = self.textCursor()
            cursor.setPosition(0)
            cursor.movePosition(QTextCursor.MoveOperation.End, QTextCursor.MoveMode.KeepAnchor)
            cursor.setCharFormat(QTextCharFormat())
            self.highlight()
            self.highlight_done_once = True
        finally:
            self.working = False

    def setCode(self, text: str) -> None:
        self.highlight_done_once = False
        self.setPlainText(text)
        self.rehighlight()
        if not self.signal_connected:
            self.textChanged.connect(self.rehighlight)
            self.signal_connected = True

    def setHighlightStyle(self, style: str) -> None:
        if self.style != style:
            self.style = style
            self.setCode(self.toPlainText())


# class TextEditorWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("Text Editor with Comment Toggle (Ctrl-/)")
#         self.setGeometry(100, 100, 800, 600)
#
#         self.text_edit = QPythonPlainTextEdit()
#         self.setCentralWidget(self.text_edit)
#         # Add sample text
#         sample_text = """
# class A(object):
#     def __init__(a: int):
#         super().__init__()
#         self.a = a
#
# """
#
#         self.text_edit.setCode(sample_text)
#
#
# if __name__ == "__main__":
#     app = QApplication(sys.argv)
#     window = TextEditorWindow()
#     window.show()
#     sys.exit(app.exec())
