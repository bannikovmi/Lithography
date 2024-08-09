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

# local imports
from stage.widget import QStageWidget
from backend.resources.manager import QResourceManager
from config.init_config import init_config

class MainWindow(QMainWindow):

    def __init__(self):
        
        super().__init__()

        # Load config files and create resource manager instance
        self.config = init_config("config") 
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

def main():

    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
