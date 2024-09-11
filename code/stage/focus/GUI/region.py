from PyQt5.QtCore import pyqtSignal, QRect

from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QSpinBox,
    QVBoxLayout
)

class QFocusRegionGB(QGroupBox):
    
    rect_updated = pyqtSignal(QRect)

    def __init__(self, config):

        self.config = config
        self.rect = QRect()
        
        super().__init__("Target region")
        self.initUI()
        self.config_widgets()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.grid = QGridLayout()
        self.vbox = QVBoxLayout()
        self.setLayout(self.grid)

        self.x1_lab = QLabel("x1")
        self.x2_lab = QLabel("x2")
        self.y1_lab = QLabel("y1")
        self.y2_lab = QLabel("y2")

        self.x1_sb = QSpinBox()
        self.y1_sb = QSpinBox()
        self.x2_sb = QSpinBox()
        self.y2_sb = QSpinBox()

        self.show_rect_cb = QCheckBox("Show rectangle")
        self.show_cross_cb = QCheckBox("Show crosses")
        self.transform_cb = QCheckBox("Transform region")

        self.grid.addWidget(self.x1_lab, 0, 0)
        self.grid.addWidget(self.x2_lab, 1, 0)
        self.grid.addWidget(self.y1_lab, 0, 2)
        self.grid.addWidget(self.y2_lab, 1, 2)

        self.grid.addWidget(self.x1_sb, 0, 1)
        self.grid.addWidget(self.x2_sb, 1, 1)
        self.grid.addWidget(self.y1_sb, 0, 3)
        self.grid.addWidget(self.y2_sb, 1, 3)

        self.grid.addLayout(self.vbox, 2, 0, 1, 4)
        self.vbox.addWidget(self.show_rect_cb)
        self.vbox.addWidget(self.show_cross_cb)

    def config_widgets(self):

        # Configurate ranges
        self.x1_sb.setMinimum(self.config["x"]["margin"])
        self.x2_sb.setMaximum(self.config["x"]["range"] - self.config["x"]["margin"])
        self.y1_sb.setMinimum(self.config["y"]["margin"])
        self.y2_sb.setMaximum(self.config["y"]["range"] - self.config["y"]["margin"])

    def connect_signals(self):

        # Update rectangle
        self.x1_sb.valueChanged.connect(self.update_rectangle)
        self.x2_sb.valueChanged.connect(self.update_rectangle)
        self.y1_sb.valueChanged.connect(self.update_rectangle)
        self.y2_sb.valueChanged.connect(self.update_rectangle)

        # Adjust ranges
        self.x1_sb.valueChanged.connect(lambda val:
            self.x2_sb.setMinimum(val + self.config["x"]["min_length"]))
        self.x2_sb.valueChanged.connect(lambda val:
            self.x1_sb.setMaximum(val - self.config["x"]["min_length"]))
        self.y1_sb.valueChanged.connect(lambda val:
            self.y2_sb.setMinimum(val + self.config["y"]["min_length"]))
        self.y2_sb.valueChanged.connect(lambda val:
            self.y1_sb.setMaximum(val - self.config["y"]["min_length"]))
        
    def set_default_values(self):

        self.x1_sb.setValue(self.config["x"]["default_low"])
        self.x2_sb.setValue(self.config["x"]["default_high"])
        self.y1_sb.setValue(self.config["y"]["default_low"])
        self.y2_sb.setValue(self.config["y"]["default_high"])

    def update_rectangle(self):

        x1 = self.x1_sb.value()
        y1 = self.y1_sb.value()
        width = self.x2_sb.value() - x1
        height = self.y2_sb.value() - y1

        self.rect = QRect(x1, y1, width, height)
        self.rect_updated.emit(self.rect)
