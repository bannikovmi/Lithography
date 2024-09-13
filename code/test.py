import sys
from PyQt5.QtWidgets import QApplication
from tests.exposure.app import App

app = QApplication(sys.argv)
a = App()
a.show()
sys.exit(app.exec_())
