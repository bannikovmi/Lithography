from PyQt5.QtCore import Qt, QTime
from PyQt5.QtWidgets import (
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget
    )

# local imports
from stage.drives.API.drive import QDrive
from widgets.numeric import QNumericIndicator

from .params import QDriveParams
from .move_button import QMoveButton

class QPlaneGB(QGroupBox):

    def __init__(self, config, resource_manager):

        # Save arguments to instance attributes
        self.config = config
        self.rm = resource_manager

        super().__init__("Lateral positioning")

        self.rm.update_resource("DRX", QDrive)
        self.rm.update_resource("DRY", QDrive)
        self.x_drive = self.rm["DRX"]
        self.y_drive = self.rm["DRY"]

        self.initUI()
        self.connect_signals()
        self.init_values()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.x_params = QDriveParams(self.config["x_params"])
        self.y_params = QDriveParams(self.config["y_params"])
        self.positioner = QPositionerWidget(self.config["positioner"])

        self.grid.addWidget(self.y_params, 0, 1)
        self.grid.addWidget(self.x_params, 1, 1)
        self.grid.addWidget(self.positioner, 0, 0, 2, 1)

    def connect_signals(self):

        # Disable pos button if at max and neg button if at min for x-direction
        self.x_drive.max_checked.connect(
            self.positioner.arrow_button_group.x_pos_pb.setDisabled)
        self.x_drive.min_checked.connect(
            self.positioner.arrow_button_group.x_neg_pb.setDisabled)

        # Disable pos button if at max and neg button if at min for y-direction
        self.y_drive.max_checked.connect(
            self.positioner.arrow_button_group.y_pos_pb.setDisabled)
        self.y_drive.min_checked.connect(
            self.positioner.arrow_button_group.y_neg_pb.setDisabled)

        # Disable/enable interface after movement start/finish
        self.x_drive.movement_status.connect(self.x_disable_interface)
        self.y_drive.movement_status.connect(self.y_disable_interface)
        # Clear eta lineedit upon movement finish
        self.x_drive.movement_status.connect(lambda state:
            self.positioner.x_eta_le.setText("") if state is False else None)
        self.y_drive.movement_status.connect(lambda state:
            self.positioner.y_eta_le.setText("") if state is False else None)

        # Power control
        self.x_params.power_cb.clicked.connect(self.x_on_power_toggle)
        self.y_params.power_cb.clicked.connect(self.y_on_power_toggle)

        # Start movement on button click
        self.positioner.arrow_button_group.x_neg_pb.clicked.connect(lambda:
            self.x_on_movement_start(sign=-self.config["x_params"]["pos_direction"]))
        self.positioner.arrow_button_group.x_pos_pb.clicked.connect(lambda:
            self.x_on_movement_start(sign=+self.config["x_params"]["pos_direction"]))
        self.positioner.arrow_button_group.y_neg_pb.clicked.connect(lambda:
            self.y_on_movement_start(sign=-self.config["y_params"]["pos_direction"]))
        self.positioner.arrow_button_group.y_pos_pb.clicked.connect(lambda:
            self.y_on_movement_start(sign=+self.config["y_params"]["pos_direction"]))

        # Abort movement on button click
        self.positioner.x_abort_pb.clicked.connect(self.x_drive.abort_movement)
        self.positioner.y_abort_pb.clicked.connect(self.y_drive.abort_movement)

        # Change IRun on set button click
        self.x_params.drive_settings.irun_ctrl.set_pb.clicked.connect(
            lambda: self.x_drive.set("irun",
                int(self.x_params.drive_settings.irun_ctrl.value())))
        self.y_params.drive_settings.irun_ctrl.set_pb.clicked.connect(
            lambda: self.y_drive.set("irun",
                int(self.y_params.drive_settings.irun_ctrl.value())))

    def init_values(self):

        # Power off
        self.x_on_power_toggle()
        self.y_on_power_toggle()

        # Set run currents
        self.x_params.drive_settings.irun_ctrl.set_pb.clicked.emit()
        self.y_params.drive_settings.irun_ctrl.set_pb.clicked.emit()

    def x_disable_interface(self, state):

        self.positioner.arrow_button_group.setDisabled(state)
        self.positioner.x_abort_pb.setDisabled(not state)
        self.x_params.power_cb.setDisabled(state)

    def y_disable_interface(self, state):

        self.positioner.arrow_button_group.setDisabled(state)
        self.positioner.y_abort_pb.setDisabled(not state)
        self.y_params.power_cb.setDisabled(state)

    def x_on_power_toggle(self):

        self.x_drive.request("max")
        self.x_drive.request("min")

        if self.x_params.power_cb.isChecked():
            self.x_drive.set("power", 1)
        else:
            self.x_drive.set("power", 0)

    def y_on_power_toggle(self):

        self.y_drive.request("max")
        self.y_drive.request("min")

        if self.y_params.power_cb.isChecked():
            self.y_drive.set("power", 1)
        else:
            self.y_drive.set("power", 0)

    def x_on_movement_start(self, sign):

        speed = int(self.x_params.drive_settings.speed_ctrl.value())
        nsteps = int(sign*self.x_params.steps_ctrl.value())

        # Set speed and mstep
        self.x_drive.set("speed", speed)
        self.x_drive.set("mstep", int(self.x_params.divider_cmb.currentText()))
        
        self.x_finish_time = QTime.currentTime().addMSecs(int(1e3*abs(nsteps)/speed))
        self.x_drive.start_movement(nsteps)
        self.x_drive.timer.timeout.connect(lambda:
            self.positioner.x_eta_le.setText(
                f"{QTime.currentTime().msecsTo(self.x_finish_time)/1e3:.1f}"))

    def y_on_movement_start(self, sign):

        speed = int(self.y_params.drive_settings.speed_ctrl.value())
        nsteps = int(sign*self.y_params.steps_ctrl.value())

        # Set speed and mstep
        self.y_drive.set("speed", speed)
        self.y_drive.set("mstep", int(self.y_params.divider_cmb.currentText()))
        
        self.y_finish_time = QTime.currentTime().addMSecs(int(1e3*abs(nsteps)/speed))
        self.y_drive.start_movement(nsteps)
        self.y_drive.timer.timeout.connect(lambda:
            self.positioner.y_eta_le.setText(
                f"{QTime.currentTime().msecsTo(self.y_finish_time)/1e3:.1f}"))

class QArrowButtonGroup(QWidget):

    def __init__(self, config):

        self.config = config

        super().__init__()
        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.x_neg_pb = QMoveButton("left")
        self.x_pos_pb = QMoveButton("right")
        self.y_neg_pb = QMoveButton("down")
        self.y_pos_pb = QMoveButton("up")

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.y_pos_pb, 0, alignment=Qt.AlignHCenter)
        
        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox, 1)
        self.vbox.addStretch(1)

        self.hbox.addStretch(1)
        self.hbox.addWidget(self.x_neg_pb, 0)
        self.hbox.addWidget(self.y_neg_pb, 1)
        self.hbox.addWidget(self.x_pos_pb, 2)
        self.hbox.addStretch(1)

class QPositionerWidget(QGroupBox):

    def __init__(self, config):

        self.config = config

        super().__init__("Movement")
        self.initUI()

    def initUI(self):

        self.setStyleSheet("background-color: white;")

        self.hbox = QHBoxLayout()
        self.setLayout(self.hbox)

        self.hbox.addStretch(1)
        self.vbox = QVBoxLayout()
        self.hbox.addLayout(self.vbox)
        
        self.arrow_button_group = QArrowButtonGroup(self.config)
        self.vbox.addWidget(self.arrow_button_group, alignment=Qt.AlignHCenter)
        self.vbox.addStretch(1)

        self.hbox2 = QHBoxLayout()
        self.vbox.addLayout(self.hbox2)

        self.hbox2.addStretch(1)
        self.x_eta_lab = QLabel("X axis ETA [s]")
        self.x_eta_le = QLineEdit()
        self.x_eta_le.setReadOnly(True)
        self.x_abort_pb = QPushButton("Abort x")
        self.x_abort_pb.setDisabled(True)
        
        self.hbox2.addWidget(self.x_eta_lab)
        self.hbox2.addWidget(self.x_eta_le)
        self.hbox2.addWidget(self.x_abort_pb)
        self.hbox2.addStretch(1)

        self.hbox3 = QHBoxLayout()
        self.vbox.addLayout(self.hbox3)

        self.hbox3.addStretch(1)
        self.y_eta_lab = QLabel("X axis ETA [s]")
        self.y_eta_le = QLineEdit()
        self.y_eta_le.setReadOnly(True)
        self.y_abort_pb = QPushButton("Abort y")
        self.y_abort_pb.setDisabled(True)
        self.hbox3.addWidget(self.y_abort_pb)
        
        self.hbox3.addWidget(self.y_eta_lab)
        self.hbox3.addWidget(self.y_eta_le)
        self.hbox3.addWidget(self.y_abort_pb)
        self.hbox3.addStretch(1)

        self.hbox.addStretch(1)

        # self.x_indicator = QNumericIndicator(
        #     label="X pos",
        #     min_value=self.config["Drives"]["DRX"]["min_position"],
        #     max_value=self.config["Drives"]["DRX"]["max_position"],
        #     orientation=Qt.Horizontal
        # )
        # self.y_indicator = QNumericIndicator(
        #     label="Y pos",
        #     min_value=self.config["Drives"]["DRY"]["min_position"],
        #     max_value=self.config["Drives"]["DRY"]["max_position"],
        #     orientation=Qt.Vertical
        # )
        # self.grid.addWidget(self.x_indicator, 1, 0)
        # self.grid.addWidget(self.y_indicator, 0, 1)
