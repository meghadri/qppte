from PySide6 import QtCore
from PySide6.QtWidgets import QWidget

from PySide6.QtGui import (
    Qt, QFontMetrics, QPainter, QPaintEvent, QResizeEvent
)

class LineNumberPanel(QWidget):
    def __init__(self, editor_parent):
        super().__init__(editor_parent)
        self.editor_parent = editor_parent

    def sizeHint(self):
        return QtCore.QSize(self.editor_parent.sizeHint())

    def resizeEvent(self, event: QResizeEvent) -> None:
        super().resizeEvent(event)

#        if self.ONLY_STUB_TEST_LINE_PANEL is False:
        cr = self.contentsRect();
        self.setGeometry(QtCore.QRect(cr.left(), cr.top(), self.editor_parent.calc_line_number_panel_width(), cr.height()))

    def paintEvent(self, event: QPaintEvent) -> None:
        super(LineNumberPanel, self).paintEvent(event)

        painter = QPainter(self)
        painter.fillRect(event.rect(), Qt.lightGray)
        block = self.editor_parent.firstVisibleBlock()
        block_number = block.blockNumber()
        bounding_rect_of_block: QtCore.QRectF = self.editor_parent.blockBoundingGeometry(block)
        translated_bounding_rect_of_block: QtCore.QRectF = bounding_rect_of_block.translated(self.editor_parent.contentOffset())
        top = translated_bounding_rect_of_block.top()
        bottom = top + self.editor_parent.blockBoundingRect(block).height()

        height = QFontMetrics(self.font()).height()
        while block.isValid() and (top <= event.rect().bottom()):
            if block.isVisible() and (bottom >= event.rect().top()):
                number = str(block_number + 1)
                painter.setPen(Qt.black)
                painter.drawText(0, top, self.width(), height,
                                 Qt.AlignRight | Qt.AlignVCenter, number)
            block = block.next()
            top = bottom
            bottom = top + self.editor_parent.blockBoundingRect(block).height()
            block_number += 1
