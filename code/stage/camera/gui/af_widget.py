from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QWidget
    )

from .af_region import QAFRegionGB
from .af_control import QAFControlGB
from .af_plot import QAF_plot_widget

class QAutofocusWidget(QWidget):

    var_updated = pyqtSignal(float)
    sub_scan_started = pyqtSignal()
    sub_scan_finished = pyqtSignal()
    proj_scan_started = pyqtSignal()
    proj_scan_finished = pyqtSignal()

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager

        super().__init__()
        
        self.initUI()
        self.connect_signals()

        # self.set_default_values()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.af_region = QAFRegionGB(self.config["region"])
        self.af_control_sub = QAFControlGB(self.config["sub_focus"], self.rm)
        self.af_control_proj = QAFControlGB(self.config["proj_focus"], self.rm)
        self.af_plot = QAF_plot_widget(self.config["plot"])

        self.grid.addWidget(self.af_region, 0, 0)
        self.grid.addWidget(self.af_control_sub, 1, 0, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.af_control_proj, 2, 0, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.af_plot, 0, 1, 3, 1)

    def connect_signals(self):

        self.var_updated.connect(self.af_control_sub.var_updated)
        self.var_updated.connect(self.af_control_proj.var_updated)
        
        self.af_control_sub.scan_started.connect(self.sub_scan_started)
        self.af_control_sub.scan_finished.connect(self.sub_scan_finished)
        self.af_control_proj.scan_started.connect(self.proj_scan_started)
        self.af_control_proj.scan_finished.connect(self.proj_scan_finished)

        self.af_control_sub.scan_data_updated.connect(lambda pos, var:
            self.af_plot.line.setData(pos, var))
