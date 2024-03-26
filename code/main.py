#!/usr/bin/python

"""
This module contains a set of commands for communication with Thyracont VSP transducers
based on PyVISA library and custom data_packages module.

Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# standard library imports
import sys

# third party imports
import pyvisa

# pyqt-related imports
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QWidget

# local imports
from gui import QMotionStepperWidget
from motion import MotionMessage

# load configurations
import tomli
with open("config.toml", mode='rb') as config_file:
    config = tomli.load(config_file)

class MainWindow(QMainWindow):

    def __init__(self, config):
        
        super().__init__()

        self.config = config
        self.init_resources()
        self.initUI()

    def init_resources(self):

        self.rm = pyvisa.ResourceManager()

        # Setup ESP Wroom32 for motion control
        self.esp = self.rm.open_resource('ASRL4::INSTR')
        self.esp.baud_rate = 115200
        self.esp.write_termination = ' \n'
        self.esp.read_termination = '\n'
        self.esp.timeout = 1000

    def initUI(self):

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.grid = QGridLayout()
        self.main_widget.setLayout(self.grid)

        self.motion_stepper_widget = QMotionStepperWidget(self.config)
        self.grid.addWidget(self.motion_stepper_widget)
        self.motion_stepper_widget.execute_pb.clicked.connect(self.execute_motion)

        # Resize main window and set title
        self.setWindowTitle('Lithography')
        self.show()


    def execute_motion(self):

        # self.motion_stepper_widget.execute_pb.setDisabled(True)
        if self.motion_stepper_widget.clockwise_rb.isChecked():
            self.direction = 1
        else:
            self.direction = 0

        self.nsteps = self.motion_stepper_widget.nsteps_sb.value()
        self.delay = 1000
        
        # self.esp.write(MotionMessage(self.direction, self.nsteps, self.delay).to_serial_message())
        print(self.esp.read())

def main():

    app = QApplication(sys.argv)
    window = MainWindow(config)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
