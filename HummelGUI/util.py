'''
Description
-----------
Deafult parameters for the main user interface

Author
------
Gregor Dederichs, EPFL School of Life Sciences
'''
# Defaults for reading EXCEL FILE
excel_file_name = "book1.xlsx" #FILE MUST BE IN GUI DIRECTORY

# Defaults for GUI
default_mode = "Settings" #should be "Blind" or "Settings"

# Defaults for DAQ
device = "Dev4"

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
rep_num = 3