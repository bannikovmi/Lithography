from PyQt5.QtCore import QObject, Qt
from PyQt5.QtWidgets import (
    QDoubleSpinBox,
    QGroupBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget
    )

import numpy as np

class QMapper(QObject):
    """
    A class for representing various scales.

    In mathematical terms a mapper is a tuple of two intervals [x_min, x_max] and [y_min, y_max]
    and a mapping function f(x) : [x_min, x_max] -> [y_min, y_max]. Input parameters are intervals
    and mapping function class (i.e. linear/logarithmic etc)

    Parameters
    ----------
    x_min : float
        Minimal value of the input scale (default=0).
    x_max : float
        Maximal value of the input scale (default=100). Raises a ValueError if x_max <= x_min.
    y_min : float
        Minimal value of the output scale (default=0).
    y_max: float
        Maximal value of the output scale (default=100). Raises a ValueError if y_max <= y_min.
    map_func : function
        The function mapping one interval to another (default function: f(x)=x). 
        The function should be monotonous and continiously differentiable over [x_min, x_max]
        interval. Both increasing and decreasing functions are valid.
    inverse_map_func : function
        The inverse of the mapping function (default function: f(x)=x). 
        User should make sure that it is indeed the inverse of the map_func.
    """

    def __init__(self,
        x_min: float=0,
        x_max: float=100,
        y_min: float=0,
        y_max: float=100, 
        map_func=lambda x: x,
        inverse_map_func=lambda x: x):
        # Save class arguments as attributes
        self.x_min = x_min
        self.x_max = x_max
        self.y_min = y_min
        self.y_max = y_max
        self.map_func = map_func
        self.inverse_map_func = inverse_map_func        

    def evaluate(self, x):
        """ Evaluate the mapping function for the given argument."""
        return self.map_func(x)

    def evaluate_inverse(self, y):
        """ Evaluate the inverse of the mapping function for the given argument."""
        return self.inverse_map_func(y)

    ####################################################################################
    # Commonly used mappers
    ####################################################################################
    @classmethod
    def linear(cls, x_min=0, x_max=100, y_min=0, y_max=100):
        """Linear mapping function y = a*x + b"""
        # Calculate ranges
        y_range = y_max - y_min
        x_range = x_max - x_min
    
        def map_func(x):
            return y_min + y_range*((x - x_min)/x_range)
        def inverse_map_func(y):
            return x_min + x_range*((y-y_min)/y_range)

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)

    @classmethod
    def square(cls, x_min=0, x_max=100, y_min=0, y_max=100):

        """Quadratic mapping function y = a*(x-x_min)^2 + b"""
        if x_min < 0:
            raise ValueError("x_min should be >= 0")

        # Calculate ranges
        y_range = y_max - y_min
        x_range = x_max - x_min
    
        def map_func(x):
            return y_min + y_range*((x - x_min)/x_range)**2
        def inverse_map_func(y):
            return x_min + x_range*((y-y_min)/y_range)**(1/2)

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)

    @classmethod
    def log10(cls, x_min=0, x_max=100, y_min=1e-2, y_max=100):
        """Exponential mapping function y = 10**(a*(x-b))"""
        
        if y_min <= 0:
            raise ValueError("y_min should be > 0")

        # Calculate a and b
        a = np.log10(y_max/y_min)/(x_max - x_min)
        b = x_max - np.log10(y_max)/a
    
        def map_func(x):
            return pow(10, a*(x-b))
        def inverse_map_func(y):
            return b + np.log10(y)/a

        return cls(x_min, x_max, y_min, y_max, map_func, inverse_map_func)

class QNumericControl(QWidget):
    
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
        self.slider = QSlider(orientation=Qt.Horizontal)
        self.slider.setMaximum(1000) # higher-resolution slider
        self.slider.setMinimumWidth(150)

        self.spinbox = QDoubleSpinBox()
        match self.dtype:
            case "int":
                self.spinbox.setDecimals(0)
            case "float":
                self.spinbox.setDecimals(2)
            case _:
                raise ValueError("Unknown datatype")

        self.units_lab = QLabel(self.units)

        self.hbox1.addWidget(self.name_label, 0)
        self.hbox1.addWidget(self.slider, 1)
        self.hbox1.addWidget(self.spinbox, 2)
        self.hbox1.addWidget(self.units_lab, 3)

        self.hbox1.setStretch(0, 0)
        self.hbox1.setStretch(1, 1)
        self.hbox1.setStretch(2, 0)
        self.hbox1.setStretch(3, 0)

        self.slider.valueChanged.connect(self.on_slider_change)
        self.spinbox.valueChanged.connect(self.on_spinbox_change)

    def on_slider_change(self, val):
        
        self.spinbox.valueChanged.disconnect()
        self.spinbox.setValue(self.mapper.evaluate(val))
        self.spinbox.valueChanged.connect(self.on_spinbox_change)

    def on_spinbox_change(self, val):
        
        self.slider.valueChanged.disconnect()
        self.slider.setValue(round(self.mapper.evaluate_inverse(val)))
        self.slider.valueChanged.connect(self.on_slider_change)

    def setMapper(self, mapper_type):

        y_min = self.spinbox.minimum()
        y_max = self.spinbox.maximum()

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

        self.spinbox.setMaximum(val)
        self.setMapper(self.mapper_type)

    def setMinimum(self, val):

        self.spinbox.setMinimum(val)
        self.setMapper(self.mapper_type)

    def value(self):

        return self.spinbox.value()

    def setValue(self, val):

        self.spinbox.setValue(val)

class QNumericIndicator(QWidget):

    def __init__(self, label="", units="", fstring=".3f", mapper_type="linear", 
        min_value = 0, max_value = 1000, orientation=Qt.Horizontal):

        self.label = label
        self.units = units
        self.fstring = fstring
        self.mapper_type = mapper_type
        self.min_value = min_value
        self.max_value = max_value
        self.orientation = orientation

        super().__init__()
        self.initUI()

        self.setMapper(mapper_type)

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)

        self.name_label = QLabel(self.label)
        self.slider = QSlider(self.orientation)
        self.slider.setMaximum(1000) # higher-resolution slider
        self.slider.setDisabled(True)

        self.lineedit = QLineEdit()
        self.lineedit.setReadOnly(True)
        self.units_lab = QLabel(self.units)

        if self.orientation == Qt.Horizontal:
            self.layout = QHBoxLayout()
            alignment = Qt.AlignVCenter
            self.slider.setMinimumWidth(100)
            self.grid.addLayout(self.layout, 0, 0)
            self.grid.addWidget(self.slider, 1, 0)

        else:
            self.layout = QVBoxLayout()
            alignment = Qt.AlignHCenter
            self.slider.setMinimumWidth(100)
            self.grid.addLayout(self.layout, 0, 0)
            self.grid.addWidget(self.slider, 0, 1)

        self.layout.addWidget(self.name_label, 0, alignment=alignment)
        self.layout.addWidget(self.lineedit, 1, alignment=alignment)
        self.layout.addWidget(self.units_lab, 2, alignment=alignment)

        self.lineedit.setMaximumWidth(70)

    def value(self):

        return float(self.lineedit.text())

    def setValue(self, val):

        self.lineedit.setText(f"{val:self.fstring}")
        
        if val > self.max_value:
            slider_val = round(self.mapper.evaluate_inverse(self.max_value))
        elif val < self.min_value:
            slider_val = round(self.mapper.evaluate_inverse(self.min_value))
        else:
            slider_val = round(self.mapper.evaluate_inverse(val))

        self.slider.setValue(slider_val)

    def setMapper(self, mapper_type):

        y_min = self.min_value
        y_max = self.max_value

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

        self.max_value = val
        self.setMapper(self.mapper_type)

    def setMinimum(self, val):

        self.min_value = val
        self.setMapper(self.mapper_type)
