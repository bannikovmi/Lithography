from PyQt5.QtCore import pyqtSignal, QThreadPool
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QSpinBox
)

from stage.camera.API.af_scan import QScanRunner

class QAFControlGB(QGroupBox):

    scan_started = pyqtSignal()
    scan_finished = pyqtSignal()
    scan_data_updated = pyqtSignal(list, list)
    var_updated = pyqtSignal(float)

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager
        self.thread_pool = QThreadPool.globalInstance()

        super().__init__(self.config["label"])
        
        self.initUI()
        self.config_widgets()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.start_lab = QLabel("Start")
        self.stop_lab = QLabel("Stop")
        self.step_lab = QLabel("Step")
        self.avg_lab = QLabel("Avg")

        self.start_sb = QSpinBox()
        self.stop_sb = QSpinBox()
        self.step_sb = QSpinBox()
        self.avg_sb = QSpinBox()

        self.start_pb = QPushButton("Start scan")
        self.status_le = QLineEdit()
        self.status_le.setReadOnly(True)
        self.status_le.setText("Idle")

        self.grid.addWidget(self.start_lab, 0, 0)
        self.grid.addWidget(self.stop_lab, 0, 2)
        self.grid.addWidget(self.step_lab, 1, 0)
        self.grid.addWidget(self.avg_lab, 1, 2)

        self.grid.addWidget(self.start_sb, 0, 1)
        self.grid.addWidget(self.stop_sb, 0, 3)
        self.grid.addWidget(self.step_sb, 1, 1)
        self.grid.addWidget(self.avg_sb, 1, 3)

        self.grid.addWidget(self.start_pb, 0, 4)
        self.grid.addWidget(self.status_le, 2, 0, 1, 5)

    def config_widgets(self):
        
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

        self.avg_sb.setMinimum(self.config["avg"]["min"])
        self.avg_sb.setMaximum(self.config["avg"]["max"])
        self.avg_sb.setSingleStep(self.config["avg"]["step"])

    def connect_signals(self):
        
        self.start_pb.clicked.connect(self.on_scan_start)

    def set_default_values(self):
        
        self.start_sb.setValue(self.config["start"]["default"])
        self.stop_sb.setValue(self.config["stop"]["default"])
        self.step_sb.setValue(self.config["step"]["default"])
        self.avg_sb.setValue(self.config["avg"]["default"])

    def on_scan_start(self):

        self.start_pb.disconnect()
        self.start_pb.setText("Abort scan")
        self.start_pb.clicked.connect(self.on_scan_abort)

        # Get drive handler and construct scan params
        # By this time drive should already be initialized
        drive = self.rm[self.config["drive"]["name"]]
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
        self.scan_finished.connect(self.on_scan_finish)

        self.var_updated.connect(lambda val: setattr(self.scan_runner, "var", val))

        # launch scan runner
        self.thread_pool.start(self.scan_runner)

    def on_scan_abort(self):

        self.on_scan_finish()

    def on_scan_finish(self):

        self.start_pb.disconnect()
        self.start_pb.setText("Start scan")
        self.start_pb.clicked.connect(self.on_scan_start)
