# standard library imports
import os
from paramiko import AutoAddPolicy, SSHClient

# third-party imports
# PyQt-related imports
from PyQt5.QtCore import pyqtSignal, QObject, QRunnable, QThreadPool

# local imports
from backend import QResource

class RunnerSignals(QObject):

    finished = pyqtSignal()

class ExposureRunner(QRunnable):

    def __init__(self, rasp0, name, exposure_time):

        super().__init__()

        self.rasp0 = rasp0
        self.name = name
        self.exposure_time = exposure_time

        self.signals = RunnerSignals()

    def run(self):

        # Run expose_remote in current thread (separate_thread is False by default)
        self.rasp0.expose_remote(self.name, self.exposure_time) 
        self.signals.finished.emit()

class QRaspZero(QResource):

    exposure_finished = pyqtSignal()
    upload_finished = pyqtSignal()

    def __init__(self, resource):

        # Reinitialize base class resource
        self.name = resource.name
        self.master_int = resource.master_int
        self.config = resource.config

        # Global thread pool instance
        self.thread_pool = QThreadPool.globalInstance()

        super().__init__(self.name, self.master_int)

    def exec_command(self, command):

        with SSHClient() as ssh:
            
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(**self.config)
            
            stdin, stdout, stderr = ssh.exec_command(command)

            result = stdout.read().decode('utf-8')
            error = stderr.read().decode('utf-8')

            return result, error

    def expose_remote(self, name, exposure_time=2000, separate_thread=False):
        
        if separate_thread:
            exposure_runner = ExposureRunner(self, name, exposure_time)
            exposure_runner.signals.finished.connect(self.exposure_finished)

            self.thread_pool.start(exposure_runner)
        else:
            return self.exec_command(
                f"python /media/expose.py {name} {exposure_time}")
            

    def list_pics(self):

        files_string = self.exec_command("ls /media/pics")[0]
        return files_string.split()

    def get_file(self, remote_path, local_path):
        
        with SSHClient() as ssh:
            
            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(**self.config)

            with ssh.open_sftp() as sftp:
                sftp.get(remote_path, local_path)

    def put_file(self, local_path, remote_path):

        with SSHClient() as ssh:

            ssh.set_missing_host_key_policy(AutoAddPolicy())
            ssh.connect(**self.config)

            with ssh.open_sftp() as sftp:
                sftp.put(local_path, remote_path)

    def upload_pic(self, local_path):

        remote_path = os.path.join("/media", "pics", os.path.basename(local_path))
        self.put_file(local_path, remote_path)

    def connect(self):

        self.ssh = SSHClient()
        self.ssh.set_missing_host_key_policy(AutoAddPolicy())
        self.ssh.connect(**self.config)

    def disconnect(self):

        self.ssh.close()

