from PyQt5.QtCore import pyqtSignal, QDate, Qt, QTime
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QMenu,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QWidgetAction
)

import pyqtgraph as pg
from stage.focus.API.recorder import QFocusRecorder
from stage.focus.GUI.modes import DriveMode, ScanMode

class QFocusScannerGB(QGroupBox):
    
    var_updated = pyqtSignal(float)
    scan_started = pyqtSignal()
    scan_finished = pyqtSignal()

    def __init__(self, config, resource_manager):

        super().__init__("Scanner")
        
        self.config = config
        self.rm = resource_manager

        # Default modes and average
        self.scan_mode = ScanMode.NONE
        self.drive_mode = DriveMode.SUBSTRATE
        self.avg_frames = 5

        self.initUI()
        self.connect_signals()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.start_pb = QPushButton("Start")
        self.save_cb = QCheckBox("Save data")
        self.auto_path_cb = QCheckBox("Auto path")

        # Plot dropdown menu
        self.plot_pb = QPushButton("Show plot")
        self.plot_menu = QMenu()
        self.plot_pb.setMenu(self.plot_menu)
        self.plot_menu.setLayoutDirection(Qt.RightToLeft)

        self.plot_qwa = QWidgetAction(self.plot_menu)
        self.pw = QFocusPW(self.config["plot"])
        self.plot_qwa.setDefaultWidget(self.pw)
        self.plot_menu.addAction(self.plot_qwa)

        self.save_cb.setChecked(True)
        self.auto_path_cb.setChecked(True)

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.grid.addWidget(self.start_pb, 0, 0)
        self.grid.addWidget(self.save_cb, 1, 0)
        self.grid.addWidget(self.auto_path_cb, 2, 0)
        self.grid.addWidget(self.plot_pb, 3, 0)

    def connect_signals(self):

        self.start_pb.clicked.connect(self.on_scan_start)
        self.save_cb.stateChanged.connect(self.auto_path_cb.setEnabled)

    def on_drive_mode_change(self, mode):

        self.drive_mode = mode
        if mode == DriveMode.SUBSTRATE:
            self.pw.setLabel('bottom', 'Z position', **self.pw.styles)
        else:
            self.pw.setLabel('bottom', 'Lense position', **self.pw.styles)

    def on_scan_start(self):

        self.scan_started.emit()

        self.save_cb.setDisabled(True)
        self.auto_path_cb.setDisabled(True)

        # Change pb behaviour
        self.start_pb.clicked.disconnect()
        if self.scan_mode == ScanMode.MANUAL:
            self.start_pb.setText("Stop")
            self.start_pb.clicked.connect(self.on_scan_stop)
        else:
            self.start_pb.setText("Abort")
            self.start_pb.clicked.connect(self.on_scan_abort)

        # Choose drive
        if self.drive_mode == DriveMode.SUBSTRATE:
            drive = self.rm["DRZ"]
        else:
            drive = self.rm["DRL"]

        # Select file path
        if self.save_cb.isChecked():

            data_dir = "../data/af_scans"

            if self.auto_path_cb.isChecked():
                # Generate path automatically
                date = QDate.currentDate().toString(Qt.ISODate) 
                time = QTime.currentTime().toString()
                file_path = f"{data_dir}/{date}_{time}.dat"
            else:
                # Show file dialog
                file_path = QFileDialog.getSaveFileName(
                    caption="Data file path", directory=data_dir)[0]

        else:
            file_path = None

        # Write header
        if file_path:
            with open(file_path, "w") as file:
                file.write("#Pos (steps),\tMerit (a. u.)\n")

        # Construct record params and create recorder
        record_params = {
            "scan_mode": self.scan_mode,
            "file_path": file_path,
            "avg_frames": self.avg_frames
        }
        self.recorder = QFocusRecorder(drive, record_params)

        # Connect recorder signals
        self.var_updated.connect(self.recorder.on_var_update)
        self.recorder.data_updated.connect(self.pw.line.setData)

        self.recorder.start()

    def on_scan_abort(self):

        self.on_scan_stop()

    def on_scan_stop(self):

        self.recorder.stop()

        self.start_pb.clicked.disconnect()
        self.start_pb.setText("Start")
        self.scan_finished.emit()

        self.save_cb.setDisabled(False)
        if self.save_cb.isChecked():
            self.auto_path_cb.setDisabled(False)

        self.start_pb.clicked.connect(self.on_scan_start)

    # def on_record_start(self):

    #     self.record_pb.clicked.disconnect()
    #     self.record_pb.clicked.connect(self.on_record_stop)
    #     self.record_pb.setText("Stop recording")
    #     self.avg_sb.setDisabled(True)

    #     if self.sub_rb.isChecked():
    #         drive = self.rm["DRZ"]
    #     else: # proj_rb is checked
    #         drive = self.rm["DRL"]

    #     self.recorder = QFocusRecorder(drive, self.save_cb.isChecked(), self.avg_sb.value())
    #     self.recorder.data_updated.connect(lambda pos, var:
    #         self.pw.line.setData(pos, var))
    #     self.var_updated.connect(self.recorder.on_var_update)

    #     self.recorder.start()

    # def on_record_stop(self):

    #     self.record_pb.clicked.disconnect()
    #     self.record_pb.clicked.connect(self.on_record_start)
    #     self.record_pb.setText("Start recording")
    #     self.avg_sb.setDisabled(False)

    #     self.var_updated.disconnect()

    #     self.recorder.stop()

class QFocusPW(pg.PlotWidget):

    def __init__(self, config):

        self.config = config
        super().__init__()

        self.initUI()

    def initUI(self):

        self.setBackground('w')

        self.styles = {
            'color': self.config["color"],
            'font-size': self.config["font-size"]
        }
        self.setLabel('bottom', 'Z Position', **self.styles)
        self.setLabel('left', 'Focus merit (a. u.)', **self.styles)
        
        self.ticks_font = QFont()
        self.ticks_font.setPixelSize(20)
        self.plotItem.getAxis("bottom").setTickFont(self.ticks_font)
        self.plotItem.getAxis("left").setTickFont(self.ticks_font)

        self.plotItem.showGrid(x=True, y=True)
        self.pen = pg.mkPen(color=(0, 0, 0), width=3)

        self.line = self.plotItem.plot([], [], pen=self.pen)
