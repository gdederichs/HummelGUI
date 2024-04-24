import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf

import numpy as np
from matplotlib import pyplot as plt

import time
import HummelGUI.util as util

device = util.device
dt, signals = util.iTBS()

with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.ao_channels.add_ao_voltage_chan(device+"/ao1")
    task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(signals)[1])


    task.write(signals)
    task.start()

    # update - artificial
    time.sleep(1.5)
    task.stop()
    #dt, signals = util.iTBS(cycle_f=10)
    #task.write(signals)
    #task.start()
    # ------------------

    task.wait_until_done(inf)
    

    print("done.")




"""
############ TO DO ############
1) write documentation of functions
2) write report 2
3) implement the following
general structure:
def run():
    all code to run the task
    ...
    ...
    ...
    while not task.is_task_done():
        if trigger:
            task.stop()
            new_signal
            run(task, new_signal)

in main:

with nidaqmx.Task() as task:
    signals = ...
    task.run(task,signals)
    task.wait_until_done(inf) #as safety only

    
"""