import nidaqmx
from nidaqmx.constants import AcquisitionType

import numpy as np
from matplotlib import pyplot as plt

import time
import util

#Parameters
device = "SimDev"

fct_times = []
real_times = []

for time_exp in range(1,10):

    fct_time = util.duration*time_exp
    dt, signal = util.fct1(A=util.ampl, f=util.freq, t=fct_time, sampling_rate=util.sampling_rate)
    sub_dts, sub_signals = util.subdivide(dt, signal, chunk_time=1.3)

    with nidaqmx.Task() as task:
        task.ao_channels.add_ao_voltage_chan(device+"/ao0") 
        
        if np.shape(sub_signals[0]) != np.shape(sub_signals[-1]):
            print("Warning: Not all signals are of equal size")

        a = time.time()
        for sub_signal in sub_signals:
            task.timing.cfg_samp_clk_timing(rate=util.sampling_rate, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.size(sub_signal))
            task.write(sub_signal)
            task.start()
            task.wait_until_done()
            task.stop()

        real_times.append(time.time()-a)
        fct_times.append(fct_time)

np_real_times = np.asarray(real_times)
np_fct_times = np.asarray(fct_times)

plt.plot(np_real_times, np_real_times-np_fct_times, marker='2', linestyle=':')
plt.xlabel('Duration of the Signal')
plt.ylabel('Delay in Execution')
plt.title('Evaluation of the Delay caused by util.subdivide()')
plt.grid(True)
plt.show()