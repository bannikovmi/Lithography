from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QSlider,
    QVBoxLayout,
    QWidget
    )

import numpy as np

from .mapper import QMapper
from .range_slider import QRangeSlider

class QDoubleControl(QWidget):

	valueChanged = pyqtSignal(float, float)

    def __init__(self, 
        label="",
        units="",
        mapper_type="linear",
        dtype="int"
    ):

        self.label = label
        self.units = units
        self.mapper_type = mapper_type
        self.dtype = dtype

        super().__init__()
        self.initUI()

        self.setMapper(mapper_type)

    def initUI(self):

        self.vbox = QVBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.setLayout(self.vbox)
        self.vbox.addLayout(self.hbox1)

        self.name_label = QLabel(self.label)
        self.slider = QRangeSlider()
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setMaximum(1000) # higher-resolution slider
        self.slider.setMinimumWidth(150)

        self.spinbox_low = QDoubleSpinBox()
        self.spinbox_high = QDoubleSpinBox()
        match self.dtype:
            case "int":
                self.spinbox_low.setDecimals(0)
                self.spinbox_high.setDecimals(0)
            case "float":
                self.spinbox_low.setDecimals(2)
                self.spinbox_high.setDecimals(2)
            case _:
                raise ValueError("Unknown datatype")

        self.units_lab = QLabel(self.units)

        self.hbox1.addWidget(self.name_label, 0)
        self.hbox1.addWidget(self.slider, 1)
        self.hbox1.addWidget(self.spinbox_low, 2)
        self.hbox1.addWidget(self.spinbox_high, 2)
        self.hbox1.addWidget(self.units_lab, 4)

        self.hbox1.setStretch(0, 0)
        self.hbox1.setStretch(1, 1)
        self.hbox1.setStretch(2, 0)
        self.hbox1.setStretch(3, 0)
        self.hbox1.setStretch(4, 0)

        self.slider.sliderMoved.connect(self.on_slider_change)
        self.spinbox_low.valueChanged.connect(self.on_spinbox_low_change)
        self.spinbox_high.valueChanged.connect(self.on_spinbox_high_change)
        # self.valueChanged.connect(lambda val: print(f"setting {self.label} value to {val}"))

    def on_slider_change(self, low, high):
        
        low_val = self.mapper.evaluate(low)
        high_val = self.mapper.evaluate(high)
        self.valueChanged.emit(low_val, high_val)

        self.spinbox_low.valueChanged.disconnect()
        self.spinbox_low.setValue(low_val)
        self.spinbox_low.valueChanged.connect(self.on_spinbox_low_change)

        self.spinbox_high.valueChanged.disconnect()
        self.spinbox_high.setValue(high_val)
        self.spinbox_high.valueChanged.connect(self.on_spinbox_high_change)

    def on_spinbox_low_change(self, val):
        
        self.valueChanged.emit(val, self.spinbox_high.value())
        self.slider.valueChanged.disconnect()
        self.slider.setLow(round(self.mapper.evaluate_inverse(val)))
        self.slider.valueChanged.connect(self.on_slider_change)

    def on_spinbox_high_change(self, val):
        
        self.valueChanged.emit(self.spinbox_low.value(), val)
        self.slider.valueChanged.disconnect()
        self.slider.setHigh(round(self.mapper.evaluate_inverse(val)))
        self.slider.valueChanged.connect(self.on_slider_change)

    def setDecimals(self, val):

        self.spinbox_low.setDecimals(val)
        self.spinbox_high.setDecimals(val)

    def setMapper(self, mapper_type):

        y_min = self.spinbox_low.minimum()
        y_max = self.spinbox_high.maximum()

        match mapper_type:
            case "linear":
                self.mapper = QMapper.linear(0, 1000, y_min, y_max)
            case "square":
                self.mapper = QMapper.square(0, 1000, y_min, y_max)
            case "log10":
                self.mapper = QMapper.log10(0, 1000, y_min, y_max)
            case _:
                raise ValueError("Unknown mapper type")

    def setMaximum(self, val):

        self.spinbox_high.setMaximum(val)
        self.setMapper(self.mapper_type)

    def setMinimum(self, val):

        self.spinbox_low.setMinimum(val)
        self.setMapper(self.mapper_type)

    def value(self):

        return self.spinbox.value()

    def setValue(self, val):

        self.spinbox.setValue(val)

    def setSingleStep(self, val):

        self.spinbox.setSingleStep(val)

