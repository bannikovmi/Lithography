from PyQt5.QtWidgets import QGridLayout, QGroupBox, QDoubleSpinbox, QSlider

class QCoupledSlider(QGroupBox):
    
    def __init__(self, label):

        super().__init__(label)
        self.initUI()

    def initUI(self):

        self.grid = QGridLayout
        self.setLayout(self.grid)

        self.slider = QSlider()
        self.spinbox = QDoubleSpinbox()

        self.grid.addWidget(self.slider, 0, 0)
        self.grid.addWidget(self.spinbox, 0, 1)

        self.grid.setColumnStretch(0, 1)


    def setMinumum(self, val):

        self.slider.setMinumum(val)
        self.spinbox.setMinumum(val)

    def setMaximum(self, val):

        self.slider.setMaximum(val)
        self.spinbox.setMaximum(val)

    def setValue(self, val):

        self.slider.setValue(val)
        self.spinbox.setValue(val)

    def setSingleStep(self, step):

        self.slider.setSingleStep(step)
        self.spinbox.setSingleStep(step)