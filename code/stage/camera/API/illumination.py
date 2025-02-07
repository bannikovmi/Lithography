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

from backend.resources.resource import QResource

class QIlluminator(QResource):

    props = {
        "freq": "FRQ",
        "duty": "DUT",
    }

    def __init__(self, resource):

        super().__init__(resource)

        # master resource
        self.esp = self.master_int.master

    ##########################################################################################
    ### Property-related functions
    ##########################################################################################
    def get(self, key):
        message = self.esp.query(f"{self.name}_{self.props[key]}")
        return int(message.split("_")[2])

    def set(self, key, val):
        setattr(self, f"_{key}", val) # update hidden attribute
        self.esp.write(f"{self.name}_{self.props[key]}_{val}")
