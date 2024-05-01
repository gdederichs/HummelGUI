import threading
import numpy as np

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf
from nidaqmx.constants import Edge

import util

class WorkerThread(threading.Thread):
    """
    Description
    -----------
    Worker thread works in parallel to GUI to execute long code, such as running or updating tasks
    """
    def __init__(self, parent):
        super().__init__()
        self.parent = parent #access to main window's attributes/functions

    def update(self):
        """
        Description
        -----------
        Run the update triggered by parent. Notably resets request values and sends new signal to DAQ
        """
        #reset requests
        if self.parent.update_request == True:
            self.parent.update_request = False
        if self.parent.stop_request == True:
            self.parent.stop_request = False
            self.parent.run_status.setText("Ramping Down")
            self.parent.run_status.setStyleSheet("color: orange; font-weight: bold;")
        self.parent.save_params(directory=self.parent.save_edit.text())
        self.parent.send_signal()

    def run(self):
        """
        Description
        -----------
        Run and send signals to DAQ, as triggered by parent.
        """
        if util.trigger: #TO BE REPLACED WITH GUI CHECKBOX
            self.parent.run_status.setText("Waiting for Trigger")
            self.parent.run_status.setStyleSheet("color: blue; font-weight: bold;")

            # trigger settings
            print("DEBUG - settings")
            self.parent.trigger_task = nidaqmx.Task()
            self.parent.trigger_task.ai_channels.add_ai_voltage_chan(util.device+"/ai0")
            self.parent.trigger_task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=1) # ! NOT SURE ABOUT PARAMS
            self.parent.trigger_task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source=util.device+"/ai0", trigger_edge=Edge.RISING)

            # wait for trigger
            print("DEBUG - WAIT")
            self.parent.trigger_task.start()
            print("DEBUG - PASS 1")
            self.parent.trigger_task.wait_until_done()
            print("DEBUG - PASS 2")

        print("DEBUG - outside")
        # save parameters of start of experiment to csv
        self.parent.save_params(directory=self.parent.save_edit.text())

        # change status labels for GUI
        self.parent.run_status.setText("Stimulation Ongoing")
        self.parent.run_status.setStyleSheet("color: red; font-weight: bold;")

        # handle button enabling/disabling while running
        self.parent.btn_update.setEnabled(True) 
        self.parent.btn_stop.setEnabled(True)
        self.parent.btn_create_signals.setEnabled(False) #once running, update() handles this

        # task handling/settings
        self.parent.task = nidaqmx.Task()
        self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao0")
        self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao1")
        self.parent.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.parent.TBS_signals)[1])

        # write signals to DAQ
        self.parent.send_signal()

        # task closing handling
        self.parent.task.wait_until_done(inf)
        self.parent.task.close()
        self.parent.running = False

        # handle button enabling/disabling after run
        self.parent.btn_update.setEnabled(False)
        self.parent.btn_stop.setEnabled(False)

        # reset status labels
        self.parent.run_status.setText("Ready")
        self.parent.run_status.setStyleSheet("color: green; font-weight: bold;")
        self.parent.stim_selected() 