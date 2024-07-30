from PyQt5.QtCore import QObject

class QInterface(QObject):

    slaves = {}

    def __init__(self, name, master):

        self.name = name
        self.master = master

        super().__init__()

    def add_slave(self, slave):
        self.slaves[slave.name] = slave
    

