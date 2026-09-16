import sys

from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QWidget,
)
from tree_sitter import Node, Point, QueryCursor

from qppte.qpythonplaintextedit import HIGHLIGHTER_QUERY, PYTHON_PARSER, QPythonPlainTextEdit


class TextEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("QPythonPlainTextEdit Demo")
        self.setGeometry(100, 100, 800, 600)

        text_edit = QPythonPlainTextEdit(highlightStyle="light_bold")

        root_panel = QWidget()
        layout = QVBoxLayout()
        root_panel.setLayout(layout)

        styles_selector = QComboBox()
        styles_selector.addItems(QPythonPlainTextEdit.listHighlightStyles())
        styles_selector.setCurrentText(text_edit.getHighlightStyle())

        styles_selector.currentTextChanged.connect(text_edit.setHighlightStyle)

        tools_panel = QWidget()
        tools_layout = QHBoxLayout()
        tools_panel.setLayout(tools_layout)
        tools_layout.addWidget(QLabel("Highlighting Style"))
        tools_layout.addWidget(styles_selector)
        tools_layout.addWidget(QLabel("        "))

        highlighting_enabled_cb = QCheckBox("Highlighting Enabled")
        tools_layout.addWidget(highlighting_enabled_cb)
        highlighting_enabled_cb.setChecked(True)

        def toggle_highlighting(enabled: bool):
            text_edit.setEnableSyntaxHighlighting(enabled)

        highlighting_enabled_cb.toggled.connect(toggle_highlighting)

        tools_layout.addWidget(QLabel(""), stretch=1)

        exit_button = QPushButton("Exit")
        tools_layout.addWidget(exit_button)
        exit_button.clicked.connect(self.close)

        layout.addWidget(tools_panel)

        layout.addWidget(text_edit)

        self.setCentralWidget(root_panel)

        self.sample_text = """@property
def foo() -> None:
    pass
    
@property(x=7)
def moo() -> None:
    pass
"""
        text_edit.setPlainText(self.sample_text)


def pretty_print(node, input_source_bytes: bytes, indent="", show_matched_text: bool = False):
    # Named nodes represent actual syntax constructs (like 'function_definition')
    # Anonymous nodes are structural literal punctuation (like '{' or ';')
    node_type = node.type if node.is_named else f'"{node.type}"'

    # Print the current node name along with its character span
    matched_text = input_source_bytes[node.start_byte : node.end_byte].decode("utf-8")
    if show_matched_text:
        print(f"{indent}{node_type} [{node.start_byte} - {node.end_byte}] [{matched_text}]")
    else:
        print(f"{indent}{node_type} [{node.start_byte} - {node.end_byte}]")

    # Recursively format all children
    for child in node.children:
        pretty_print(child, input_source_bytes, indent + "  ")


def get_offset(lines: list[str], p: Point) -> int:
    return sum([len(line) for line in lines[0 : p.row]]) + p.column + p.row


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TextEditorWindow()

    # show parsed tree
    input_lines = window.sample_text.splitlines()
    input_text_bytes = window.sample_text.encode()
    tree = PYTHON_PARSER.parse(input_text_bytes)
    print("=========== PARSED TREE ===========")
    pretty_print(tree.root_node, input_text_bytes, show_matched_text=False)
    print("===================================")

    # do query and show captured results
    print("=========== QUERY RESULTS ===========")
    query_cursor = QueryCursor(HIGHLIGHTER_QUERY)
    captures = query_cursor.captures(tree.root_node)

    matches: list[tuple[int, dict[str, list[Node]]]] = query_cursor.matches(tree.root_node)
    matches.sort(key=lambda m: m[0])
    for _, m in matches:
        for capture_name, nodes in m.items():
            for node in nodes:
                start_offset = get_offset(input_lines, node.start_point)
                end_offset = get_offset(input_lines, node.end_point)
                print(
                    f"@{capture_name:20} {node.start_point.row:2}:{node.start_point.column:<2}"
                    f" [{window.sample_text[start_offset:end_offset]}]"
                )

    window.show()
    sys.exit(app.exec())
