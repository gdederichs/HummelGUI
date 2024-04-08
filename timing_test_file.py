import nidaqmx
from nidaqmx.constants import AcquisitionType

import numpy as np
from matplotlib import pyplot as plt

import time
import util

######## USB 6216 does not support hardware timing via python/nidaqmx. ############

######## NEW: USB 6341 seems to support hardware timing via python/nidaqmx ########

#simple task
device = "Dev4"
dt, signal = util.fct1(A=util.ampl, f=10, t=3, sampling_rate=util.sampling_rate)



with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")

    task.timing.cfg_samp_clk_timing(rate=util.sampling_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.size(signal)) 
    #SAMPLING RATE NOT EXACTLY UNDERSTOOD:
    #correct frequency of signal is obtained but not the correct total duration
    #by playing around with values: f_out = f_in*rate_cfg/rate_real and t_out = 1000/rate_cfg
    #idea: samps_per_chan is set to 1000 default! --> simply specify number of samples in the signal
    #can use this to write multiple periods: four x periods: samps_per_chan = x*np.size(signal)
    #update: this works hehe


    task.write(signal)
    task.start()

    plt.plot(dt, signal)
    plt.grid()
    plt.show()
    #np.set_printoptions(precision=2, suppress=True)
    #print(signal)

    task.wait_until_done(30)

    print("done.")