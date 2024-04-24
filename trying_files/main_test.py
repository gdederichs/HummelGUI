import nidaqmx
import numpy as np
from matplotlib import pyplot as plt
import time
import HummelGUI.util as util


 #TO DO:     DONE - 1. function to subdivide signal into small portions
     #       DONE - 2. each subdivision is written to the DAQ
     #       DONE - 3. each subdivision should be in the order of seconds or shorter
     #       DONE - 4. in main loop, have request_update = true or false
     #       DONE - 5. if false, continue to write next sequences of the signal
     #       DONE - 6. if true, change from which "mother function" the subdivisions should be made
     #                 continue with those, thus upating the signal
     #       6b. find manner to update request_update while in run(), from an external button/trigger
     #       6c. get update mechanism to work with DAQ
     #       7. main loop should be stopped with a function request_stop() thus terminating the stimulation
     #       7b. refactor code into a class
     #       8. add second channel to write to




class UpdatableSignal:
    def __init__(self,ampl,freq,duration,sampling_rate,update_requested = False, bool_run = True) -> None:
        ''' An UpdatableSignal object handles the creation of a signal and its writing to a DAQ. 
            In particular, it handles the update requests to change the current signal being written 
            to the DAQ to a new signal. 
        
        Parameters
        ----------
        self : self
            self
            
        ampl : float
            amplitude of the signal
            
        freq : float
            frequency of the signal

        duration : float
            duration of the signal

        sampling_rate : float
            sampling rate at which the signal is constructed

        update_requested : bool
            indicates if an update of the signal is to be performed

        bool_run : bool
            indicates if the program should currently be run
        '''
        #signal
        self.ampl = ampl #2
        self.freq = freq #3 #[Hz]
        self.duration = duration #10 #[s]
        self.sasampling_rate = sampling_rate #100
        self.dt, self.signal = util.fct1(self.ampl, self.freq, self.duration, self.sasampling_rate)

        #updatable
        self.update_requested = update_requested
        self.bool_run = bool_run
        self.counter = 0

    
    def run(self, task):
        ''' Run the subdivision of an UpdatableSignal and write it to a DAQ. 
        
        Parameters
        ----------
        self : UpdatableSignal
            the UpdtableSignal object being run
            
        task : nidaqmx.Task()
            the DAQ task to be written to
            

        Notes
        -----
        Updates are checked between each subdivision.
        '''
        #produce subdivisions of signal
        dt_div, signal_div = util.subdivide(self.dt, self.signal, util.chunk_time)

        task.start()

        #For Visualisation only
        if util.visuals:
            previous_subdiv = [] 
            previous_dt_div = []
            plt.ion()
            fig, ax = plt.subplots()
            line, = ax.plot(previous_dt_div,previous_subdiv)

        #write all subdivisions to DAQ
        for idx, subdivision in enumerate(signal_div):

            if util.should_print:
                print("Subdivision {} with A={:.0f}".format(idx, np.max(subdivision)))

            #For Visualisation only
            if util.visuals:
                previous_dt_div.append(dt_div[idx])
                previous_subdiv.append(subdivision)
                line.set_xdata(previous_dt_div)
                line.set_ydata(previous_subdiv)
                ax.relim()
                ax.autoscale_view()
                fig.canvas.draw()
                fig.canvas.flush_events()


            #======= ARTIFICIAL UPDATE REQUEST FOR TESTS ===============
            if idx == 7 and self.counter == 2:
                self.update_requested = True
            #===========================================================

            # check for update request between each subdivision
            if self.update_requested:
                self.handle_update(task)
                break

            task.write(subdivision)
            

        
        task.stop()
        time.sleep(0.01)

    
    def handle_update(self,task):
        ''' Handles updates of a signal when an update is requested 
        
        Parameters
        ----------
        self : UpdatableSignal
            the UpdtableSignal object to be updated
            
        task : nidaqmx.Task()
            the DAQ task to write the update to
        '''
        #reset bool; handle task stop
        self.update_requested = False
        task.stop()

        #modify values of function parameters
        self.ampl += 2
        self.freq += 4
        self.duration = self.duration

        #compute new signal
        self.dt, self.signal = util.fct1(self.ampl, self.freq, self.duration, self.sasampling_rate)


def main():
    task = nidaqmx.Task()
    task.ao_channels.add_ao_voltage_chan("SimDev/ao0")
    task.timing.cfg_samp_clk_timing(rate=util.sampling_rate, sample_mode=nidaqmx.constants.AcquisitionType.CONTINUOUS) # ATTENTION: USB-6216 does not support hardware timing
                                                                                                                        # timing must be set via software loop

    signal_handler = UpdatableSignal(ampl=util.ampl, freq=util.freq, duration=util.duration, sampling_rate=util.sampling_rate)

    while signal_handler.bool_run:

        signal_handler.counter += 1
        if util.should_print:
            print("Signal",signal_handler.counter)

        signal_handler.run(task)

    task.close()

if __name__ == "__main__":
    main()