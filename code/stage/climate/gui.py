# pyqt-related imports
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QDoubleSpinBox,
    )

class QAHTWidget(QGroupBox):

    def __init__(self, config, resource_manager):

        super().__init__("Climate")
        self.config = config
        self.rm = resource_manager
        self.initUI()

        self.request_HT()

        self.timer = QTimer()
        self.timer.setInterval(30000)
        self.timer.timeout.connect(self.request_HT)

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.temp_label = QLabel("Temperature [°C]")
        self.temp_le = QLineEdit()
        self.temp_le.setReadOnly(True)

        self.hum_label = QLabel("Humidity [%]")
        self.hum_le = QLineEdit()
        self.hum_le.setReadOnly(True)

        self.update_label = QLabel("Update interval [s]")
        self.update_sb = QDoubleSpinBox()
        self.update_sb.setMinimum(0.5)
        self.update_sb.setMaximum(100)
        self.update_sb.setValue(30)
        self.update_sb.valueChanged.connect(lambda val:
            self.timer.setInterval(int(val*1e3)))

        self.grid.addWidget(self.temp_label, 0, 0)
        self.grid.addWidget(self.temp_le, 0, 1)
        self.grid.addWidget(self.hum_label, 1, 0)
        self.grid.addWidget(self.hum_le, 1, 1)
        self.grid.addWidget(self.update_label, 0, 2)
        self.grid.addWidget(self.update_sb, 1, 2)

    def request_HT(self):

        pass
        # self.ESP.write("AHT_GTM")

    def updateUI(self, message):

        try:
            self.temp_le.setText(message.arguments[0])
            self.hum_le.setText(message.arguments[1])
        except IndexError:
            pass

