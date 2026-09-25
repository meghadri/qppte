from PySide6 import QtCore
from PySide6.QtWidgets import QWidget

from PySide6.QtGui import (
    Qt, QFontMetrics, QPainter, QPaintEvent
)

class LineNumberPanel(QWidget):
    def __init__(self, editor_parent):
        super().__init__(editor_parent)
        self.editor_parent = editor_parent

    def sizeHint(self):
        return QtCore.QSize(self.editor_parent.sizeHint())

    def paintEvent(self, event: QPaintEvent) -> None:
        super(LineNumberPanel, self).paintEvent(event)
        print(f"LineNumberPanel.paintEvent: event.rect = {event.rect()}, event.region = {event.region()}")
        # self.editor_parent.paintEvent(event)
        # self.editor_parent.update()
        # region Description
        if True: #self.ONLY_STUB_TEST_LINE_PANEL is False:
            painter = QPainter(self)
            if True: # self.ONLY_STUB_TEST_LINE_PANEL is False:
                painter.fillRect(event.rect(), Qt.lightGray)
                block = self.editor_parent.firstVisibleBlock()
                blockNumber = block.blockNumber()
                boundingRectOfBlock: QtCore.QRectF = self.editor_parent.blockBoundingGeometry(block)
                translatedBoundingRectOfBlock: QtCore.QRectF = boundingRectOfBlock.translated(self.editor_parent.contentOffset())
                top = translatedBoundingRectOfBlock.top()
                bottom = top + self.editor_parent.blockBoundingRect(block).height()

                # Just to make sure I use the right font
                height = QFontMetrics(self.font()).height()
                print(
                    f"QPythonPlainTextEdit.line_number_area_paint_event: block = {block}, blockNumber = {blockNumber}, top = {top}, bottom = {bottom}, height = {height}")
                while block.isValid() and (top <= event.rect().bottom()):
                    print(
                        f"QPythonPlainTextEdit.line_number_area_paint_event: block = {block}, block.isValid = {block.isValid()}, block.isVisible() = {block.isVisible()}, blockNumber = {blockNumber}, top = {top}, bottom = {bottom}, event.rect().top() = {event.rect().top()}m, event.rect().bottom() = {event.rect().bottom()},  height = {height}")
                    if block.isVisible() and (bottom >= event.rect().top()):
                        number = str(blockNumber + 1)
                        painter.setPen(Qt.black)
                        painter.drawText(0, top, self.width(), height,
                                         Qt.AlignRight | Qt.AlignVCenter, number)
                        print(
                            f"QPythonPlainTextEdit.line_number_area_paint_event: block = {block}, block.isVisible = {block.isVisible()}, blockNumber = {blockNumber}, top = {top}, bottom = {bottom}, width = {self.width()},  height = {height}, number = {number}")

                    block = block.next()
                    top = bottom
                    bottom = top + self.editor_parent.blockBoundingRect(block).height()
                    blockNumber += 1

            # painter.end()
        # endregion


