from PyQt5.QtCore import pyqtProperty, QPointF, Qt
from PyQt5.QtGui import (
    QBrush,
    QColor,
    QLinearGradient,
    QRadialGradient,
    QResizeEvent,
    QPainter,
    QPaintEvent,
    QPen)
from PyQt5.QtWidgets import QAbstractButton

class QRectangularLedIndicator(QAbstractButton):
    
    scaledSize = 1000.0

    def __init__(self, parent=None):
        QAbstractButton.__init__(self, parent)

        self.setMinimumSize(24, 24)
        self.setCheckable(True)

        # Red
        self.on_color_1 = QColor(255, 0, 0)
        self.on_color_2 = QColor(192, 0, 0)
        self.off_color_1 = QColor(28, 0, 0)
        self.off_color_2 = QColor(128, 0, 0)

    def resizeEvent(self, QResizeEvent):
        self.update()

    def paintEvent(self, QPaintEvent):
        realSize = min(self.width(), self.height())

        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)

        painter.setRenderHint(QPainter.Antialiasing)
        # painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(realSize / self.scaledSize, realSize / self.scaledSize)

        gradient = QLinearGradient(QPointF(-450, -450), QPointF(450, 450))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawRect(0, 0, 1000, 1000)

        painter.setPen(pen)
        if self.isChecked():
            gradient = QLinearGradient(QPointF(100, 100), QPointF(900, 900))
            gradient.setColorAt(0, self.on_color_1)
            gradient.setColorAt(1, self.on_color_2)
        else:
            gradient = QLinearGradient(QPointF(100, 100), QPointF(900, 900))
            gradient.setColorAt(0, self.off_color_1)
            gradient.setColorAt(1, self.off_color_2)

        painter.setBrush(gradient)
        painter.drawRect(100, 100, 900, 900)

    @pyqtProperty(QColor)
    def onColor1(self):
        return self.on_color_1

    @onColor1.setter
    def onColor1(self, color):
        self.on_color_1 = color

    @pyqtProperty(QColor)
    def onColor2(self):
        return self.on_color_2

    @onColor2.setter
    def onColor2(self, color):
        self.on_color_2 = color

    @pyqtProperty(QColor)
    def offColor1(self):
        return self.off_color_1

    @offColor1.setter
    def offColor1(self, color):
        self.off_color_1 = color

    @pyqtProperty(QColor)
    def offColor2(self):
        return self.off_color_2

    @offColor2.setter
    def offColor2(self, color):
        self.off_color_2 = color

class QRoundLedIndicator(QAbstractButton):
    scaledSize = 1000.0

    def __init__(self, parent=None):
        QAbstractButton.__init__(self, parent)

        self.setMinimumSize(24, 24)
        self.setCheckable(True)

        # Green
        self.on_color_1 = QColor(255, 0, 0)
        self.on_color_2 = QColor(192, 0, 0)
        self.off_color_1 = QColor(28, 0, 0)
        self.off_color_2 = QColor(128, 0, 0)

    def resizeEvent(self, QResizeEvent):
        self.update()

    def paintEvent(self, QPaintEvent):
        realSize = min(self.width(), self.height())

        painter = QPainter(self)
        pen = QPen(Qt.black)
        pen.setWidth(1)

        painter.setRenderHint(QPainter.Antialiasing)
        painter.translate(self.width() / 2, self.height() / 2)
        painter.scale(realSize / self.scaledSize, realSize / self.scaledSize)

        gradient = QRadialGradient(QPointF(-500, -500), 1500, QPointF(-500, -500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 500, 500)

        gradient = QRadialGradient(QPointF(500, 500), 1500, QPointF(500, 500))
        gradient.setColorAt(0, QColor(224, 224, 224))
        gradient.setColorAt(1, QColor(28, 28, 28))
        painter.setPen(pen)
        painter.setBrush(QBrush(gradient))
        painter.drawEllipse(QPointF(0, 0), 450, 450)

        painter.setPen(pen)
        if self.isChecked():
            gradient = QRadialGradient(QPointF(-500, -500), 1500, QPointF(-500, -500))
            gradient.setColorAt(0, self.on_color_1)
            gradient.setColorAt(1, self.on_color_2)
        else:
            gradient = QRadialGradient(QPointF(500, 500), 1500, QPointF(500, 500))
            gradient.setColorAt(0, self.off_color_1)
            gradient.setColorAt(1, self.off_color_2)

        painter.setBrush(gradient)
        painter.drawEllipse(QPointF(0, 0), 400, 400)

    @pyqtProperty(QColor)
    def onColor1(self):
        return self.on_color_1

    @onColor1.setter
    def onColor1(self, color):
        self.on_color_1 = color

    @pyqtProperty(QColor)
    def onColor2(self):
        return self.on_color_2

    @onColor2.setter
    def onColor2(self, color):
        self.on_color_2 = color

    @pyqtProperty(QColor)
    def offColor1(self):
        return self.off_color_1

    @offColor1.setter
    def offColor1(self, color):
        self.off_color_1 = color

    @pyqtProperty(QColor)
    def offColor2(self):
        return self.off_color_2

    @offColor2.setter
    def offColor2(self, color):
        self.off_color_2 = color

# import sys
# from PyQt5.QtWidgets import QApplication, QMainWindow, QGridLayout, QWidget

# class MainWindow(QMainWindow):

#     def __init__(self):

#         super().__init__()
#         self.initUI()

#     def initUI(self):

#         self.grid = QGridLayout()

#         self.main_widget = QWidget()
#         self.setCentralWidget(self.main_widget)
#         self.main_widget.setLayout(self.grid)

#         self.round_led = QRoundLedIndicator()
#         self.rect_led = QRectangularLedIndicator()
#         # self.grid.addWidget(self.round_led)
#         self.grid.addWidget(self.rect_led)

#         self.show()

# def main():

#     app = QApplication(sys.argv)
#     window = MainWindow()

#     sys.exit(app.exec_())

# if __name__ == '__main__':
#     main()
