import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import util

######## USB 6216 does not support hardware timing. Timing must be set via software loop ############

task = nidaqmx.Task()
task.ao_channels.add_ao_voltage_chan('SimDev/ao0')

#test function to be sent
dt, signal = util.fct1(A=2,f=1,t=11,sampling_rate=util.sampling_rate)

if util.visuals:
    plt.ion()
    fig, ax = plt.subplots()
    line, = ax.plot([],[])
    t_seq = []
    sig_seq = []


task.start()

start = time.time()
for idx,sample in enumerate(signal):
    task.write(sample)

    if util.visuals:
        t_seq.append(dt[idx])
        sig_seq.append(sample)
        line.set_xdata(t_seq)
        line.set_ydata(sig_seq)
        ax.relim()
        ax.autoscale_view()
        fig.canvas.draw()
        fig.canvas.flush_events()

    time.sleep(1/util.sampling_rate) ###### THIS DOES NOT WORK, accumulates delay on every loop (ex: 11s signal runs in 11.8s)
stop = time.time()
print(stop-start)

task.stop()
task.close()