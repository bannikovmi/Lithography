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
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QTabWidget, QWidget

# local gui imports
from positioning.tab import QPositioningTab

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

        self.rm = pyvisa.ResourceManager("@py")

        # Setup ESP Wroom32 for motion control
        # self.ESP = self.rm.open_resource('ASRL4::INSTR')
        # self.ESP.baud_rate = 115200
        # self.ESP.write_termination = ' \n'
        # self.ESP.read_termination = '\n'
        # self.ESP.timeout = 1000
        self.ESP = None

    def initUI(self):

        # Create tab widgets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.positioning_tab = QPositioningTab(self.config, self.ESP)
        self.tabs.addTab(self.positioning_tab, "Positioning")

        # Resize main window and set title
        self.setWindowTitle('Lithography')
        self.show()

def main():

    app = QApplication(sys.argv)
    window = MainWindow(config)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
