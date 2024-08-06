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
from stage.widget import QStageWidget
from backend.resources.manager import QResourceManager

# load configurations
config_file = os.path.join("config", "config.json")
with open(config_file, "r") as file:
    config = json.load(file)

class MainWindow(QMainWindow):

    def __init__(self, config):
        
        super().__init__()

        self.config = config
        self.rm = QResourceManager(self.config)

        self.initUI()

    def initUI(self):

        # Initialiaze main widget
        self.stage_widget = QStageWidget(self.config["gui"]["stage"], self.rm)
        self.setCentralWidget(self.stage_widget)

        # Resize main window and set title
        self.setWindowTitle('Lithography')
        
        # Fullscreen
        self.resize(1920, 1080)
        self.showMaximized()
        
        self.show()

print(os.getcwd())

def main():

    app = QApplication(sys.argv)
    window = MainWindow(config)

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
