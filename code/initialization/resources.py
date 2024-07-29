from PyQt5.QtCore import pyqtSignal, QMutex, QObject

import pyvisa

#testing
import logging
logging.basicConfig(format='%(levelname)s:%(asctime)s:%(message)s', level=logging.CRITICAL)

class ResourceManager():

    def __init__(self, config):
        
        self.pyvisa_rm = pyvisa.ResourceManager()
        self.config = config

    def get_resources(self):

        res = {}
        
        for name in self.config["resources"]:

            address = self.config["resources"][name]["address"]
            pyvisa_handler = self.rm.open_resource(address)
    
            res[name] = QResource(name, pyvisa_handler)

        return res

class QResource(QObject):

    def __init__(self, 
        name: str = "",
        pyvisa_handler = None,
        parent=None,
    ):
        
        super().__init__()

        logging.info(f"QResource {name} init")

        # Save data to local variables
        self.name = name
        self.pyvisa_handler = pyvisa_handler
        self.parent = parent
        self.mutex = QMutex()

    # Common methods
    def clear(self):
        if self.parent is None:
            self.pyvisa_handler.clear()

    def close(self):
        if self.parent is None:
            self.pyvisa_handler.close()

    def read(self):
        if self.parent is None:
            return self.pyvisa_handler.read()
        else:
            self.parent.pyvisa_handler.read()

    def write(self, message):
        return self.pyvisa_handler.write(message)

    def query(self, message):
        return self.pyvisa_handler.query(message)

    # Mutex version of query
    def mutex_query(self, message):
        logging.info(f"QResource {self.name} query {message} ?")
        self.mutex.lock()
        logging.info(f"QResource {self.name} query {message} lock_mutex")
        res = self.query(message)
        logging.info(f"QResource {self.name} query {message} unlock_mutex")
        self.mutex.unlock()
        logging.info(f"QResource {self.name} query {message} {res}")
        return res
