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

from .numeric import QNumericControl

class QDriveParams(QGroupBox):

    def __init__(self, config, name):

        self.config = config
        self.name = name

        super().__init__(self.config["Drives"][name]["label"])

        self.initUI()
        self.connect_signals()

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

        for div in self.config["Drives"]["step_dividers"]:
            self.divider_cmb.addItem(str(div))
        
        self.hbox.setStretch(0, 0)
        self.hbox.setStretch(1, 0)
        self.hbox.setStretch(2, 0)
        self.hbox.addStretch(1)

        self.steps_ctrl = QStepsControl(self.config, self.name)
        self.grid.addWidget(self.steps_ctrl, 1, 0)

        # Set widget params
        self.settings_menu = QMenu()
        self.settings_pb.setMenu(self.settings_menu)

        self.settings_qwa = QWidgetAction(self.settings_menu)
        self.drive_settings = QDriveSettings(self.config, self.name)
        self.settings_qwa.setDefaultWidget(self.drive_settings)
        self.settings_menu.addAction(self.settings_qwa)

    def connect_signals(self):
        pass

class QStepsControl(QNumericControl):

    def __init__(self, config, name):

        self.config = config
        self.name = name

        super().__init__(label="Steps", units="")
        self.extendUI()

    def extendUI(self):

        min_steps = self.config["Drives"][self.name]["min_steps"]
        max_steps = self.config["Drives"][self.name]["max_steps"]

        self.setMinimum(min_steps)
        self.setMaximum(max_steps)
        self.setMapper("log10")

        init_steps = self.config["Drives"][self.name]["init_steps"]
        self.setValue(init_steps)

        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.vbox.addLayout(self.hbox2, 1)
        self.vbox.addLayout(self.hbox3, 2)

        for ind, step in enumerate(self.config["Drives"][self.name]["predef_steps"]):
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

    def __init__(self, config, name):

        self.config = config
        self.name = name

        super().__init__()
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.speed_ctrl = QSpeedControl(self.config, self.name)
        self.grid.addWidget(self.speed_ctrl, 0, 0)

class QSpeedControl(QNumericControl):

    def __init__(self, config, name):

        self.config = config
        self.name = name

        super().__init__(label="Speed", units="steps/s")
        self.extendUI()

    def extendUI(self):

        min_speed = self.config["Drives"][self.name]["min_speed"]
        max_speed = self.config["Drives"][self.name]["max_speed"]
        self.setMinimum(min_speed)
        self.setMaximum(max_speed)
        self.setMapper("log10")

        init_speed = self.config["Drives"][self.name]["init_speed"]
        self.setValue(init_speed)        

        self.hbox2 = QHBoxLayout()
        self.vbox.addLayout(self.hbox2, 1)

        for speed in self.config["Drives"][self.name]["predef_speeds"]:
            speed_pb = QPushButton(f"{speed}")
            self.hbox2.addWidget(speed_pb)
            speed_pb.clicked.connect(self.on_pb_click)

    def on_pb_click(self):

        speed = float(self.sender().text())
        self.setValue(speed)