'''
Description
-----------
Deafult parameters for the main user interface

Author
------
Gregor Dederichs, EPFL School of Life Sciences
'''

import numpy as np
from matplotlib import pyplot as plt
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf


# Defaults for GUI
default_mode = "Settings" #should be "Blind" or "Settings"

# Defaults for DAQ
device = "SimDev6341"
trigger = True

# Defaults for iTBS (units: seconds and Hz)
total_TBS_time = 20 #time of entire signal
train_stim_time = 2 #time of stim within train
train_break_time = 8 #break time within train
carrier_f = 2000 #high frequency signals
sampling_f = 100000 #matlab has dt = 0.01ms
freq_of_pulse = 100 #frequency of envelope
burst_freq = 5 #frequency of theta-bursts
A_sum = 4 #sum of amplitudes
A_ratio = 1 #ratio of amplitudes
ampli1 = A_sum/(1+A_ratio) #amplitude of signal 1
ampli2 = A_ratio*A_sum/(1+A_ratio) #amplitude of signal 2
ramp_up_time = 5 #in s; high freq stim with no shift (no pulse), ramping aplitude
ramp_down_time = 5 #in s

# Defaults for saving
save_filename = "stimulations_data.csv"


# Base Functions
def createTI(high_f = carrier_f,
             pulse_f = freq_of_pulse,
             burst_f = burst_freq,
             duration = train_stim_time,
             A1 = ampli1,
             A2 = ampli2):
    """
    Description
    -----------
    Creats two signals for creating theta-bursts when summed
    
    Parameters
    ----------
    high_f : int
        base high frequency of the signals

    pulse_f : int
        the frequency in Hz of interference envelope

    burst_f : int
        the frequency in Hz at which theta-bursts (3 pulses) occur 

    duration: int
        the time in seconds of the signals

    A1 : float
        amplitude in mA of signal 1

    A2 : float
        amplitude in mA of signal 2

    """
    cycle_t = 1/burst_f #related to cycle frequency
    pulse_t = 3/pulse_f 
    no_pulses = int(duration/cycle_t)
    dt = np.linspace(0,duration,int(sampling_f*duration))
    f1 = high_f
    f2 = high_f + pulse_f

    # Pulse
    pulse_dt = np.linspace(0,pulse_t,int(sampling_f*pulse_t))
    I1 = A1*np.cos(2*np.pi*f1*pulse_dt)
    I2 = A2*np.cos(2*np.pi*f2*pulse_dt+np.pi)

    # Break
    break_dt = pulse_dt[-1] + np.linspace(1/sampling_f, cycle_t-pulse_t, int(sampling_f*(cycle_t-pulse_t)))
    I1b = A1*np.cos(2*np.pi*f1*break_dt)
    I2b = A2*np.cos(2*np.pi*f1*break_dt+np.pi) #with freq f1: no change

    # One cycle
    I1 = np.concatenate((I1, I1b))
    I2 = np.concatenate((I2, I2b))
    signals = np.vstack((I1,I2))

    # Complete signal
    signals = np.tile(signals, no_pulses)


    return signals



def ramp(direction = "up",
        carrier_f = carrier_f,
        ramp_time = ramp_up_time,
        A1_max=ampli1,
        A2_max=ampli2):
        """
        Description
        -----------
        Creates signals with no temporal interference, with linearly increasing/decreasing amplitudes (eg. notably used to start and finish stimulations)
        
        Parameters
        ----------
        direction : string
            either "up" or "down", indicating the direction of the ramping (0 to Amplitude vs. Amplitude to 0)

        carrier_f : int
            the high frequency of signals

        ramp_time : int
            the time in seconds of the linear change in amplitude

        A1 : float
            the maximum amplitude of signal 1 in mA reached at the end of the ramp

        A2 : float
            the maximum amplitude of signal 2 in mA reached at the end of the ramp
        """
        # time space
        dt = np.linspace(0,ramp_time,int(sampling_f*ramp_time))

        # envelope of linear change
        ramp1 = np.linspace(0,A1_max,int(sampling_f*ramp_time))
        ramp2 = np.linspace(0,A2_max,int(sampling_f*ramp_time))
        if direction=="down":
            ramp1 = ramp1[::-1]
            ramp2 = ramp2[::-1]
        elif direction != "up":
            raise ValueError("parameter 'direction' should be either 'up' or 'down' (case sensitive)")

        # scale signals according to envelope
        I1 = ramp1*np.cos(2*np.pi*carrier_f*dt)
        I2 = ramp2*np.cos(2*np.pi*carrier_f*dt+np.pi)

        return np.vstack((I1,I2))