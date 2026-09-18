import sys
from pathlib import Path

from PySide6 import QtCore
from PySide6.QtGui import QKeyEvent, Qt
from PySide6.QtWidgets import (
    QApplication,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMenu,
    QMenuBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qppte.qpythonplaintextedit import QPythonPlainTextEdit


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
        styles_selector.addItems(text_edit.listAvailableHighlightStyles())
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

        menu_bar = QMenuBar()

        def open_file():
            file_name, _ = QFileDialog.getOpenFileName(
                self, caption="Import project from file", dir=str(Path.home()), filter="*.py"
            )
            if file_name != "":
                text_edit.setPlainText(Path(file_name).read_text())

        file_menu = QMenu("&File", menu_bar)
        file_menu.addAction("&Open", open_file)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)
        menu_bar.addMenu(file_menu)

        edit_menu = QMenu("&Edit", menu_bar)
        edit_menu.addAction(
            "&Undo [Ctrl-Z]",
            lambda: text_edit.keyPressEvent(
                QKeyEvent(QtCore.QEvent.Type.KeyPress, Qt.Key.Key_Z, QtCore.Qt.KeyboardModifier.ControlModifier, "z")
            ),
        )
        edit_menu.addAction(
            "&Redo [Ctrl-R]",
            lambda: text_edit.keyPressEvent(
                QKeyEvent(QtCore.QEvent.Type.KeyPress, Qt.Key.Key_R, QtCore.Qt.KeyboardModifier.ControlModifier, "z")
            ),
        )
        edit_menu.addSeparator()
        menu_bar.addMenu(edit_menu)

        self.setMenuBar(menu_bar)


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


def main():
    app = QApplication(sys.argv)
    window = TextEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
