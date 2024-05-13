"""
Description
-----------
Module for the creation of TI signals

Author
------
Gregor Dederichs, EPFL School of Life Sciences
"""

import util
import fbase
import numpy as np

def TI(total_time = util.total_TBS_time,
         shift_f = util.freq_of_pulse,
         carrier_f = util.carrier_f,
         A1 = util.ampli1,
         A2 = util.ampli2,
         ramp_up_time = util.ramp_up_time,
         ramp_down_time = util.ramp_down_time,
         rampup = True):
    ''' 
    Description
    -----------
    Create a continuous Temporal Intereference (TI) signal
    
    Parameters
    ----------
    total_time : int
        the time in seconds that the stimulation lasts (excluding ramp-up and ramp-down)
        
    shift_f : int
        the frequency in Hz of the envelope (pulse) 

    carrier_f : int
        the frequency in Hz of the individual signals (ie. high frequency)

    A1 : float
        the amplitude in mA of signal 1

    A2 : float
        the amplitude in mA of signal 2

    ramp_up_time : int
        the time in seconds of amplitude increase of high frequency signals, before stimulation

    ramp_down_time : int
        the time in seconds of amplitude decrease of high frequency signals, after stimulation

    rampup : bool
        True if rampup is to be included (eg. False for updating signal during stimulation)

    Returns
    -------
    tuple[np.array, np.array]
        the time points and the signals (eg. signal 1 is signals[0])
    '''
    dt = np.linspace(0,total_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_down_time)))
    # ========== RAMP UP ==========
    if rampup:
        dt = np.linspace(0,total_time+ramp_up_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_up_time+ramp_down_time)))
        signals = fbase.ramp(direction="up", carrier_f=carrier_f, ramp_time=ramp_up_time, A1_max=A1, A2_max=A2)

    # ======== MAIN SIGNAL ========
    f1 = carrier_f
    f2 = f1 + shift_f

    main_dt = np.linspace(0,total_time,int(util.sampling_f*total_time))

    main_I1 = A1*np.cos(2*np.pi*f1*main_dt)
    main_I2 = A2*np.cos(2*np.pi*f2*main_dt+np.pi)

    main_sig = np.vstack((main_I1,main_I2))

    if rampup:
        #concatenate to ramp
        signals = np.concatenate((signals, main_sig), axis=1)
    else:
        #if no ramp, first_sig is the beginning of the signal
        signals = main_sig

    # ======== RAMP DOWN ========
    down = fbase.ramp(direction="down", carrier_f=carrier_f, ramp_time=ramp_down_time, A1_max=A1, A2_max=A2)
    signals = np.concatenate((signals,down),axis=1)

    # add 100 zeros to offset spiking and update dt accordingly 
    signals = np.concatenate((signals, np.zeros((2,100))), axis=1)
    dt = np.concatenate((dt, dt[-1] + np.arange(0, 100) * dt[1]-dt[0]))

    return dt, signals