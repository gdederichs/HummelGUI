import numpy as np
from matplotlib import pyplot as plt


def iTBS(total_time = 20,
        stim_time = 2,
        break_time = 8,
        plot = False):

    no_cycles = np.floor(total_time/(stim_time+break_time)-0.001)
    dt = np.linspace(0,total_time,int(sampling_f*total_time))

    #creating signals
    signals = createTI(duration=stim_time)
    signals = np.concatenate((signals, np.zeros((2,sampling_f*break_time))), axis=1)
    
    for i in np.arange(no_cycles):
        signals = np.concatenate((signals, createTI(duration=stim_time)), axis=1)
        if i!=no_cycles-1:
            signals = np.concatenate((signals, np.zeros((2,sampling_f*break_time))), axis=1)
        else: #last stim needs special care to correctly fit time
            dt_dim = np.size(dt)
            sig_dim = np.shape(signals)[1]
            # fill in remaining time
            if dt_dim-sig_dim>0:
                signals = np.concatenate((signals, np.zeros((2,dt_dim-sig_dim))), axis=1)
            # or increase time to allow end of signal
            else:
                dt = np.linspace(0, (sig_dim - 1) * (dt[1]-dt[0]), sig_dim)

    
    if plot:
        I1 = signals[0]
        I2 = signals[1]
        I = I1+I2
        plt.plot(dt,I)
        #plt.plot(dt,I1)
        #plt.plot(dt,I2)
        plt.show()

    return signals



def createTI(high_f = 2000,
             pulse_f = 100,
             duration = 2,
             A1 = 0.5,
             A2 = 0.5,
             plot = False):
    
    cycle_t = 0.2
    pulse_t = 0.03
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

    if plot:
        I1 = signals[0]
        I2 = signals[1]
        I = I1+I2
        plt.plot(dt,I)
        #plt.plot(dt,I1)
        #plt.plot(dt,I2)
        plt.show()

    return signals




def subdivide(dt, signal, chunk_time):
    ''' Seperate a signal into a sequence of multiple subsignals. In particular, this allows
        to write a signal to a DAQ while still being able to access access the execution 
        between subsignals.
        
        Parameters
        ----------
        dt : list or np.array
            the time points of the signal
            
        signal : list or np.array
            the values of the signal at each time point
            
        chunk_time : float
            duration of a single subdivision
            
        Returns
        -------
        tuple[list, list]
            the subdivided time points and the subdivided signal
    '''
    tot_duration = dt[-1]
    n_samples = np.size(dt)
    sampling_rate = n_samples/tot_duration

    #cut samples into chunks which last chunk_time
    samples_per_chunk = int(sampling_rate*chunk_time)
    subdivisions = [signal[i:i+samples_per_chunk] for i in np.arange(0,n_samples,samples_per_chunk)]
    dt_subdivision = [dt[i:i+samples_per_chunk] for i in np.arange(0,n_samples,samples_per_chunk)]
    
    return dt_subdivision, subdivisions


def fct1(A,f,t,sampling_rate):
    ''' Produces a simple sine wave
        
        Parameters
        ----------
        A : float
            amplitude
            
        f : float
            frequency
            
        t : float
            duration of the sine wave

        sampling_rate : float
            sampling_rate to produce time points

        Returns
        -------
        tuple[list, list]
            the time points and the signal
        '''
    dt=np.linspace(0,t,int(sampling_rate*t))
    signal = A*np.sin(2*np.pi*f*dt)
    return dt, signal


def single_period(A,t,sampling_rate):
    ''' Produces a single period of a sine wave
        
        Parameters
        ----------
        A : float
            amplitude
            
        t : float
            period

        sampling_rate : float
            sampling_rate to produce time points

        Returns
        -------
        tuple[list, list]
            the time points and the signal
        '''
    dt = np.linspace(0,t,int(sampling_rate*t))
    signal = A*np.sin(2*np.pi/t*dt)
    return dt, signal


def fct2(A,f,t,sampling_rate):
    ''' Produces a simple cosine wave
        
        Parameters
        ----------
        A : float
            amplitude
            
        f : float
            frequency
            
        t : float
            duration of the sine wave

        sampling_rate : float
            sampling_rate to produce time points

        Returns
        -------
        tuple[list, list]
            the time points and the signal
        '''
    dt=np.linspace(0,t,sampling_rate*t)
    signal = A*np.cos(2*np.pi*f*dt)
    return dt, signal


'''
Parameters for the main program
'''
#for iTBS
sampling_f = 100000 #matlab has dt = 0.01 (in ms); here: in 1/s = Hz

#general
ampl = 2
freq = 3 #[Hz]
period = 1/freq
duration = 5 #[s]
sampling_rate = 1000
chunk_time = 1

# plot visuals/terminal outputs?
visuals = True
should_print  = True