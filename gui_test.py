import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject

import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util

device = "SimDev"

dt, signal = util.fct1(util.ampl, util.freq, util.duration, util.sampling_rate)

task = nidaqmx.Task()
task.ao_channels.add_ao_voltage_chan(device+"/ao0")

# Step 1: Create a worker class
class Worker(QObject):
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, task, signal, parent = None) -> None:
        super().__init__(parent)
        self.task = task
        self.signal = signal

    def sendSignal(self):
        if device == "SimDev":
            print("Output of virtual signal")
            time.sleep(10)
        else:
            print("starting sig")
            self.task.start()
            self.task.write(self.signal)
            self.task.stop()
            print("finsiehd sig")
            self.finished.emit()



class Window(QMainWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.clicksCount = 0
        self.setupUi()

    def stop(self, task):
        print("stop button pressed")
        task.stop()
        print("stop called")

    def close(self, task):
        task.close()

    def run_sendSignal(self):
        self.thread = QThread()
        self.worker = Worker(task,signal)
        self.worker.moveToThread(self.thread)

        self.thread.started.connect(self.worker.sendSignal)
        self.thread.finished.connect(self.thread.deleteLater)

        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)

        self.thread.start()

    def setupUi(self):
        self.setWindowTitle("NIBS GUI")
        self.setGeometry(200, 200, 500, 400)
        self.centralWidget = QWidget()
        self.setCentralWidget(self.centralWidget)
        # Create and connect widgets
        send_btn = QPushButton("send signal", self)
        send_btn.clicked.connect(lambda:self.run_sendSignal())

        stop_btn = QPushButton("stop", self)
        stop_btn.clicked.connect(lambda:self.stop(task))

        close_btn = QPushButton("close", self)
        close_btn.clicked.connect(lambda:self.close(task))

        stop_btn.move(0,50)
        close_btn.move(0,100)



app = QApplication(sys.argv)
win = Window()
win.show()

app.aboutToQuit.connect(task.close())
sys.exit(app.exec())