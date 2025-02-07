from PyQt5.QtCore import Qt

from .mapper import QMapper

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
