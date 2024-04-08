import sys
from PyQt6.QtWidgets import QApplication, QLabel, QWidget, QPushButton, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, pyqtSignal, QThread, QObject

import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util
import threading

device = "SimDev"

print("Signal parameters: \nAmplitude: {} \nFrequency: {} \nDuration: {}".format(util.ampl, util.freq, util.duration))
dt, signal = util.fct1(util.ampl, util.freq, util.duration, util.sampling_rate)



with nidaqmx.Task() as task:
    
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.timing.cfg_samp_clk_timing(util.sampling_rate)

    def test_stop(task):
        print("stopping in 2 seconds")
        time.sleep(2)
        task.stop()
        print("stopping now")

    task.start()

    start_time = time.time()
    thread1 = threading.Thread(target=task.write,args=(signal,))
    thread2 = threading.Thread(target=test_stop, args=(task,))

    print("threads started")
    thread1.start()
    thread2.start()


    thread1.join()
    thread2.join()
    print("threads joined")

    stop_time = time.time()

    print("\nOverall time: {:.2f}s \nSignal duration: {}s".format(stop_time-start_time,util.duration))



    #FOLLOW UP IDEA FOR NEXT TESTS: 
    # remove stop from thread2 and have it on main code
    # or opposite: have stop on thread1 and have task on main (maybe more logical)
    # with both the stop and write function in threads: doesn't seem to work