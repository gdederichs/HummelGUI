import nidaqmx
import threading
import numpy as np
import util
from matplotlib import pyplot as plt
from nidaqmx.constants import AcquisitionType


#THIS FILE IS A SCRAP FILE FOR TESTING OF DIFFERENT CODE SNIPPETS, FUNCTIONS, ETC.
#THERE SHOULD BE NO IMPORTANT CODE IN THIS FILE THAT HAS NOT BEEN IMPLEMENTED IN ANOTHER FILE


"""
request_update = False

def update():
    global current_signal
    if request_update == True:
        dt, new_signal = util.fct1(2, 20, 3, sampling_rate)
        with lock:
            current_signal = new_signal

def write_task():
    global current_signal
    with lock:
        task.write(current_signal)
        print("wrote signal with amplitude {:.0f}".format(np.max(current_signal)))

sampling_rate = 50
dt, signal = util.fct1(3, 10, 3, sampling_rate)


task = nidaqmx.Task()
task.ao_channels.add_ao_voltage_chan("Dev1/ao0")
task.timing.cfg_samp_clk_timing(rate=sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS)
current_signal = signal

task.start()
for i in range(3):
    if i == 1:
        request_update=True

    lock = threading.Lock()
    update_thread = threading.Thread(target=update)
    write_thread = threading.Thread(target=write_task)

    update_thread.start()
    write_thread.start()

    update_thread.join()
    write_thread.join()

task.stop()
task.close()
"""


"""
g = util.fct1(3,100,9,1000)
print(np.shape(g))



import nidaqmx

with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan("SimDev/ao0")

    task.timing.cfg_samp_clk_timing(1000)


    print("1 Channel N Samples Write: ")
    print(task.write([1.1, 2.2, 3.3, 4.4, 5.5], auto_start=True))
    task.wait_until_done()
    task.stop()


    task.ao_channels.add_ao_voltage_chan("SimDev/ao1")

    print("N Channel N Samples Write: ")
    print(task.write([[1.1, 2.2, 3.3, 4.4, 5.5],[1.1, 2.2, 3.3, 4.4, 5.5]], auto_start=True))
    task.wait_until_done()
    task.stop()
"""



"""
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")

    task.timing.cfg_samp_clk_timing(1000)

    print("1 Channel N Samples Write: ")
    print(task.write([1.1, 2.2, 3.3, 4.4, 5.5], auto_start=True))
    task.wait_until_done()
    task.stop()
"""