import numpy as np

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
ampl = 2
freq = 3 #[Hz]
period = 1/freq
duration = 10 #[s]
sampling_rate = 1000
chunk_time = 1

# plot visuals/terminal outputs?
visuals = True
should_print  = True