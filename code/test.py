#!/usr/bin/python

"""
This module contains a set of commands for communication with Thyracont VSP transducers
based on PyVISA library and custom data_packages module.

Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# standard library imports
import sys

# third party imports
# pyqt-related imports
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QTabWidget, QWidget

# local gui imports
from positioning.drives.params import QDriveParams

# load configurations
import tomli
with open("config.toml", mode='rb') as config_file:
    config = tomli.load(config_file)

class MainWindow(QMainWindow):

    def __init__(self, config):
        
        super().__init__()

        self.config = config
        self.initUI()

    def initUI(self):

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.grid = QGridLayout()
        self.central_widget.setLayout(self.grid)

        self.params_widget = QDriveParams(config, name='DRX')
        self.grid.addWidget(self.params_widget, 0, 0)

        # Resize main window and set title
        self.setWindowTitle('Lithography')
        self.show()

def main():

    app = QApplication(sys.argv)
    window = MainWindow(config)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
