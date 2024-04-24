import numpy as np
from matplotlib import pyplot as plt
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf
import util

def iTBS(total_time = util.total_iTBS_time,
         stim_time = util.train_stim_time,
         break_time = util.train_break_time,
         pulse_f = util.freq_of_pulse,
         burst_f = util.burst_freq,
         carrier_f = util.carrier_f,
         A1 = util.ampli1,
         A2 = util.ampli2,
         ramp_up_time = util.ramp_up_time,
         ramp_down_time = util.ramp_down_time,
         rampup = True):

    no_cycles = np.floor(total_time/(stim_time+break_time)-0.001)
    dt = np.linspace(0,total_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_down_time)))
    break_dt = np.linspace(0, break_time, int(util.sampling_f*break_time))

    #creating signals
    # ========== RAMP UP ==========
    if rampup:
        dt = np.linspace(0,total_time+ramp_up_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_up_time+ramp_down_time)))
        signals = util.ramp(direction="up", carrier_f=carrier_f, ramp_time=ramp_up_time, A1_max=A1, A2_max=A2)

    # ======== MAIN SIGNAL ========
    first_sig = util.createTI(high_f=carrier_f,
                       pulse_f=pulse_f,
                       burst_f=burst_f,
                       duration=stim_time,
                       A1=A1,
                       A2=A2)
    if rampup:
        #concatenate to ramp
        signals = np.concatenate((signals, first_sig), axis=1)
    else:
        #if no ramp, first_sig is the beginning of the signal
        signals=first_sig

    I1b = A1*np.cos(2*np.pi*carrier_f*break_dt)
    I2b = A2*np.cos(2*np.pi*carrier_f*break_dt+np.pi)
    signals = np.concatenate((signals, np.vstack((I1b,I2b))), axis=1)
    
    for i in np.arange(no_cycles):
        new = util.createTI(high_f=carrier_f,
                       pulse_f=pulse_f,
                       burst_f=burst_f,
                       duration=stim_time,
                       A1=A1,
                       A2=A2)
        signals = np.concatenate((signals, new), axis=1)
        
        if i!=no_cycles-1:
            I1b = A1*np.cos(2*np.pi*carrier_f*break_dt)
            I2b = A2*np.cos(2*np.pi*carrier_f*break_dt+np.pi)
            signals = np.concatenate((signals, np.vstack((I1b,I2b))), axis=1)
        else: 
            #last stim needs special care to correctly fit time
            dt_dim = np.size(dt)-int(util.sampling_f*ramp_down_time)
            sig_dim = np.shape(signals)[1]
            # fill in remaining time
            if dt_dim-sig_dim>0:
                last_break_dt = np.arange(0, dt_dim-sig_dim) * (dt[1]-dt[0])
                I1b = A1*np.cos(2*np.pi*carrier_f*last_break_dt)
                I2b = A2*np.cos(2*np.pi*carrier_f*last_break_dt+np.pi)
                signals = np.concatenate((signals, np.vstack((I1b,I2b))), axis=1)
                
    # ========= RAMP DOWN =========
    down = util.ramp(direction="down", carrier_f=carrier_f, ramp_time=ramp_down_time, A1_max=A1, A2_max=A2)
    signals = np.concatenate((signals, down), axis=1)
    # add 100 zeros to offset spiking - update dt accordingly 
    signals = np.concatenate((signals, np.zeros((2,100))), axis=1)
    dt = np.concatenate((dt, dt[-1] + np.arange(0, 100) * dt[1]-dt[0]))
    if rampup:
        #shifts 0 to beginning of stim if ramp is included
        dt -= ramp_up_time 

    return dt, signals