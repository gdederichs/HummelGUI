import nidaqmx
import nidaqmx.task
import numpy as np
from matplotlib import pyplot as plt
import time
import util
import threading

#TESTS: 
# with both the stop and write function in threads - stop called twice (WHY?); doesn't stop after 2 seconds
# stop on main code and write on a thread - doesn't stop after 2 seconds
# write on main code and stop on a thread - doesn't stop after 2 seconds

def test_stop(task):
    print("stopping in 2 seconds")
    time.sleep(2)
    print("attempting to stop")
    task.stop()
    print("task has stopped")

device = "SimDev"

print("Signal parameters:\
       \nAmplitude: {}\
       \nFrequency: {}\
       \nDuration: {}\
      ".format(util.ampl,
               util.freq,
               util.duration))

dt, signal = util.fct1(util.ampl, util.freq, util.duration, util.sampling_rate)


#WRITE in thread - STOP in main
start_time = time.time()
print("\n=================================\nSTOP in thread - WRITE in main")
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.timing.cfg_samp_clk_timing(util.sampling_rate)

    task.start()

    thread1 = threading.Thread(target=task.write, args=(signal,))
    thread1.start()
    print("thread start")
    test_stop(task)

stop_time = time.time()
print("\nOverall time: {:.2f}s\
        \nSignal duration: {}s\
        ".format(stop_time-start_time,util.duration))


#STOP in thread - WRITE in main
start_time = time.time()
print("\n=================================\nSTOP in thread - WRITE in main")
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.timing.cfg_samp_clk_timing(util.sampling_rate)

    task.start()

    stop_thread = threading.Thread(target=test_stop, args=(task,))
    task.write(signal)
    stop_thread.start()
    print("thread start")
 
stop_time = time.time()
print("\nOverall time: {:.2f}s\
        \nSignal duration: {}s\
        ".format(stop_time-start_time,util.duration))


#STOP in thread - WRITE in thread
start_time = time.time()
print("\n=================================\nSTOP in thread - WRITE in thread")
with nidaqmx.Task() as task:
    task.ao_channels.add_ao_voltage_chan(device+"/ao0")
    task.timing.cfg_samp_clk_timing(util.sampling_rate)
    task.start()

    stop_thread2 = threading.Thread(target=test_stop, args=(task,))
    write_thread2 = threading.Thread(target=task.write, args=(signal,))

    stop_thread2.start()
    write_thread2.start()
    print("threads start")

    stop_thread2.join()
    write_thread2.join()
 
stop_time = time.time()
print("\nOverall time: {:.2f}s\
        \nSignal duration: {}s\
        ".format(stop_time-start_time,util.duration))