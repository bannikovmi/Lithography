class QMotionGB(QGroupBox):

    def __init__(self, config, ESP, label):

        self.config = config
        self.ESP = ESP

        super().__init__(label)
        self.initUI()

        self.x_power_toggle()
        self.y_power_toggle()        
        self.x_moving = False
        self.y_moving = False

    def initUI(self):

        self.grid = QGridLayout()
        self.setLayout(self.grid)