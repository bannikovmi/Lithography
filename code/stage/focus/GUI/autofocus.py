from PyQt5.QtCore import pyqtSignal, QThreadPool
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox
)

from stage.focus.API.autoscan import QAutoscanRunner

class QAutoFocusGB(QGroupBox):

    scan_started = pyqtSignal()
    scan_finished = pyqtSignal()
    scan_data_updated = pyqtSignal(list, list)
    var_updated = pyqtSignal(float)
    opt_z_updated = pyqtSignal(float)

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        self.thread_pool = QThreadPool.globalInstance()

        super().__init__("Autoscan params")
        
        self.initUI()
        self.config_widgets()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        # Create widgets
        self.relative_rb = QRadioButton("Relative coords")
        self.absolute_rb = QRadioButton("Absolute coords")

        self.start_lab = QLabel("Start")
        self.stop_lab = QLabel("Stop")
        self.step_lab = QLabel("Step")

        self.start_sb = QSpinBox()
        self.stop_sb = QSpinBox()
        self.step_sb = QSpinBox()

        self.status_lab = QLabel("Status")
        self.status_le = QLineEdit()
        self.status_le.setReadOnly(True)
        self.status_le.setText("Idle")

        # Create and fill layouts
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.relative_rb, 0, 0, 1, 3)
        self.grid.addWidget(self.absolute_rb, 0, 3, 1, 3)

        self.grid.addWidget(self.start_lab, 1, 0)
        self.grid.addWidget(self.stop_lab, 1, 2)
        self.grid.addWidget(self.step_lab, 1, 4)

        self.grid.addWidget(self.start_sb, 1, 1)
        self.grid.addWidget(self.stop_sb, 1, 3)
        self.grid.addWidget(self.step_sb, 1, 5)

        self.grid.addWidget(self.status_lab, 2, 0)
        self.grid.addWidget(self.status_le, 2, 1, 1, 5)

    def config_widgets(self):
        
        # Select relative coords
        self.relative_rb.setChecked(True)

        # Configurate ranges
        self.start_sb.setMinimum(self.config["start"]["min"])
        self.start_sb.setMaximum(self.config["start"]["max"])
        self.start_sb.setSingleStep(self.config["start"]["step"])

        self.stop_sb.setMinimum(self.config["stop"]["min"])
        self.stop_sb.setMaximum(self.config["stop"]["max"])
        self.stop_sb.setSingleStep(self.config["stop"]["step"])

        self.step_sb.setMinimum(self.config["step"]["min"])
        self.step_sb.setMaximum(self.config["step"]["max"])
        self.step_sb.setSingleStep(self.config["step"]["step"])

    def connect_signals(self):
        
        pass

    def set_default_values(self):
        
        self.start_sb.setValue(self.config["start"]["default"])
        self.stop_sb.setValue(self.config["stop"]["default"])
        self.step_sb.setValue(self.config["step"]["default"])

    def on_scan_start(self):

        self.start_pb.disconnect()
        self.start_pb.setText("Abort scan")
        self.start_pb.clicked.connect(self.on_scan_abort)

        # Get drive handler and construct scan params
        # By this time drive and rasp0 should already be initialized
        drive = self.rm[self.config["drive"]["name"]]
        rasp0 = self.rm["rasp0"]
        scan_params = {
            "drive": self.config["drive"],
            "polling_interval": self.config["polling_interval"],
            "start": self.start_sb.value(),
            "stop": self.stop_sb.value(),
            "step": self.step_sb.value(),
            "avg": self.avg_sb.value()
        }

        # Create scan runner and connect signals
        self.scan_runner = QScanRunner(drive, scan_params)
        self.scan_runner.signals.started.connect(self.scan_started)
        self.scan_runner.signals.finished.connect(self.scan_finished)
        self.scan_runner.signals.status_updated.connect(self.status_le.setText)
        self.scan_runner.signals.data_updated.connect(self.scan_data_updated)
        self.scan_runner.signals.opt_z_updated.connect(self.opt_z_updated)

        self.scan_finished.connect(self.on_scan_finish)
        self.var_updated.connect(self.scan_runner.on_var_update)

        # launch scan runner
        self.thread_pool.start(self.scan_runner)

    def on_scan_abort(self):

        self.on_scan_finish()

    def on_scan_finish(self):

        self.start_pb.disconnect()
        self.start_pb.setText("Start scan")
        self.start_pb.clicked.connect(self.on_scan_start)
