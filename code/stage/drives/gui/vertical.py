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

from stage.drives.API.drive import QDrive
from widgets.numeric import QNumericIndicator

from .params import QDriveParams
from .move_button import QMoveButton

class QVerticalGB(QGroupBox):

    def __init__(self, config, resource_manager):

        # Save arguments to instance attributes
        self.config = config
        self.rm = resource_manager

        super().__init__("Vertical positioning")
            
        self.rm.update_resource("DRZ", QDrive)
        self.drive = self.rm["DRZ"]

        self.initUI()
        self.connect_signals()
        self.init_values()

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.params = QDriveParams(self.config["params"])
        self.positioner = QPositionerWidget(self.config["positioner"])
        
        self.grid.addWidget(self.positioner, 0, 0)
        self.grid.addWidget(self.params, 0, 1)

    def connect_signals(self):

        # Disable pos button if at max and neg button if at min
        self.drive.max_checked.connect(
            self.positioner.arrow_button_group.neg_pb.setDisabled)
        self.drive.min_checked.connect(
            self.positioner.arrow_button_group.pos_pb.setDisabled)

        # Disable/enable interface after movement start/finish
        self.drive.movement_status.connect(self.disable_interface)
        # Clear eta lineedit upon movement finish
        self.drive.movement_status.connect(lambda state:
            self.positioner.eta_le.setText("") if state is False else None)

        # Power control
        self.params.power_cb.clicked.connect(self.on_power_toggle)

        # Start movement on button click
        self.positioner.arrow_button_group.neg_pb.clicked.connect(lambda:
            self.on_movement_start(sign=-self.config["params"]["pos_direction"]))
        self.positioner.arrow_button_group.pos_pb.clicked.connect(lambda:
            self.on_movement_start(sign=+self.config["params"]["pos_direction"]))

        # Abort movement on button click
        self.positioner.abort_pb.clicked.connect(self.drive.abort_movement)

        # Change IRun on set button click
        self.params.drive_settings.irun_ctrl.set_pb.clicked.connect(
            lambda: self.drive.set("irun",
                int(self.params.drive_settings.irun_ctrl.value())))

    def init_values(self):

        # Power off
        self.on_power_toggle()

        # Set run current
        self.params.drive_settings.irun_ctrl.set_pb.clicked.emit()

    def disable_interface(self, state):

        self.positioner.arrow_button_group.setDisabled(state)
        self.positioner.abort_pb.setDisabled(not state)
        self.params.power_cb.setDisabled(state)

    def on_power_toggle(self):

        self.drive.request("max")
        self.drive.request("min")

        if self.params.power_cb.isChecked():
            self.drive.set("power", 1)
            self.positioner.arrow_button_group.setDisabled(False)
        else:
            self.drive.set("power", 0)
            self.positioner.arrow_button_group.setDisabled(True)

    def on_movement_start(self, sign):

        speed = int(self.params.drive_settings.speed_ctrl.value())
        nsteps = int(sign*self.params.steps_ctrl.value())

        # Set speed and mstep
        self.drive.set("speed", speed)
        self.drive.set("mstep", int(self.params.divider_cmb.currentText()))
        
        self.finish_time = QTime.currentTime().addMSecs(int(1e3*abs(nsteps)/speed))
        self.drive.start_movement(nsteps)
        self.drive.timer.timeout.connect(lambda:
            self.positioner.eta_le.setText(
                f"{QTime.currentTime().msecsTo(self.finish_time)/1e3:.1f}"))

class QArrowButtonGroup(QWidget):

    def __init__(self, config):

        self.config = config

        super().__init__()
        self.initUI()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.neg_pb = QMoveButton("down")
        self.pos_pb = QMoveButton("up")

        self.vbox.addStretch(1)
        self.vbox.addWidget(self.pos_pb, 0, alignment=Qt.AlignVCenter)
        self.vbox.addWidget(self.neg_pb, 1, alignment=Qt.AlignVCenter)
        self.vbox.addStretch(1)

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
        self.eta_lab = QLabel("ETA [s]")
        self.eta_le = QLineEdit()
        self.eta_le.setReadOnly(True)
        self.abort_pb = QPushButton("Abort")
        self.abort_pb.setDisabled(True)
        self.hbox2.addWidget(self.abort_pb)
        
        self.hbox2.addWidget(self.eta_lab)
        self.hbox2.addWidget(self.eta_le)
        self.hbox2.addWidget(self.abort_pb)
        self.hbox2.addStretch(1)

        self.hbox.addStretch(1)

        # self.indicator = QNumericIndicator(
        #     label="Z pos",
        #     min_value=self.config["Drives"]["DRZ"]["min_position"],
        #     max_value=self.config["Drives"]["DRZ"]["max_position"],
        #     orientation=Qt.Vertical
        # )
        # self.hbox.addWidget(self.indicator, 1)
