import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util

######## USB 6216 does not support hardware timing. Timing must be set via software: investigated here ############

task = nidaqmx.Task()
scond_tas = nidaqmx.stream
task.ao_channels.add_ao_voltage_chan('Dev2/ao0')
task.timing.cfg_samp_clk_timing(rate=util.sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) # ATTENTION: USB-6216 does not support hardware timing
task.write_many_samples

#test function to be sent
dt, signal = util.fct1(A=2,f=1,t=5,sampling_rate=util.sampling_rate)
#plt.plot(dt, signal)
#plt.show()

task.start()


task.write(signal)


task.stop()
task.close()