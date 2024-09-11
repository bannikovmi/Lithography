from PyQt5.QtWidgets import QApplication
from tests.exposure import App

import sys

app = QApplication(sys.argv)
a = App()
a.show()
sys.exit(app.exec_())
