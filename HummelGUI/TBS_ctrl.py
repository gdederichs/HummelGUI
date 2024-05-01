"""
Description
-----------
Module for the creation of TBS control signals

Author
------
Gregor Dederichs, EPFL School of Life Sciences
"""

import numpy as np
import util

def TBS_control(total_time = util.total_TBS_time,
         carrier_f = util.carrier_f,
         A1 = util.ampli1,
         A2 = util.ampli2,
         ramp_up_time = util.ramp_up_time,
         ramp_down_time = util.ramp_down_time,
         rampup = True):
    ''' 
    Description
    -----------
    Create control signal (high frequency, no shift)
    
    Parameters
    ----------
    total_time : int
        the time in seconds that the stimulation lasts (excluding ramp-up and ramp-down)

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
    dt = np.linspace(0,total_time, int(util.sampling_f*total_time))
    # ========== RAMP UP ==========
    if rampup:
        signals = util.ramp(direction="up", carrier_f=carrier_f, ramp_time=ramp_up_time, A1_max=A1, A2_max=A2)
    
    # ======== MAIN SIGNAL ========
    I1b = A1*np.cos(2*np.pi*carrier_f*dt)
    I2b = A2*np.cos(2*np.pi*carrier_f*dt+np.pi)
    if rampup:
        signals = np.concatenate((signals, np.vstack((I1b,I2b))), axis=1)
    else:
        signals = np.vstack((I1b,I2b))

    # ======== RAMP DOWN ========
    down = util.ramp(direction="down", carrier_f=carrier_f, ramp_time=ramp_down_time, A1_max=A1, A2_max=A2)
    signals = np.concatenate((signals,down),axis=1)

    # adjust dt to include ramps
    if rampup:
        dt = np.linspace(0,total_time+ramp_up_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_up_time+ramp_down_time)))
    else:
        dt = np.linspace(0,total_time+ramp_down_time, int(util.sampling_f*(total_time+ramp_down_time)))

    # add 100 zeros to offset spiking and update dt accordingly 
    signals = np.concatenate((signals, np.zeros((2,100))), axis=1)
    dt = np.concatenate((dt, dt[-1] + np.arange(0, 100) * dt[1]-dt[0]))

    return dt, signals