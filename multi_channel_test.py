import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf

import numpy as np
from matplotlib import pyplot as plt

import time
import util


device = "SimDev"
signals = util.iTBS()

with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.ao_channels.add_ao_voltage_chan(device+"/ao1")
    task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(signals)[1])

    task.write(signals)
    task.start()
    time.sleep(3)
    task.wait_until_done(inf)

    print("done.")