import util
import numpy as np

def cTBS(total_time = util.total_iTBS_time,
         pulse_f = util.freq_of_pulse,
         burst_f = util.burst_freq,
         carrier_f = util.carrier_f,
         A1 = util.ampli1,
         A2 = util.ampli2,
         ramp_up_time = util.ramp_up_time,
         ramp_down_time = util.ramp_down_time,
         rampup = True):
    
    dt = np.linspace(0,total_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_down_time)))
    # ========== RAMP UP ==========
    if rampup:
        dt = np.linspace(0,total_time+ramp_up_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_up_time+ramp_down_time)))
        signals = util.ramp(direction="up", carrier_f=carrier_f, ramp_time=ramp_up_time, A1_max=A1, A2_max=A2)

    # ======== MAIN SIGNAL ========
    sig = util.createTI(high_f=carrier_f,
                  pulse_f=pulse_f,
                  burst_f=burst_f,
                  duration=total_time,
                  A1=A1, A2=A2)
    if rampup:
        #concatenate to ramp
        signals = np.concatenate((signals, sig), axis=1)
    else:
        #if no ramp, first_sig is the beginning of the signal
        signals = sig

    # ======== RAMP DOWN ========
    down = util.ramp(direction="down", carrier_f=carrier_f, ramp_time=ramp_down_time, A1_max=A1, A2_max=A2)
    signals = np.concatenate((signals,down),axis=1)

    # add 100 zeros to offset spiking and update dt accordingly 
    signals = np.concatenate((signals, np.zeros((2,100))), axis=1)
    dt = np.concatenate((dt, dt[-1] + np.arange(0, 100) * dt[1]-dt[0]))

    #shifts 0 to beginning of stim if ramp is included
    if rampup:
        dt -= ramp_up_time 

    return dt, signals


"""
a,b = cTBS()
from matplotlib import pyplot as plt

fig, axs = plt.subplots(3)
axs[0].plot(a, b[0])
axs[1].plot(a, b[1])
axs[2].plot(a, b[0]+b[1])

plt.show()
"""