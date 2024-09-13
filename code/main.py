#!/usr/bin/python

"""
Author: Mikhail Bannikov bannikovmi96@gmail.com
"""

# standard library imports
import json
import os
import sys

# third party imports
# pyqt-related imports
from PyQt5.QtCore import QThreadPool
from PyQt5.QtWidgets import (
    QApplication,
    QGridLayout,
    QMainWindow,
    QMenu,
    QTabWidget,
    QWidget,
    QWidgetAction
)

# local imports
from stage.GUI.stage import QStageWidget
from backend.resources.manager import QResourceManager
from config.init_config import init_config

from exposure.GUI.exposure import QExposureWidget

# We need more threads
QThreadPool.globalInstance().setMaxThreadCount(5)

class MainWindow(QMainWindow):

    def __init__(self):
        
        super().__init__()

        # Load config files and create resource manager instance
        self.config = init_config("config") 
        self.rm = QResourceManager(self.config)

        self.initUI()

    def initUI(self):

        # Initialiaze main widget
        self.stage_widget = QStageWidget(self.config["GUI"]["stage"], self.rm)
        self.setCentralWidget(self.stage_widget)

        # Menus
        self.expo_menu = QMenu("Exposure")
        self.menuBar().addMenu(self.expo_menu)

        self.expo_qwa = QWidgetAction(self.expo_menu)
        self.expo_widget = QExposureWidget(self.config["GUI"]["menus"]["exposure"], self.rm)
        self.expo_qwa.setDefaultWidget(self.expo_widget)
        self.expo_menu.addAction(self.expo_qwa)

        # Resize main window and set title
        self.setWindowTitle('Lithography')

        # Fullscreen
        self.resize(1920, 1080)
        self.showMaximized()
        
        self.show()

    def closeEvent(self, event):
        
        self.expo_widget.closeEvent(event)
        self.stage_widget.closeEvent(event)

        event.accept()

def main():

    app = QApplication(sys.argv)
    window = MainWindow()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

# import paramiko, time

# ssh_params = {
#     "hostname": "192.168.3.160",
#     "port": 22,
#     "username": "litho-proj-1",
#     "password": "FIAN1234"
# }

# ssh = paramiko.SSHClient()
# ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# ssh.connect(**ssh_params)

# # ssh.exec_command("python /media/init.py")

# channel = ssh.invoke_shell()
# while not channel.recv_ready():
#     time.sleep(0.3)
# channel.recv(9999) # skip initial info

# print("starting loop...", end='\t')
# channel.send("python /media/loop.py\n")
# print("finished")

# print("starting to listen:")
# while True:
#     print(">>>", end='\t')
#     send = input()
#     channel.send(f"{send}\n")
#     print("ready")
#     if send == "q":
#         print("breaking")
#         break

# channel.close()

# ssh.exec_command("python /media/stop.py")

# channel.send("python /media/init.py\n")
# while not channel.recv_ready():
#     time.sleep(0.3)
# channel.recv(9999).decode('utf-8')


# channel.send("python /media/stop.py\n")
# while not channel.recv_ready():
#     time.sleep(0.3)
# channel.recv(9999).decode('utf-8')

# channel.send("python /media/pyssh/loop.py\n")
# while not channel.recv_ready():
#     time.sleep(0.3)
# channel.recv(9999).decode('utf-8')

# while True:

#     channel.send(input())
#     while not channel.recv_ready():
#         time.sleep(0.3)
#     channel.recv(9999).decode('utf-8')

# stdin, stdout, stderr = ssh.exec_command('ls /media')

# result = stdout.read().decode('utf-8')
# print(result)

# import cv2 as cv
# import numpy as np
# import matplotlib.pyplot as plt

# img = cv.imread('exposure/pics/grid.png')
# assert img is not None, "file could not be read, check with os.path.exists()"

# rows,cols,ch = img.shape
# pts1 = np.float32([[150, 150],[325, 150], [323, 323]])
# pts2 = np.float32([[0, 0], [473, 0], [473, 473]])

# for pt1, pt2 in zip(pts1, pts2):
#     cv.circle(img, (int(pt1[0]), int(pt1[1])), 10, (0,0,255), -1)
#     cv.circle(img, (int(pt2[0]), int(pt2[1])), 10, (255,0,0), -1)

# M = cv.getAffineTransform(pts1,pts2)
# dst = cv.warpAffine(img,M,(cols,rows))


# plt.subplot(121),plt.imshow(img),plt.title('Input')
# plt.subplot(122),plt.imshow(dst),plt.title('Output')
# plt.show()