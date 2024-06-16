# standard library imports
import sys, os

# pyqt-related imports
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QCheckBox, QGridLayout, QGroupBox, QLabel,
    QLineEdit, QPushButton, QRadioButton, QShortcut, QSpinBox)
import pyqtgraph as pg

# local imports
sys.path.insert(0, os.path.abspath('..')) # enable import from sibling packages
from gui.led import QRectangularLedIndicator
from gui.numeric import QNumericControl

from .move_button import QMoveButton

class QPlanePositioningWidget(QGroupBox):

    def __init__(self, config, ESP, label="XY positioning"):

        self.config = config
        self.ESP = ESP

        super().__init__(label)
        self.initUI()

        self.x_power_toggle()
        self.y_power_toggle()        
        self.x_moving = False
        self.y_moving = False

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.arrow_button_group = QPlaneArrowButtonGroup(self.config)
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

        self.speed_control = QNumericControl(label="Speed", units="steps/s", mapper_type="linear")
        self.speed_control.setMinimum(1)
        self.speed_control.setMaximum(5000)
        self.speed_control.setMapper("log10")
        self.grid.addWidget(self.speed_control, 0, 1)

        self.step_control = QNumericControl(label="Step", units="steps", mapper_type="linear")
        self.step_control.setMinimum(1)
        self.step_control.setMaximum(1000000)
        self.step_control.setMapper("log10")
        self.grid.addWidget(self.step_control, 1, 1)

        #####################################
        self.single_rb.setChecked(True)
        self.continious_rb.setDisabled(True)
        self.single_rb.setDisabled(True)

        # self.speed_control.setDisabled(True)
        # self.toggle_mode()

        self.arrow_button_group.down_pb.pressed.connect(self.move_down)
        self.arrow_button_group.left_pb.clicked.connect(self.move_left)
        self.arrow_button_group.right_pb.clicked.connect(self.move_right)
        self.arrow_button_group.up_pb.clicked.connect(self.move_up)

        self.x_abort_pb = QPushButton("Abort X movement")
        self.x_abort_pb.setDisabled(True)
        self.x_abort_pb.clicked.connect(self.on_x_abort)
        self.grid.addWidget(self.x_abort_pb, 3, 0)

        self.y_abort_pb = QPushButton("Abort Y movement")
        self.y_abort_pb.setDisabled(True)
        self.y_abort_pb.clicked.connect(self.on_y_abort)
        self.grid.addWidget(self.y_abort_pb, 3, 1)

        self.x_power_cb = QCheckBox("X power")
        self.x_power_cb.setChecked(False)
        self.x_power_cb.clicked.connect(self.x_power_toggle)
        self.grid.addWidget(self.x_power_cb, 4, 0)

        self.y_power_cb = QCheckBox("Y power")
        self.y_power_cb.setChecked(False)
        self.y_power_cb.clicked.connect(self.y_power_toggle)
        self.grid.addWidget(self.y_power_cb, 4, 1)

    def x_power_toggle(self):

        if self.x_power_cb.isChecked():
            self.ESP.write("DRX_POW_1")
            self.arrow_button_group.left_pb.setDisabled(False)
            self.arrow_button_group.right_pb.setDisabled(False)
        else:
            self.ESP.write("DRX_POW_0")
            self.arrow_button_group.left_pb.setDisabled(True)
            self.arrow_button_group.right_pb.setDisabled(True)

        self.ESP.write("DRX_MAX")
        self.ESP.write("DRX_MIN")

    def y_power_toggle(self):

        if self.y_power_cb.isChecked():
            self.ESP.write("DRY_POW_1")
            self.arrow_button_group.up_pb.setDisabled(False)
            self.arrow_button_group.down_pb.setDisabled(False)
        else:
            self.ESP.write("DRY_POW_0")
            self.arrow_button_group.up_pb.setDisabled(True)
            self.arrow_button_group.down_pb.setDisabled(True)

        self.ESP.write("DRY_MAX")
        self.ESP.write("DRY_MIN")


    # def toggle_mode(self):

    #     if self.continious_rb.isChecked():
    #         self.speed_control.setDisabled(False)
    #         self.step_control.setDisabled(True)
    #         self.arrow_button_group.setMode("continious")
    #     else:
    #         self.speed_control.setDisabled(True)
    #         self.step_control.setDisabled(False)
    #         self.arrow_button_group.setMode("single")

    def move_down(self):
        
        self.y_timer = QTimer()
        self.y_timer.setInterval(500)
        self.y_timer.timeout.connect(lambda: self.ESP.write("DRY_MIN"))
        self.y_timer.start()

        self.y_abort_pb.setDisabled(False)
        self.y_power_cb.setDisabled(True)

        self.arrow_button_group.down_pb.setDisabled(True)
        self.arrow_button_group.up_pb.setDisabled(True)

        nsteps = -int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRY_SPD_{speed}")
        self.ESP.write(f"DRY_MOV_{nsteps}")

        self.y_moving = True

    def move_left(self):

        self.x_timer = QTimer()
        self.x_timer.setInterval(500)
        self.x_timer.timeout.connect(lambda: self.ESP.write("DRX_MIN"))
        self.x_timer.start()

        self.x_abort_pb.setDisabled(False)
        self.x_power_cb.setDisabled(True)

        self.arrow_button_group.left_pb.setDisabled(True)
        self.arrow_button_group.right_pb.setDisabled(True)

        nsteps = -int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRX_SPD_{speed}")
        self.ESP.write(f"DRX_MOV_{nsteps}")

        self.x_moving = True

    def move_right(self):
        
        self.x_timer = QTimer()
        self.x_timer.setInterval(500)
        self.x_timer.timeout.connect(lambda: self.ESP.write("DRX_MAX"))
        self.x_timer.start()

        self.x_abort_pb.setDisabled(False)
        self.x_power_cb.setDisabled(True)

        self.arrow_button_group.left_pb.setDisabled(True)
        self.arrow_button_group.right_pb.setDisabled(True)

        nsteps = int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRX_SPD_{speed}")
        self.ESP.write(f"DRX_MOV_{nsteps}")

        self.x_moving = True

    def move_up(self):
        
        self.y_timer = QTimer()
        self.y_timer.setInterval(500)
        self.y_timer.timeout.connect(lambda: self.ESP.write("DRY_MAX"))
        self.y_timer.start()

        self.y_abort_pb.setDisabled(False)
        self.y_power_cb.setDisabled(True)

        self.arrow_button_group.down_pb.setDisabled(True)
        self.arrow_button_group.up_pb.setDisabled(True)

        nsteps = int(self.step_control.value())
        speed = int(self.speed_control.value())
        self.ESP.write(f"DRY_SPD_{speed}")
        self.ESP.write(f"DRY_MOV_{nsteps}")

        self.y_moving = True

    def on_x_abort(self):

        self.ESP.write("DRX_MOV_ABT")
        self.on_x_finish()

    def on_x_finish(self):

        self.x_abort_pb.setDisabled(True)
        self.x_power_cb.setDisabled(False)
        self.arrow_button_group.left_pb.setDisabled(False)
        self.arrow_button_group.right_pb.setDisabled(False)

        self.x_moving = False
        self.ESP.write("DRX_MAX")
        self.ESP.write("DRX_MIN")
        self.x_timer.stop()

    def on_y_abort(self):

        self.ESP.write("DRY_MOV_ABT")
        self.on_y_finish()

    def on_y_finish(self):

        self.y_abort_pb.setDisabled(True)
        self.y_power_cb.setDisabled(False)
        self.arrow_button_group.up_pb.setDisabled(False)
        self.arrow_button_group.down_pb.setDisabled(False)

        self.y_moving = False
        self.ESP.write("DRY_MAX")
        self.ESP.write("DRY_MIN")
        self.y_timer.stop()
        
    def update_UI(self, resource_name, command, arguments):

        try:
            if resource_name == "DRX":
                if command == "MAX":
                    state = int(arguments[0])
                    if self.x_moving and state:
                        self.on_x_abort()
                    if not self.x_moving:
                        self.arrow_button_group.right_led.setChecked(state)
                        self.arrow_button_group.right_pb.setDisabled(state)
                elif command == "MIN":
                    state = int(arguments[0])
                    if self.x_moving and state:
                        self.on_x_abort()
                    if not self.x_moving:
                        self.arrow_button_group.left_led.setChecked(state)
                        self.arrow_button_group.left_pb.setDisabled(state)
                elif command == "MOV":
                    if arguments[0] == "FIN":
                        self.on_x_finish()
            else:
                if command == "MAX":
                    state = int(arguments[0])
                    if self.y_moving and state:
                        self.on_y_abort()
                    if not self.y_moving:
                        self.arrow_button_group.up_led.setChecked(state)
                        self.arrow_button_group.up_pb.setDisabled(state)
                elif command == "MIN":
                    state = int(arguments[0])
                    if self.y_moving and state:
                        self.on_y_abort()
                    if not self.y_moving:
                        self.arrow_button_group.down_led.setChecked(state)
                        self.arrow_button_group.down_pb.setDisabled(state)
                elif command == "MOV":
                    if arguments[0] == "FIN":
                        self.on_y_finish()
        except IndexError:
            pass

class QPlaneArrowButtonGroup(QGroupBox):

    def __init__(self, config, label=None):

        self.config = config
        self.mode = "continious"

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.down_pb = QMoveButton("down")
        self.left_pb = QMoveButton("left")
        self.right_pb = QMoveButton("right")
        self.up_pb = QMoveButton("up")

        self.grid.addWidget(self.down_pb, 2, 2)
        self.grid.addWidget(self.left_pb, 2, 1)
        self.grid.addWidget(self.right_pb, 2, 3)
        self.grid.addWidget(self.up_pb, 1, 2)

        self.down_led = QRectangularLedIndicator()
        self.left_led = QRectangularLedIndicator()
        self.right_led = QRectangularLedIndicator()
        self.up_led = QRectangularLedIndicator()

        self.grid.addWidget(self.down_led, 3, 2)
        self.grid.addWidget(self.left_led, 2, 0)
        self.grid.addWidget(self.right_led, 2, 4)
        self.grid.addWidget(self.up_led, 0, 2)

        self.down_led.setDisabled(True)
        self.left_led.setDisabled(True)
        self.right_led.setDisabled(True)
        self.up_led.setDisabled(True)

    def setMode(self, mode):

        match mode:
            case "continious":
                self.down_pb.setAutoRepeat(True)
                self.left_pb.setAutoRepeat(True)
                self.right_pb.setAutoRepeat(True)
                self.up_pb.setAutoRepeat(True)
            case "single":
                self.down_pb.setAutoRepeat(False)
                self.left_pb.setAutoRepeat(False)
                self.right_pb.setAutoRepeat(False)
                self.up_pb.setAutoRepeat(False)

                self.down_pb.setAutoRepeat(False)
                self.left_pb.setAutoRepeat(False)
                self.right_pb.setAutoRepeat(False)
                self.up_pb.setAutoRepeat(False)
            case _:
                raise ValueError("Unknown mode")


