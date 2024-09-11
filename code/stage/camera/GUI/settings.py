from PyQt5.QtWidgets import (
    QCheckBox,
    QHBoxLayout,
    QPushButton,
    QVBoxLayout,
    QWidget
)

from widgets.numeric.control import QNumericControl

class QCameraSettings(QWidget):

    def __init__(self, config, cam):

        self.config = config
        self.cam = cam

        super().__init__()
        self.initUI()
        self.connect_signals()
        self.set_default_values()

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.restore_pb = QPushButton("Restore default values")
        self.vbox.addWidget(self.restore_pb)

        self.hbox = QHBoxLayout()
        self.vbox.addLayout(self.hbox)

        # Auto white balance
        self.auto_wb_cb = QCheckBox("Auto white balance")
        self.auto_wb_cb.setChecked(self.config["auto_wb"])
        self.hbox.addWidget(self.auto_wb_cb)

        # Auto-exposure
        self.auto_exp_cb = QCheckBox("Auto exposure")
        self.auto_exp_cb.setChecked(self.config["auto_exp"])
        self.hbox.addWidget(self.auto_exp_cb)

        self.param_controls = {}

        for key, val in self.config.items():
            
            if isinstance(val, dict):
            
                num_control = QNumericControl(val["label"])
                num_control.setMinimum(val["min"])
                num_control.setMaximum(val["max"])
                num_control.setSingleStep(val["step"])
                num_control.setDecimals(0)
            
                self.vbox.addWidget(num_control)
                self.param_controls[key] = num_control

    def connect_signals(self):

        self.auto_exp_cb.clicked.connect(self.on_auto_exp)
        self.auto_wb_cb.clicked.connect(self.on_auto_wb)
        for key, ctrl in self.param_controls.items():
            # Note the use of named argument key=key inside lambda function. For more info see
            # https://www.pythonguis.com/tutorials/transmitting-extra-data-qt-signals
            ctrl.valueChanged.connect(lambda val, key=key: self.cam.set(key, val))
        self.restore_pb.clicked.connect(self.set_default_values)

    def set_default_values(self):

        self.auto_exp_cb.setChecked(self.config["auto_exp"])
        self.auto_wb_cb.setChecked(self.config["auto_wb"])
        self.on_auto_exp()
        self.on_auto_wb()

        for key, ctrl in self.param_controls.items():
            ctrl.setValue(self.config[key]["default"])

    def on_auto_exp(self):

        if self.auto_exp_cb.isChecked():
            self.param_controls["exposure"].setDisabled(True)
            self.cam.auto_exp = True
        else:
            self.param_controls["exposure"].setDisabled(False)
            self.cam.auto_exp = False
            self.cam.exposure = self.param_controls["exposure"].value()

    def on_auto_wb(self):

        if self.auto_wb_cb.isChecked():
            self.param_controls["wb_temp"].setDisabled(True)
            self.cam.auto_wb = True
        else:
            self.param_controls["wb_temp"].setDisabled(False)
            self.cam.auto_wb = False
            self.cam.wb_temp = self.param_controls["wb_temp"].value()
