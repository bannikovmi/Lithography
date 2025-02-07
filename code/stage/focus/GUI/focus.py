from PyQt5.QtCore import pyqtSignal, QRect, Qt
from PyQt5.QtWidgets import (
    QCheckBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox
    )

from stage.focus.GUI.region import QFocusRegionGB
from stage.focus.GUI.merit import QMeritGB
from stage.focus.GUI.modes import DriveMode, QDriveModeGB, QScanModeGB, ScanMode
from stage.focus.GUI.autofocus import QAutoFocusGB
from stage.focus.GUI.scanner import QFocusScannerGB

class QFocusGB(QGroupBox):

    var_updated = pyqtSignal(float)
    sub_scan_started = pyqtSignal()
    sub_scan_finished = pyqtSignal()
    proj_scan_started = pyqtSignal()
    proj_scan_finished = pyqtSignal()
    opt_z_updated = pyqtSignal(float)

    rect_updated = pyqtSignal(QRect)
    show_rect = pyqtSignal(int)
    show_cross = pyqtSignal(int)

    def __init__(self, config, resource_manager):

        self.config = config
        self.rm = resource_manager

        super().__init__("Focus")
        
        self.initUI()
        self.connect_signals()

    def initUI(self):

        # Create widgets
        self.region_gb = QFocusRegionGB(self.config["region"])
        self.merit_gb = QMeritGB(self.config["merit"])
        self.drive_mode_gb = QDriveModeGB()
        self.scan_mode_gb = QScanModeGB()
        self.scanner_gb = QFocusScannerGB(self.config["scanner"], self.rm)
        self.auto_gb = QAutoFocusGB(self.config["sub_focus"], self.rm)

        # Create layout
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Fill layouts
        self.grid.addWidget(self.region_gb, 0, 0, 2, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.merit_gb, 0, 1, 2, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.drive_mode_gb, 0, 2)
        self.grid.addWidget(self.scan_mode_gb, 1, 2)
        self.grid.addWidget(self.scanner_gb, 0, 3, 2, 1, alignment=Qt.AlignLeft)
        self.grid.addWidget(self.auto_gb, 0, 4, 2, 1, alignment=Qt.AlignLeft)

        self.grid.setColumnStretch(5, 1)

        # Configurate widgets
        self.auto_gb.setDisabled(True)
        self.scanner_gb.setDisabled(True)

    def connect_signals(self):

        self.var_updated.connect(self.merit_gb.on_var_update)

        self.region_gb.show_rect_cb.stateChanged.connect(self.show_rect)
        self.region_gb.show_cross_cb.stateChanged.connect(self.show_cross)
        self.region_gb.rect_updated.connect(self.rect_updated)
        
        self.scan_mode_gb.mode_changed.connect(lambda mode:
            setattr(self.scanner_gb, "scan_mode", mode))
        self.scan_mode_gb.mode_changed.connect(self.on_scan_mode_change)
        self.drive_mode_gb.mode_changed.connect(self.on_drive_mode_change)

        self.scanner_gb.scan_started.connect(lambda:
            self.scan_mode_gb.setDisabled(True))
        self.scanner_gb.scan_finished.connect(lambda:
            self.scan_mode_gb.setDisabled(False))

        self.scanner_gb.scan_started.connect(lambda:
            self.drive_mode_gb.setDisabled(True))
        self.scanner_gb.scan_finished.connect(lambda:
            self.drive_mode_gb.setDisabled(False))

        self.scanner_gb.scan_started.connect(lambda:
            self.merit_gb.avg_sb.setDisabled(True))
        self.scanner_gb.scan_finished.connect(lambda:
            self.merit_gb.avg_sb.setDisabled(False))

        self.merit_gb.mean_updated.connect(self.scanner_gb.var_updated)
        self.merit_gb.avg_sb.valueChanged.connect(lambda val:
            setattr(self.scanner_gb, "avg_frames", val))

        # self.var_updated.connect(self.af_control_sub.var_updated)
        # self.var_updated.connect(self.af_control_proj.var_updated)
        # self.var_updated.connect(self.af_plotter.var_updated)
        
        # self.af_control_sub.scan_started.connect(self.sub_scan_started)
        # self.af_control_sub.scan_finished.connect(self.sub_scan_finished)
        # self.af_control_proj.scan_started.connect(self.proj_scan_started)
        # self.af_control_proj.scan_finished.connect(self.proj_scan_finished)

        # self.af_control_sub.opt_z_updated.connect(self.opt_z_updated)
        # self.af_control_proj.opt_z_updated.connect(self.opt_z_updated)

        # self.af_control_sub.scan_data_updated.connect(lambda pos, var:
        #     self.af_plotter.pw.line.setData(pos, var))
        # self.af_control_proj.scan_data_updated.connect(lambda pos, var:
        #     self.af_plotter.pw.line.setData(pos, var))

    def on_scan_mode_change(self, mode):

        self.scanner_gb.scan_mode = mode

        if mode == ScanMode.NONE:
            self.auto_gb.setDisabled(True)
            self.scanner_gb.setDisabled(True)
        elif mode == ScanMode.MANUAL:
            self.auto_gb.setDisabled(True)
            self.scanner_gb.setDisabled(False)
        else:
            self.auto_gb.setDisabled(False)
            self.scanner_gb.setDisabled(False)

    def on_drive_mode_change(self, mode):

        self.scanner_gb.on_drive_mode_change(mode)
        # Remove old auto groupbox
        self.grid.removeWidget(self.auto_gb)

        # Create new auto groupbox
        if mode == DriveMode.SUBSTRATE:
            self.auto_gb = QAutoFocusGB(self.config["sub_focus"], self.rm)
        if mode == DriveMode.PROJECTOR:
            self.auto_gb = QAutoFocusGB(self.config["proj_focus"], self.rm)

        # Add new groupbox to layout
        self.grid.addWidget(self.auto_gb, 0, 4, 2, 1, alignment=Qt.AlignLeft)
        # Set auto gb disabled if auto rb is not checked
        if not self.scan_mode_gb.auto_rb.isChecked():
            self.auto_gb.setDisabled(True)

        self.grid.setColumnStretch(5, 1)
