from collections import deque
import time

import numpy as np

from PyQt5.QtCore import pyqtSignal, QObject

class QFocusRecorder(QObject):

    data_updated = pyqtSignal(list, list)

    def __init__(self, drive, record_params):

        self.drive = drive
        print(self.drive.name)
        self.scan_mode = record_params["scan_mode"]
        self.file_path = record_params["file_path"]
        self.avg_frames = record_params["avg_frames"]

        self.var_counter = 0

        super().__init__()

        self.pos_list = []
        self.var_list = []

    def start(self):

        self.drive.movement_finished.connect(self.record_point)

    def stop(self):

        self.drive.movement_finished.disconnect(self.record_point)

    def record_point(self):

        # Set counter to 0 and wait until enough frames were recorded
        self.var_counter = 0
        # while self.var_counter < self.avg_frames:
        #     time.sleep(30e-3)

        # Get position and append data to lists
        pos = float(self.drive.pos)
        self.var_list.append(self.var)
        self.pos_list.append(pos)

        if self.file_path is not None:
            with open(self.file_path, "a") as file:
                file.write(f"{pos:.4f}\t{self.var:.4f}\n")

        self.data_updated.emit(self.pos_list, self.var_list)

    def on_var_update(self, var):

        self.var_counter += 1
        self.var = var
        