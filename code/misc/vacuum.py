from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QGridLayout, QGroupBox, QLabel, QLineEdit, QPushButton

class QVacuumWidget(QGroupBox):

    state_changed = pyqtSignal(bool)

    def __init__(self, config, ESP, label="Vacuum pump"):

        self.config=config
        self.ESP = ESP
        self.state = False

        super().__init__(label)
        self.initUI()

    def initUI(self):
        
        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.vacuum_pb = QPushButton("Toggle")
        self.vacuum_label = QLabel("State")
        self.vacuum_le = QLineEdit()
        self.vacuum_le.setText("Off")
        self.vacuum_le.setReadOnly(True)

        self.grid.addWidget(self.vacuum_pb, 0, 0)
        self.grid.addWidget(self.vacuum_label, 0, 1)
        self.grid.addWidget(self.vacuum_le, 0, 2)

        self.vacuum_pb.clicked.connect(lambda state: self.on_toggle())

    def on_toggle(self):
        
        if self.state:
            self.turn_off()
        else:
            self.turn_on()

    def turn_on(self):
        
        self.state = True
        self.vacuum_le.setText("On")
        self.state_changed.emit(True)

    def turn_off(self):
        
        self.state = False
        self.vacuum_le.setText("Off")
        self.state_changed.emit(False)

