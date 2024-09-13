from PyQt5.QtWidgets import (
	QGroupBox, 
	QHBoxLayout,
	QLabel,
	QSpinBox
)

class QVarScannerGB(QGroupBox):

	def __init__(self, config):

		self.config = config
		self.name = self.config["name"]

		super().__init__(self.name)

		self.initUI()
		self.set_borders()
		self.connect_signals()
		self.set_default_values()

	def initUI(self):

		self.hbox = QHBoxLayout()
		self.setLayout(self.hbox)

		self.start_lab = QLabel(f"{self.name} start")
		self.stop_lab = QLabel(f"{self.name} stop")
		self.step_lab = QLabel(f"{self.name} step")

		self.start_sb = QSpinBox()
		self.stop_sb = QSpinBox()
		self.step_sb = QSpinBox()

		self.hbox.addWidget(self.start_lab)
		self.hbox.addWidget(self.start_sb)
		self.hbox.addWidget(self.stop_lab)
		self.hbox.addWidget(self.stop_sb)
		self.hbox.addWidget(self.step_lab)
		self.hbox.addWidget(self.step_sb)
		self.hbox.addStretch(1)

	def set_borders(self):

		self.start_sb.setMinimum(self.config["start"]["min"])
		self.start_sb.setMaximum(self.config["start"]["max"])
		self.start_sb.setSingleStep(self.config["start"]["step"])

		self.stop_sb.setMinimum(self.config["stop"]["min"])
		self.stop_sb.setMaximum(self.config["stop"]["max"])
		self.stop_sb.setSingleStep(self.config["stop"]["step"])

		self.step_sb.setMinimum(self.config["step"]["min"])
		self.step_sb.setMaximum(self.config["step"]["max"])
		self.step_sb.setSingleStep(self.config["step"]["step"])

	def connect_signals(self):

		self.start_sb.valueChanged.connect(self.on_start_change)
		self.stop_sb.valueChanged.connect(self.on_stop_change)

	def set_default_values(self):

		self.start_sb.setValue(self.config["start"]["default"])
		self.stop_sb.setValue(self.config["stop"]["default"])
		self.step_sb.setValue(self.config["step"]["default"])

	def on_start_change(self, val):

		self.stop_sb.setMinimum(val+1)
		self.step_sb.setMaximum(self.stop_sb.value() - val)

	def on_stop_change(self, val):

		self.start_sb.setMaximum(val-1)
		self.step_sb.setMaximum(val - self.start_sb.value())

	def get_params(self):

		ret = {
			"start": self.start_sb.value(),
			"stop": self.stop_sb.value(),
			"step": self.step_sb.value()
		}

		return ret

	def get_fname(self):

		pars = self.get_params()
		return "%s_%s_%s" % (pars["start"], pars["stop"], pars["step"])
