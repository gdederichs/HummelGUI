'''
Description
-----------
Base functions necessary to create more complex signals

Author
------
Gregor Dederichs, EPFL School of Life Sciences
'''
import os
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf
import util



# ========== BASE FUNCTIONS ==========
def get_subject_and_session_IDs(filename):
    """
     Description
     -----------
     Reads an excel file containing subject IDs and returns the corresponding list

     Parameters
     ----------
     filename : str
        name of the excel file in the same directory
    """
    parent_dir = os.getcwd()
    path = os.path.join(parent_dir,"HummelGUI", filename) 

    # check path
    if not os.path.exists(path):
        raise ValueError("File not found")
    else: # (if path exists)
        try:
            df = pd.read_excel(path)
            df = df
        except:
            raise ValueError("File not readable")
        
        subj_IDs = df["Subj"].to_list()
        subj_IDs.insert(0,"Select Subject ID")
        sess_IDs = df.columns.to_list()[1:]
        sess_IDs.insert(0, "Select Session ID")

        return subj_IDs,sess_IDs


def TBS(high_f = util.carrier_f,
             pulse_f = util.freq_of_pulse,
             burst_f = util.burst_freq,
             duration = util.train_stim_time,
             A1 = util.ampli1,
             A2 = util.ampli2):
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
    dt = np.linspace(0,duration,int(util.sampling_f*duration))
    f1 = high_f
    f2 = high_f + pulse_f

    # Pulse
    pulse_dt = np.linspace(0,pulse_t,int(util.sampling_f*pulse_t))
    I1 = A1*np.cos(2*np.pi*f1*pulse_dt)
    I2 = A2*np.cos(2*np.pi*f2*pulse_dt+np.pi)

    # Break
    break_dt = pulse_dt[-1] + np.linspace(1/util.sampling_f, cycle_t-pulse_t, int(util.sampling_f*(cycle_t-pulse_t)))
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
        carrier_f = util.carrier_f,
        ramp_time = util.ramp_up_time,
        A1_max=util.ampli1,
        A2_max=util.ampli2):
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
        dt = np.linspace(0,ramp_time,int(util.sampling_f*ramp_time))

        # envelope of linear change
        ramp1 = np.linspace(0,A1_max,int(util.sampling_f*ramp_time))
        ramp2 = np.linspace(0,A2_max,int(util.sampling_f*ramp_time))
        if direction=="down":
            ramp1 = ramp1[::-1]
            ramp2 = ramp2[::-1]
        elif direction != "up":
            raise ValueError("parameter 'direction' should be either 'up' or 'down' (case sensitive)")

        # scale signals according to envelope
        I1 = ramp1*np.cos(2*np.pi*carrier_f*dt)
        I2 = ramp2*np.cos(2*np.pi*carrier_f*dt+np.pi)

        return np.vstack((I1,I2))