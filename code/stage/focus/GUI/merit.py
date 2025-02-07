from collections import deque

from numpy import mean

# pyqt-related imports
from PyQt5.QtCore import pyqtSignal 
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QSpinBox
)

class QMeritGB(QGroupBox):

    mean_updated = pyqtSignal(float)

    def __init__(self, config):

        self.config = config

        super().__init__("Focus merit")
    
        self.deq = deque([], maxlen=self.config["avg"]["default"])

        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):
        
        self.setStyleSheet("background-color: white;")

        # Create widgets
        self.laplace_lab = QLabel("Laplacian var")
        self.merit_le = QLineEdit()
        self.merit_le.setReadOnly(True)

        self.avg_lab = QLabel("Avg frames")
        self.avg_sb = QSpinBox()

        # Create and fill layout
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.laplace_lab, 0, 0)
        self.grid.addWidget(self.merit_le, 1, 0)
        self.grid.addWidget(self.avg_lab, 2, 0)
        self.grid.addWidget(self.avg_sb, 3, 0)

        # Configurate widgets
        self.avg_sb.setMinimum(self.config["avg"]["min"])
        self.avg_sb.setMaximum(self.config["avg"]["max"])
        self.avg_sb.setSingleStep(self.config["avg"]["step"])

    def connect_signals(self):

        self.avg_sb.valueChanged.connect(self.on_avg_change)

    def set_default_values(self):

        self.avg_sb.setValue(self.config["avg"]["default"])

    def on_avg_change(self, val):

        self.deq = deque(self.deq, maxlen=val)

    def on_var_update(self, val):

        self.deq.append(val)
        mean_val = mean(self.deq)
        self.merit_le.setText(f"{mean_val:.3f}")
        self.mean_updated.emit(mean_val)
