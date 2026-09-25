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
    QFrame
)

from qppte.qpythonplaintextedit import QPythonPlainTextEdit
from qppte.style import DEFAULT_STYLES


class TextEditorWindow(QMainWindow):
    @property
    def __DEFAULT_CODE_EDITOR_TEXT(self) -> None:
        return """@property
def foo() -> None:
    pass
    
@property(x=7)
def moo() -> None:
    pass
"""

    @property
    def __DEFAULT_HIGHLIGHT_STYLESET(self) -> tuple:
        # return ('default', 'light_bold')
        return tuple(*DEFAULT_STYLES)

    @property
    def __DEFAULT_HIGHLIGHT_STYLE(self) -> str:
        return 'light_bold'

    @property
    def __DEFAULT_BASE_WINDOW_TITLE(self) -> str:
        return 'QPythonPlainTextEdit Demo'

    def __create_tools_panel(self) -> QWidget:
        tools_panel = QWidget()
        tools_layout = QHBoxLayout()
        tools_panel.setLayout(tools_layout)

        frame1: QFrame = QFrame(tools_panel)
        frame1_layout: QHBoxLayout = QHBoxLayout()
        frame1.setLayout(frame1_layout)
        styles_selector = QComboBox(frame1)
        styles_selector.addItems(self.text_edit.listAvailableHighlightStyles())
        styles_selector.setCurrentText(self.text_edit.getHighlightStyle())

        styles_selector.currentTextChanged.connect(self.text_edit.setHighlightStyle)
        frame1_layout.addWidget(QLabel("Highlighting Style"))
        frame1_layout.addWidget(styles_selector)

        highlighting_enabled_cb = QCheckBox("Highlighting Enabled")
        highlighting_enabled_cb.setChecked(True)
        frame2: QFrame = QFrame(tools_panel)
        frame2_layout: QHBoxLayout = QHBoxLayout()
        frame2.setLayout(frame2_layout)
        frame2_layout.addWidget(highlighting_enabled_cb)

        def toggle_highlighting(enabled: bool):
            self.text_edit.setEnableSyntaxHighlighting(enabled)

        highlighting_enabled_cb.toggled.connect(toggle_highlighting)

        exit_button = QPushButton("Exit")
        tools_layout.addWidget(frame1)
        tools_layout.addWidget(frame2)
        tools_layout.addWidget(exit_button)
        exit_button.clicked.connect(self.close)

        return tools_panel

    def __create_menubar(self) -> QWidget:
        menu_bar = QMenuBar()

        def open_file():
            file_name, _ = QFileDialog.getOpenFileName(
                self, caption="Import project from file", dir=str(Path.home()), filter="*.py"
            )
            if file_name != "":
                self.text_edit.setPlainText(Path(file_name).read_text())

        file_menu = QMenu("&File", menu_bar)
        file_menu.addAction("&Open", open_file)
        file_menu.addSeparator()
        file_menu.addAction("&Quit", self.close)
        menu_bar.addMenu(file_menu)

        edit_menu = QMenu("&Edit", menu_bar)
        edit_menu.addAction(
            "&Undo [Ctrl-Z]",
            lambda: self.text_edit.keyPressEvent(
                QKeyEvent(QtCore.QEvent.Type.KeyPress, Qt.Key.Key_Z, QtCore.Qt.KeyboardModifier.ControlModifier, "z")
            ),
        )
        edit_menu.addAction(
            "&Redo [Ctrl-R]",
            lambda: self.text_edit.keyPressEvent(
                QKeyEvent(QtCore.QEvent.Type.KeyPress, Qt.Key.Key_R, QtCore.Qt.KeyboardModifier.ControlModifier, "z")
            ),
        )
        edit_menu.addSeparator()
        menu_bar.addMenu(edit_menu)

        return menu_bar

    def __init__(self):
        super().__init__()
        self.setWindowTitle(self.__DEFAULT_BASE_WINDOW_TITLE)
        self.setGeometry(100, 100, 800, 600)

        self.text_edit = QPythonPlainTextEdit(self, highlightStyle=self.__DEFAULT_HIGHLIGHT_STYLE)

        root_panel = QWidget()
        self.setCentralWidget(root_panel)

        root_panel_layout = QVBoxLayout()
        root_panel.setLayout(root_panel_layout)

        tools_panel = self.__create_tools_panel()
        root_panel_layout.addWidget(tools_panel)
        root_panel_layout.addWidget(self.text_edit)


        menu_bar = self.__create_menubar()
        self.setMenuBar(menu_bar)

        self.sample_text = self.__DEFAULT_CODE_EDITOR_TEXT
        self.text_edit.setPlainText(self.sample_text)


def __pretty_print(node, input_source_bytes: bytes, indent="", show_matched_text: bool = False):
    # Named nodes represent actual syntax constructs (like 'function_definition')
    # Anonymous nodes are structural literal punctuation (like '{' or ';')
    node_type = node.type if node.is_named else f'"{node.type}"'

    # Print the current node name along with its character span
    matched_text = input_source_bytes[node.start_byte: node.end_byte].decode("utf-8")
    if show_matched_text:
        print(f"{indent}{node_type} [{node.start_byte} - {node.end_byte}] [{matched_text}]")
    else:
        print(f"{indent}{node_type} [{node.start_byte} - {node.end_byte}]")

    # Recursively format all children
    for child in node.children:
        pretty_print(child, input_source_bytes, indent + "  ")


## Redirect everything to stdout

def main():
    app = QApplication(sys.argv)
    window = TextEditorWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
