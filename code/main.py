#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# standard library imports
import json
import os
import sys

# third party imports
# pyqt-related imports
from PyQt5.QtWidgets import QApplication, QGridLayout, QMainWindow, QTabWidget, QWidget

# local gui imports
from positioning.tab import QPositioningTab
from initialization.resources import QResourceManager
# from tasks.manager import QTaskManager

# load configurations
config_file = os.path.join("config", "config.json")
with open(config_file, "r") as file:
    config = json.load(file)

class MainWindow(QMainWindow):

    def __init__(self, config):
        
        super().__init__()

        self.config = config
        self.rm = QResourceManager(self.config)

        for key, val in self.rm.resources.items():
            print(key, val.__dict__)

        # self.tm = QTaskManager(self.config, self.rm)
        self.initUI()

    def initUI(self):

        # Create tab widgets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # self.positioning_tab = QPositioningTab(self.config, simulation=True)
        # self.tabs.addTab(self.positioning_tab, "Positioning")

        # Resize main window and set title
        self.setWindowTitle('Lithography')
        
        # Fullscreen
        self.resize(1920, 1080)
        self.showMaximized()
        
        self.show()

def main():

    app = QApplication(sys.argv)
    window = MainWindow(config)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
