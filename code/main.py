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
from stage.tab import QStageTab
from initialization.resources.manager import QResourceManager
from tasks.manager import QTaskManager

# load configurations
config_file = os.path.join("config", "config.json")
with open(config_file, "r") as file:
    config = json.load(file)

class MainWindow(QMainWindow):

    def __init__(self, config):
        
        super().__init__()

        self.config = config
        self.resource_manager = QResourceManager(self.config)
        self.task_manager = QTaskManager(self.config, self.resource_manager)

        self.initUI()

    def initUI(self):

        # Create tab widgets
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.stage_tab = QStageTab(self.task_manager, simulation=True)
        self.tabs.addTab(self.stage_tab, "Stage control")

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
