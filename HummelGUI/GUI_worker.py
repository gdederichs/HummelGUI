import threading
import nidaqmx.constants
import numpy as np

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf
from nidaqmx.constants import Edge
from nidaqmx.constants import Slope

from PyQt6.QtCore import Qt

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
        self.exit_repetitions = False

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
            self.exit_repetitions = True
            self.parent.run_status.setText("Ramping Down")
            self.parent.run_status.setStyleSheet("color: orange; font-weight: bold;")
            self.parent.run_status.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.parent.save_params(directory=self.parent.save_edit.text())
        self.parent.send_signal()

    def run(self):
        """
        Description
        -----------
        Run and send signals to DAQ, as triggered by parent. 
        Runs the number of specified times (by parent = GUI).
        Each run is on a new Task
        """
        for rep_counter in range(self.parent.rep_num):

            # task handling/settings
            self.parent.task = nidaqmx.Task()
            self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao0")
            self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao1")
            self.parent.task.timing.cfg_samp_clk_timing(rate=util.sampling_f,sample_mode=AcquisitionType.FINITE,samps_per_chan=np.shape(self.parent.TBS_signals)[1])
            
            # add trigger to writing task
            if self.parent.use_trigger:
                self.parent.task.triggers.start_trigger.cfg_dig_edge_start_trig(trigger_source="/"+util.device+"/PFI0", trigger_edge=Edge.RISING)
                self.parent.task.triggers.start_trigger

            # save parameters of start of experiment to csv
            self.parent.save_params(directory=self.parent.save_edit.text())
            
            # handle button enabling/disabling while running
            self.parent.btn_update.setEnabled(True) 
            self.parent.btn_stop.setEnabled(True)
            self.parent.btn_create_signals.setEnabled(False) #once running, update() handles this

            # handle labels
            if not self.parent.use_trigger:
                self.parent.run_status.setText("Stimulation {} Ongoing".format(rep_counter))
                self.parent.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.parent.btn_create_signals.setEnabled(True)
            else:
                self.parent.run_status.setText("Stimulation {} Conditional on Trigger:\n  -'Active' LED ON: Stimulation Ongoing \n  -'Active' LED OFF: Waiting for Trigger".format(rep_counter))
                self.parent.run_status.setStyleSheet("color: blue; font-weight: bold;")
                self.parent.run_status.setAlignment(Qt.AlignmentFlag.AlignLeft)
                self.parent.btn_create_signals.setEnabled(True)

            # write signals to DAQ
            self.parent.send_signal()

            # task closing handling
            self.parent.task.wait_until_done(inf)
            self.parent.task.close()

            # handle button enabling/disabling after run
            self.parent.btn_update.setEnabled(False)
            self.parent.btn_stop.setEnabled(False)

            # triggered by parent's stop request
            if self.exit_repetitions:
                self.exit_repetitions = False
                break

        # reset status labels
        self.parent.running = False
        self.parent.run_status.setText("Ready")
        self.parent.run_status.setStyleSheet("color: green; font-weight: bold;")
        self.parent.run_status.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.parent.stim_selected() 