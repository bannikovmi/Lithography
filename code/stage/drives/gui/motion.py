# standard library imports
import sys, os

# pyqt-related imports
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QCheckBox,
    QComboBox,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QSpinBox,
    )

# local imports
sys.path.insert(0, os.path.abspath('..')) # enable import from sibling packages
from gui.numeric import QNumericControl, QNumericIndicator
from gui.led import QRectangularLedIndicator

from .move_button import QMoveButton

def PyQt_orientation(orientation_label):

    if orientation_label == "Horizontal":
        return Qt.Horizontal
    else:
        return Qt.Vertical

class QMotionGB(QGroupBox):

    def __init__(self, config, esp, name):
        
        self.config = config
        self.esp = esp
        self.name = name
        
        self.orientation = PyQt_orientation(
            self.config["Drives"][name]["orientation"])
        
        super().__init__(self.config["Drives"][name]["label"])

        self.initUI()
        self.connect_signals()
        self.power_toggle()
        self.is_moving = False

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.move_params = QMoveParams(self.name, self.config)
        self.move_box = QMoveBox(self.name, self.config)

        if self.orientation == Qt.Horizontal:
            self.grid.addWidget(self.move_box, 0, 0)
            self.grid.addWidget(self.move_params, 1, 0)
        else:
            self.grid.addWidget(self.move_box, 0, 0)
            self.grid.addWidget(self.move_params, 0, 1)

    def connect_signals(self):

        self.move_box.arrow_button_group.pos_pb.clicked.connect(
            lambda: self.move(sign=+self.config["Drives"][self.name]["pos_direction"]))
        self.move_box.arrow_button_group.neg_pb.clicked.connect(
            lambda: self.move(sign=-self.config["Drives"][self.name]["pos_direction"]))

        self.move_params.power_cb.clicked.connect(self.power_toggle)
        self.move_box.abort_pb.clicked.connect(self.on_abort)

    def power_toggle(self):

        if self.move_params.power_cb.isChecked():
            self.esp.write(f"{self.name}_POW_1")
            self.move_box.arrow_button_group.pos_pb.setDisabled(False)
            self.move_box.arrow_button_group.neg_pb.setDisabled(False)
        else:
            self.esp.write(f"{self.name}_POW_0")
            self.move_box.arrow_button_group.pos_pb.setDisabled(True)
            self.move_box.arrow_button_group.neg_pb.setDisabled(True)

        # Check Max and min limit switchers
        self.esp.write(f"{self.name}_MAX")
        self.esp.write(f"{self.name}_MIN")

    def move(self, sign):

        self.timer = QTimer()
        self.timer.setInterval(
            self.config["Drives"][self.name]["limits_check_interval"])
        if sign > 0:
            self.timer.timeout.connect(lambda: self.esp.write(f"{self.name}_MAX"))
        else:
            self.timer.timeout.connect(lambda: self.esp.write(f"{self.name}_MIN"))
        self.timer.start()

        self.move_box.abort_pb.setDisabled(False)
        self.move_box.arrow_button_group.setDisabled(True)
        self.move_params.power_cb.setDisabled(True)

        nsteps = sign*int(self.move_params.steps_widget.value())
        speed = int(self.move_params.speed_widget.value())
        mstep = int(self.move_params.divider_cb.currentText())

        self.esp.write(f"{self.name}_MST_{mstep}")
        self.esp.write(f"{self.name}_SPD_{speed}")
        self.esp.write(f"{self.name}_MOV_{nsteps}")

        self.is_moving = True

    def on_abort(self):

        self.esp.write(f"{self.name}_MOV_ABT")
        self.on_finish()

    def on_finish(self):

        self.move_box.abort_pb.setDisabled(True)
        self.move_box.arrow_button_group.setDisabled(False)
        self.move_params.power_cb.setDisabled(False)

        self.esp.write(f"{self.name}_MAX")
        self.esp.write(f"{self.name}_MIN")
        self.timer.stop()
        self.is_moving = False
        
    def update_UI(self, resource_name, command, arguments):

        try:
            if command == "MAX":
                state = int(arguments[0])
                if self.is_moving and state:
                    self.on_abort()
                if self.config["Drives"][self.name]["pos_direction"] == +1:
                    self.move_box.arrow_button_group.pos_led.setChecked(state)
                    self.move_box.arrow_button_group.pos_pb.setDisabled(state)
                else:
                    self.move_box.arrow_button_group.neg_led.setChecked(state)
                    self.move_box.arrow_button_group.neg_pb.setDisabled(state)
            elif command == "MIN":
                state = int(arguments[0])
                if self.is_moving and state:
                    self.on_abort()
                if self.config["Drives"][self.name]["pos_direction"] == +1:
                    self.move_box.arrow_button_group.neg_led.setChecked(state)
                    self.move_box.arrow_button_group.neg_pb.setDisabled(state)
                else:
                    self.move_box.arrow_button_group.pos_led.setChecked(state)
                    self.move_box.arrow_button_group.pos_pb.setDisabled(state)
            elif command == "MOV":
                if arguments[0] == "FIN":
                    self.on_finish()
        except IndexError:
            pass

class QMoveParams(QGroupBox):

    def __init__(self, name, config):

        self.name = name
        self.config = config

        super().__init__("Parametres")
        self.initUI()
        self.connect_signals()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # GUI elements
        self.power_cb = QCheckBox("Power")
        self.settings_pb = QPushButton("UART settings")
        self.single_rb = QRadioButton("Single")
        self.continious_rb = QRadioButton("Continious")
        self.divider_label = QLabel("Step divider")
        self.divider_cb = QComboBox()
        self.speed_widget = QSpeedWidget(self.name, self.config)
        self.steps_widget = QStepsWidget(self.name, self.config)

        # Add widgets to layout
        self.grid.addWidget(self.power_cb, 0, 0)
        self.grid.addWidget(self.settings_pb, 0, 1)
        self.grid.addWidget(self.single_rb, 0, 2)
        self.grid.addWidget(self.continious_rb, 0, 3)
        self.grid.addWidget(self.divider_label, 0, 4)
        self.grid.addWidget(self.divider_cb, 0, 5)
        self.grid.addWidget(self.speed_widget, 1, 0, 1, 6)
        self.grid.addWidget(self.steps_widget, 2, 0, 1, 6)

        # Set widgets params
        for div in self.config["Drives"]["step_dividers"]:
            self.divider_cb.addItem(str(div))
        
        divider = float(self.divider_cb.currentText())
        self.speed_widget.divider = divider
        self.steps_widget.divider = divider

        self.single_rb.setChecked(True)
        self.single_rb.setDisabled(True)
        self.continious_rb.setDisabled(True)

    def connect_signals(self):

        self.divider_cb.currentTextChanged.connect(
            lambda txt: self.speed_widget.update_mult(float(txt)))
        self.divider_cb.currentTextChanged.connect(
            lambda txt: self.steps_widget.update_mult(float(txt)))

class QMoveBox(QGroupBox):

    def __init__(self, name, config):

        self.name = name
        self.config = config

        self.orientation = PyQt_orientation(
            self.config["Drives"][name]["orientation"])

        super().__init__("Movement")
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Create widgets
        self.arrow_button_group = QArrowButtonGroup(self.name, self.config)
        self.abort_pb = QPushButton("Abort")
        self.position_widget = QPositionWidget(self.name, self.config)

        # Add widgets to grid
        self.grid.addWidget(self.arrow_button_group, 0, 0)
        self.grid.addWidget(self.abort_pb, 1, 0)
        self.grid.addWidget(self.position_widget, 0, 1, 2, 1)

        # Set widgets params
        self.abort_pb.setDisabled(True)

class QArrowButtonGroup(QGroupBox):

    def __init__(self, name, config):

        self.name = name
        self.config = config
        self.orientation = PyQt_orientation(
            self.config["Drives"][name]["orientation"])

        super().__init__()
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.neg_led = QRectangularLedIndicator()
        self.pos_led = QRectangularLedIndicator()
        self.neg_led.setDisabled(True)
        self.pos_led.setDisabled(True)

        if self.orientation == Qt.Horizontal:

            self.neg_pb = QMoveButton("left")
            self.pos_pb = QMoveButton("right")
            self.grid.addWidget(self.neg_pb, 0, 1)
            self.grid.addWidget(self.pos_pb, 0, 2)

            self.grid.addWidget(self.neg_led, 0, 0)
            self.grid.addWidget(self.pos_led, 0, 3)

        else:

            self.neg_pb = QMoveButton("down")
            self.pos_pb = QMoveButton("up")
            self.grid.addWidget(self.neg_pb, 2, 0)
            self.grid.addWidget(self.pos_pb, 1, 0)

            self.grid.addWidget(self.neg_led, 3, 0)
            self.grid.addWidget(self.pos_led, 0, 0)

class QPositionWidget(QNumericIndicator):

    def __init__(self, name, config):

        self.name = name
        self.config = config
        self.orientation = PyQt_orientation(
            self.config["Drives"][name]["orientation"])

        min_value = self.config["Drives"][self.name]["min_position"]
        max_value = self.config["Drives"][self.name]["max_position"]

        super().__init__(label="Position", units="", fstring="d",
            min_value=min_value, max_value=max_value, orientation=self.orientation)

        self.setMinimum(min_value)
        self.setMaximum(max_value)

        self.lineedit.setMaximumWidth(50)

class QSpeedWidget(QNumericControl):

    def __init__(self, name, config):

        self.name = name
        self.config = config
        self.divider = 1

        super().__init__(label="Speed [steps/s]", units="", 
            mapper_type="square", orientation=Qt.Horizontal)

        self.times_label = QLabel("/div=")
        self.mult_le = QLineEdit()
        self.mult_le.setReadOnly(True)
        # self.mult_le.setMaximumWidth(50)

        self.setMinimum(self.config["Drives"][self.name]["min_speed"])
        self.setMaximum(self.config["Drives"][self.name]["max_speed"])
        self.spinbox.setDecimals(0)

        self.grid.addWidget(self.times_label, 0, self.grid.columnCount())
        self.grid.addWidget(self.mult_le, 0, self.grid.columnCount())

        self.setValue(self.config["Drives"][self.name]["init_speed"])
        self.update_mult(self.divider)

    def on_slider_change(self, val):
        
        self.spinbox.valueChanged.disconnect()
        spinbox_val = self.mapper.evaluate(val)
        self.spinbox.setValue(spinbox_val)
        self.mult_le.setText(f"{self.mapper.evaluate(val)/self.divider:.4f}")
        self.spinbox.valueChanged.connect(self.on_spinbox_change)

    def on_spinbox_change(self, val):
        
        self.slider.valueChanged.disconnect()
        self.slider.setValue(round(self.mapper.evaluate_inverse(val)))
        self.mult_le.setText(f"{self.mapper.evaluate(val)/self.divider:.4f}")
        self.slider.valueChanged.connect(self.on_slider_change)

    def update_mult(self, mult):
        
        self.divider = mult
        self.mult_le.setText(f"{self.value()/self.divider:.4f}")

class QStepsWidget(QNumericControl):

    def __init__(self, name, config):

        self.name = name
        self.config = config
        self.divider = 1

        super().__init__(label="Steps", units="", 
            mapper_type="square", orientation=Qt.Horizontal)

        self.times_label = QLabel("/div=")
        self.mult_le = QLineEdit()
        self.mult_le.setReadOnly(True)
        # self.mult_le.setMaximumWidth(50)

        self.setMinimum(self.config["Drives"][self.name]["min_steps"])
        self.setMaximum(self.config["Drives"][self.name]["max_steps"])
        self.spinbox.setDecimals(0)

        self.grid.addWidget(self.times_label, 0, self.grid.columnCount())
        self.grid.addWidget(self.mult_le, 0, self.grid.columnCount())

        self.setValue(self.config["Drives"][self.name]["init_steps"])
        self.update_mult(self.divider)

    def on_slider_change(self, val):
        
        self.spinbox.valueChanged.disconnect()
        spinbox_val = self.mapper.evaluate(val)
        self.spinbox.setValue(spinbox_val)
        self.mult_le.setText(f"{self.mapper.evaluate(val)/self.divider:.4f}")
        self.spinbox.valueChanged.connect(self.on_spinbox_change)

    def on_spinbox_change(self, val):
        
        self.slider.valueChanged.disconnect()
        self.slider.setValue(round(self.mapper.evaluate_inverse(val)))
        self.mult_le.setText(f"{self.mapper.evaluate(val)/self.divider:.4f}")
        self.slider.valueChanged.connect(self.on_slider_change)

    def update_mult(self, mult):
        
        self.divider = mult
        self.mult_le.setText(f"{self.value()/self.divider:.4f}")
