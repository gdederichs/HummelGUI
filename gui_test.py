import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject

import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util


class SignalSender(QObject): #for threading... need to look into this more in detail
    finished = pyqtSignal()
    progress = pyqtSignal(int)

    def __init__(self, task, signal):
        super().__init__()
        self.task = task
        self.signal = signal

    def run(self): #is auto called by sender.start()
        self.task.start()
        self.task.write(self.signal)
        self.task.stop()
        self.finished.emit()




def send(task, signal):
    task.start()
    task.write(signal)
    task.stop()


    #Trying threading:
    """sender = SignalSender(task, signal)
    sender.finished.connect(lambda:print("Signal sent")) 
    sender.start()
    sender.wait()"""

def stop(task):
    task.stop()

def close(task):
    task.close()

app = QApplication([])

window = QWidget()
window.setWindowTitle("NIBS GUI")
window.setGeometry(200, 200, 500, 400)

send_btn = QPushButton("send signal", parent=window)
stop_btn = QPushButton("stop", parent=window)
close_btn = QPushButton("close", parent=window)
stop_btn.move(0,50)
close_btn.move(0,100)



window.show()
dt, signal = util.fct1(util.ampl, util.freq, util.duration, util.sampling_rate)

task = nidaqmx.Task()
task.ao_channels.add_ao_voltage_chan("Dev2/ao0")


send_btn.clicked.connect(lambda:send(task,signal))
stop_btn.clicked.connect(lambda:stop(task))
close_btn.clicked.connect(lambda:close(task))

app.aboutToQuit.connect(task.close)
sys.exit(app.exec())