from PyQt5.QtGui import QFont
import pyqtgraph as pg

class QAF_plot_widget(pg.PlotWidget):

    def __init__(self, config):

        self.config = config
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setBackground('w')

        self.styles = {'color':'b', 'font-size':'20pt'}
        self.setLabel('bottom', 'Position', **self.styles)
        self.setLabel('left', 'Focus merit (a. u.)', **self.styles)
        
        self.ticks_font = QFont()
        self.ticks_font.setPixelSize(20)
        self.plotItem.getAxis("bottom").setTickFont(self.ticks_font)
        self.plotItem.getAxis("left").setTickFont(self.ticks_font)

        self.plotItem.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(0, 0, 0), width=3)

        self.line = self.plotItem.plot([], [], pen=self.pen)
