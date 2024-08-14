# pyqt-related imports
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMenu,
    QPushButton,
    QRadioButton,
    QSpinBox,
    QWidget,
    QWidgetAction
    )

from widgets.numeric import QNumericControl

class QDriveParams(QGroupBox):

    def __init__(self, config):

        self.config = config

        super().__init__(self.config["label"])

        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.hbox = QHBoxLayout()
        self.grid.addLayout(self.hbox, 0, 0)

        self.power_cb = QCheckBox("Power")
        self.settings_pb = QPushButton("Settings")

        self.divider_lab = QLabel("Step divider")
        self.divider_cmb = QComboBox()

        self.hbox.addWidget(self.power_cb, 0)
        self.hbox.addWidget(self.settings_pb, 1)
        self.hbox.addWidget(self.divider_lab, 2)
        self.hbox.addWidget(self.divider_cmb, 3)

        for div in self.config["step_div"]["predef"]:
            self.divider_cmb.addItem(str(div))
        
        self.hbox.setStretch(0, 0)
        self.hbox.setStretch(1, 0)
        self.hbox.setStretch(2, 0)
        self.hbox.addStretch(1)

        self.steps_ctrl = QStepsControl(self.config)
        self.grid.addWidget(self.steps_ctrl, 1, 0)

        # Set widget params
        self.settings_menu = QMenu()
        self.settings_pb.setMenu(self.settings_menu)

        self.settings_qwa = QWidgetAction(self.settings_menu)
        self.drive_settings = QDriveSettings(self.config)
        self.settings_qwa.setDefaultWidget(self.drive_settings)
        self.settings_menu.addAction(self.settings_qwa)

class QStepsControl(QNumericControl):

    def __init__(self, config):

        self.config = config

        super().__init__(label="Steps", units="")
        self.extendUI()

    def extendUI(self):

        self.setMinimum(self.config["steps"]["min"])
        self.setMaximum(self.config["steps"]["max"])
        self.setMapper("log10")

        self.setValue(self.config["steps"]["default"])

        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.vbox.addLayout(self.hbox2, 1)
        self.vbox.addLayout(self.hbox3, 2)

        for ind, step in enumerate(self.config["steps"]["predef"]):
            step_pb = QPushButton(f"{step}")

            if ind < 3:
                self.hbox2.addWidget(step_pb)
            else:
                self.hbox3.addWidget(step_pb)
            step_pb.clicked.connect(self.on_pb_click)

    def on_pb_click(self):

        step = float(self.sender().text())
        self.setValue(step)

class QDriveSettings(QWidget):

    def __init__(self, config):

        self.config = config

        super().__init__()
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.speed_ctrl = QSpeedControl(self.config)
        self.grid.addWidget(self.speed_ctrl, 0, 0)

        self.irun_ctrl = QRunCurrentControl(self.config)
        self.grid.addWidget(self.irun_ctrl, 1, 0)

class QSpeedControl(QNumericControl):

    def __init__(self, config):

        self.config = config

        super().__init__(label="Speed", units="steps/s")
        self.extendUI()

    def extendUI(self):

        self.setMinimum(self.config["speed"]["min"])
        self.setMaximum(self.config["speed"]["max"])
        self.setMapper("log10")

        self.setValue(self.config["speed"]["default"])        

        self.hbox2 = QHBoxLayout()
        self.vbox.addLayout(self.hbox2, 1)

        for speed in self.config["steps"]["predef"]:
            speed_pb = QPushButton(f"{speed}")
            self.hbox2.addWidget(speed_pb)
            speed_pb.clicked.connect(self.on_pb_click)

    def on_pb_click(self):

        speed = float(self.sender().text())
        self.setValue(speed)

class QRunCurrentControl(QNumericControl):

    def __init__(self, config):

        self.config = config

        super().__init__(label="Run current", units="")
        self.extendUI()

    def extendUI(self):

        self.setMinimum(self.config["irun"]["min"])
        self.setMaximum(self.config["irun"]["max"])

        self.setValue(self.config["irun"]["default"])
        self.setSingleStep(self.config["irun"]["step"])     

        self.set_pb = QPushButton("Set")
        self.set_pb.setDisabled(True)
        self.hbox1.addWidget(self.set_pb)

        self.valueChanged.connect(lambda: self.set_pb.setDisabled(False))
        self.set_pb.clicked.connect(lambda: self.set_pb.setDisabled(True))