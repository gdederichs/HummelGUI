import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject

import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util
import threading

device = "Dev2"

dt, signal = util.fct1(util.ampl, util.freq, util.duration, util.sampling_rate)
print(np.size(signal),"=========")

task = nidaqmx.Task()
task.ao_channels.add_ao_voltage_chan(device+"/ao0")
task.timing.cfg_samp_clk_timing(util.sampling_rate)

def test_stop():
    print("stopping in 2 seconds")
    time.sleep(2)
    task.stop()
    print("stopping now")

task.start()
thread1 = threading.Thread(target=task.write,args=(signal,))
thread2 = threading.Thread(test_stop())

thread1.start()
thread2.start()
print("threads started")

thread1.join()
thread2.join()
print("threads joined")

task.close()