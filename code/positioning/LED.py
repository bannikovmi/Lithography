# pyqt-related imports
from PyQt5.QtCore import pyqtSignal, QTimer, QTime
from PyQt5.QtWidgets import (
    QGroupBox,
    QLabel,
    QLineEdit,
    QGridLayout,
    QPushButton,
    QRadioButton,
    QSpinBox,
    )

class QLEDWidget(QGroupBox):

    def __init__(self, config, ESP, name, label):

        super().__init__(label)
        self.name = name
        self.config = config
        self.ESP = ESP
        
        self.initUI()
        self.emission_on = False
        self.ESP.write(f"{self.name}_DUT_{0}") # turn off the lighting

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        # Frequency
        self.freq_lab = QLabel("Frequency [Hz]")
        self.freq_sb = QSpinBox()
        self.freq_pb = QPushButton("Set")
        self.freq_sb.setMinimum(self.config[self.name]["min_freq"])
        self.freq_sb.setMaximum(self.config[self.name]["max_freq"])
        self.freq_sb.setValue(self.config[self.name]["init_freq"])
        self.freq_pb.clicked.connect(self.set_freq)

        self.grid.addWidget(self.freq_lab, 0, 0)
        self.grid.addWidget(self.freq_sb, 0, 1)
        self.grid.addWidget(self.freq_pb, 0, 2, 1, 2)

        # Mode
        self.continious_rb = QRadioButton("Continious")
        self.single_rb = QRadioButton("Single")
        self.continious_rb.setChecked(True)
        self.continious_rb.clicked.connect(self.toggle_mode)
        self.single_rb.clicked.connect(self.toggle_mode)
        self.start_pb = QPushButton("Turn on")
        self.start_pb.clicked.connect(self.on_emission_start)
        
        self.grid.addWidget(self.continious_rb, 1, 0)
        self.grid.addWidget(self.single_rb, 1, 1)
        self.grid.addWidget(self.start_pb, 1, 2, 1, 2)

        # Duty
        self.duty_lab = QLabel("Duty")
        self.duty_sb = QSpinBox()
        self.duty_sb.setMinimum(self.config[self.name]["min_duty"])
        self.duty_sb.setMaximum(self.config[self.name]["max_duty"])
        self.duty_sb.setValue(self.config[self.name]["init_duty"])
        self.duty_pb = QPushButton("Set")
        self.duty_pb.clicked.connect(self.set_duty)

        self.grid.addWidget(self.duty_lab, 2, 0)
        self.grid.addWidget(self.duty_sb, 2, 1)
        self.grid.addWidget(self.duty_pb, 2, 2, 1, 2)

        # Timer
        self.timer_label = QLabel("Timer [ms]")
        self.timer_sb = QSpinBox()
        self.timer_sb.setMinimum(self.config[self.name]["min_timer"])
        self.timer_sb.setMaximum(self.config[self.name]["max_timer"])
        self.timer_sb.setValue(self.config[self.name]["init_timer"])

        self.eta_label = QLabel("Time left [ms]")
        self.eta_le = QLineEdit()
        self.eta_le.setReadOnly(True)
        
        self.grid.addWidget(self.timer_label, 3, 0)
        self.grid.addWidget(self.timer_sb, 3, 1)
        self.grid.addWidget(self.eta_label, 3, 2)
        self.grid.addWidget(self.eta_le, 3, 3)

    def update_UI(self, resource_name, command_name, arguments):

        pass

    def set_freq(self):

        value = self.freq_sb.value()
        self.ESP.write(f"{self.name}_FRQ_{value}")

    def set_duty(self):

        value = self.duty_sb.value()
        if self.emission_on:
            self.ESP.write(f"{self.name}_DUT_{value}")

    def toggle_mode(self):

        if self.continious_rb.isChecked():
            self.start_pb.setText("Turn on")
        else:
            self.start_pb.setText("Start")

    def disable_interface(self, state):

        self.continious_rb.setDisabled(state)
        self.single_rb.setDisabled(state)
        self.timer_sb.setDisabled(state)

    def on_emission_start(self):

        self.emission_on = True
        self.disable_interface(True)

        self.start_pb.clicked.disconnect()
        self.start_pb.clicked.connect(self.on_emission_finish)

        if self.continious_rb.isChecked():
            
            self.start_pb.setText("Turn off")
            self.ESP.write(f"{self.name}_DUT_{self.duty_sb.value()}")

        else:
            
            self.start_pb.setText("Abort")

            self.stop_timer = QTimer()
            self.stop_timer.setInterval(self.timer_sb.value())
            self.stop_timer.setSingleShot(True)
            self.stop_timer.timeout.connect(self.on_emission_finish)

            self.eta_le.setText(f"{self.timer_sb.value()}")
            self.eta_timer = QTimer()
            self.eta_timer.setInterval(self.config[self.name]["eta_update_interval"])
            
            self.finish_time = QTime.currentTime().addMSecs(self.timer_sb.value())
            self.eta_timer.timeout.connect(lambda:
                self.eta_le.setText(f"{QTime.currentTime().msecsTo(self.finish_time)}"))

            self.ESP.write(f"{self.name}_DUT_{self.duty_sb.value()}")
            self.stop_timer.start()
            self.eta_timer.start()

    def on_emission_finish(self):

        self.ESP.write(f"{self.name}_DUT_0")
        
        if self.continious_rb.isChecked():
            
            self.start_pb.setText("Turn on")

        else:
            
            self.start_pb.setText("Start")
            self.stop_timer.stop()
            self.eta_timer.stop()

            self.eta_le.setText("")

        self.disable_interface(False)
        self.start_pb.clicked.disconnect()
        self.start_pb.clicked.connect(self.on_emission_start)

class QTimedOnGB(QGroupBox):

    emission_started = pyqtSignal()
    emission_finished = pyqtSignal()
    duty_updated = pyqtSignal(int)

    def __init__(self, config, ESP, name, label="Emission"):

        super().__init__(label)
        self.config = config
        self.ESP = ESP
        self.name = name
        self.initUI()

    def initUI(self):
        
        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)
        
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.vbox.addLayout(self.hbox1, 0)
        self.vbox.addLayout(self.hbox2, 1)

        self.duty_label = QLabel("Duty")


        self.timer_label = QLabel("Timer [ms]")
        self.timer_sb = QSpinBox()
        self.timer_sb.setMinimum(self.config[self.name]["min_timer"])
        self.timer_sb.setMaximum(self.config[self.name]["max_timer"])

        self.start_pb = QPushButton("Start")
        self.eta_label = QLabel("Time left [ms]")
        self.eta_le = QLineEdit()
        self.eta_le.setReadOnly(True)

        self.hbox1.addWidget(self.duty_label, 0)
        self.hbox1.addWidget(self.duty_sb, 1)
        self.hbox1.addWidget(self.timer_label, 2)
        self.hbox1.addWidget(self.timer_sb, 3)
        
        self.hbox1.addWidget(self.start_pb, 0)
        self.hbox2.addWidget(self.eta_label, 1)
        self.hbox2.addWidget(self.eta_le, 2)

        self.start_pb.clicked.connect(self.on_emission_start)

    
