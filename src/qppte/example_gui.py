import sys

from PySide6.QtWidgets import QApplication, QMainWindow
from tree_sitter import Point, QueryCursor

from qppte.qpythonplaintextedit import HIGHLIGHTER_QUERY, PYTHON_PARSER, QPythonPlainTextEdit


class TextEditorWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Text Editor with Comment Toggle (Ctrl-/)")
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QPythonPlainTextEdit("light_bold")
        self.setCentralWidget(self.text_edit)
        # Add sample text
        self.sample_text = """@property
def foo() -> None:
    pass
    
@property(x=7)
def moo() -> None:
    pass
"""
        self.text_edit.setCode(self.sample_text)


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

    for capture_name in captures:
        for node in captures[capture_name]:
            start_offset = get_offset(input_lines, node.start_point)
            end_offset = get_offset(input_lines, node.end_point)
            print(
                f"@{capture_name:20} {node.start_point.row:2}:{node.start_point.column:<2} [{window.sample_text[start_offset:end_offset]}]"
            )

    window.show()
    sys.exit(app.exec())
