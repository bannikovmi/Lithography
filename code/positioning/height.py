# standard library imports
import sys, os

# pyqt-related imports
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QCheckBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QRadioButton, QSpinBox)
import pyqtgraph as pg

# local imports
sys.path.insert(0, os.path.abspath('..')) # enable import from sibling packages
from gui.numeric import QNumericControl
from gui.led import QRectangularLedIndicator

from .move_button import QMoveButton

class QZMotionWidget(QGroupBox):

    def __init__(self, config, ESP, label="Z axis motion"):

        super().__init__(label)
        self.config = config
        self.ESP = ESP
        self.initUI()
        self.z_power_toggle()
        self.is_moving = False

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.arrow_button_group = QHeightArrowButtonGroup(self.config)
        self.grid.addWidget(self.arrow_button_group, 0, 0, 2, 1)

        self.mode_gb = QGroupBox("Mode")
        self.mode_grid = QGridLayout()
        self.mode_gb.setLayout(self.mode_grid)

        self.single_rb = QRadioButton("single-step")
        self.continious_rb = QRadioButton("continious")
        self.mode_grid.addWidget(self.single_rb, 0, 0)
        self.mode_grid.addWidget(self.continious_rb, 0, 1)

        # self.single_rb.clicked.connect(self.toggle_mode)
        # self.continious_rb.clicked.connect(self.toggle_mode)

        self.grid.addWidget(self.mode_gb, 2, 0, 1, 2)

        self.speed_control = QNumericControl(label="Speed", units="steps/s",
            mapper_type="linear", orientation=Qt.Horizontal)
        self.speed_control.setMinimum(1)
        self.speed_control.setMaximum(5000)
        self.speed_control.setMapper("log10")
        self.grid.addWidget(self.speed_control, 0, 1)

        self.step_control = QNumericControl(label="Step", units="steps",
            mapper_type="linear", orientation=Qt.Horizontal)
        self.step_control.setMinimum(1)
        self.step_control.setMaximum(1000000)
        self.step_control.setMapper("log10")
        self.grid.addWidget(self.step_control, 1, 1)

        self.single_rb.setChecked(True)
        self.mode_gb.setDisabled(True)
        # self.continious_rb.setChecked(True)
        # self.step_control.setDisabled(True)
        # self.toggle_mode()

        self.arrow_button_group.up_pb.clicked.connect(self.move_up)
        self.arrow_button_group.down_pb.clicked.connect(self.move_down)

        self.z_power_cb = QCheckBox("Power")
        self.z_power_cb.setChecked(False)
        self.z_power_cb.clicked.connect(self.z_power_toggle)
        self.grid.addWidget(self.z_power_cb, 3, 0)

        self.abort_pb = QPushButton("Abort movement")
        self.abort_pb.setDisabled(True)
        self.abort_pb.clicked.connect(self.on_abort)
        self.grid.addWidget(self.abort_pb, 3, 1)

    # def toggle_mode(self):

    #     if self.continious_rb.isChecked():
    #         self.speed_control.setDisabled()
    #         self.step_control.setDisabled(True)
    #         self.arrow_button_group.setMode("continious")
    #     else:
    #         self.speed_control.setDisabled(True)
    #         self.step_control.setDisabled(False)
    #         self.arrow_button_group.setMode("single")

    def z_power_toggle(self):

        if self.z_power_cb.isChecked():
            self.ESP.write("DRZ_POW_1")
            self.arrow_button_group.up_pb.setDisabled(False)
            self.arrow_button_group.down_pb.setDisabled(False)
        else:
            self.ESP.write("DRZ_POW_0")
            self.arrow_button_group.up_pb.setDisabled(True)
            self.arrow_button_group.down_pb.setDisabled(True)

        self.ESP.write("DRZ_MAX")
        self.ESP.write("DRZ_MIN")

    def move_down(self):

        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(lambda: self.ESP.write("DRZ_MAX"))
        self.timer.start()

        self.abort_pb.setDisabled(False)
        self.arrow_button_group.setDisabled(True)
        self.z_power_cb.setDisabled(True)

        nsteps = int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRZ_SPD_{speed}")
        self.ESP.write(f"DRZ_MOV_{nsteps}")

        self.is_moving = True

    def move_up(self):

        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(lambda: self.ESP.write("DRZ_MIN"))
        self.timer.start()

        self.abort_pb.setDisabled(False)
        self.arrow_button_group.setDisabled(True)
        self.z_power_cb.setDisabled(True)

        nsteps = -int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRZ_SPD_{speed}")
        self.ESP.write(f"DRZ_MOV_{nsteps}")

        self.is_moving = True

    def on_abort(self):

        self.ESP.write("DRZ_MOV_ABT")
        self.on_finish()

    def on_finish(self):

        self.abort_pb.setDisabled(True)
        self.arrow_button_group.setDisabled(False)
        self.z_power_cb.setDisabled(False)

        self.ESP.write("DRZ_MAX")
        self.ESP.write("DRZ_MIN")
        self.timer.stop()
        self.is_moving = False
        
    def update_UI(self, resource_name, command, arguments):

        try:
            if command == "MAX":
                state = int(arguments[0])
                if self.is_moving and state:
                    self.on_abort()
                self.arrow_button_group.down_led.setChecked(state)
                self.arrow_button_group.down_pb.setDisabled(state)
            elif command == "MIN":
                state = int(arguments[0])
                if self.is_moving and state:
                    self.on_abort()
                self.arrow_button_group.up_led.setChecked(state)
                self.arrow_button_group.up_pb.setDisabled(state)
            elif command == "MOV":
                if arguments[0] == "FIN":
                    self.on_finish()
        except IndexError:
            pass

class QHeightArrowButtonGroup(QGroupBox):

    def __init__(self, config, label=None):

        self.config = config
        self.mode = "continious"

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.down_pb = QMoveButton("down")
        self.up_pb = QMoveButton("up")

        self.grid.addWidget(self.down_pb, 2, 0)
        self.grid.addWidget(self.up_pb, 1, 0)

        self.down_led = QRectangularLedIndicator()
        self.up_led = QRectangularLedIndicator()

        self.grid.addWidget(self.down_led, 3, 0)
        self.grid.addWidget(self.up_led, 0, 0)

        self.down_led.setDisabled(True)
        self.up_led.setDisabled(True)

    def setMode(self, mode):

        match mode:
            case "continious":
                self.down_pb.setAutoRepeat(True)
                self.up_pb.setAutoRepeat(True)
            case "single":
                self.down_pb.setAutoRepeat(False)
                self.up_pb.setAutoRepeat(False)
            case _:
                raise ValueError("Unknown mode")
