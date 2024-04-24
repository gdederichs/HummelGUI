import time
import os
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (QLineEdit,
                            QLabel,
                            QWidget,
                            QPushButton,
                            QCheckBox,
                            QGridLayout,
                            QComboBox)
import pyqtgraph as pg

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf

import numpy as np
import util
import iTBS
import cTBS
import threading

class MainWindow(QWidget):
    """
    Description
    -----------
    Main GUI window. Handles all events linked to the GUI, notably storing all parameters and functions necessary to run
    """
    def __init__(self, *args, **kwargs):
        """
        Description
        -----------
        Initialise main window of the GUI.
        The main GUI window handles all events linked to the GUI, 
        notably storing all parameters and functions necessary for NIBS
        """
        super().__init__(*args, **kwargs)

        # Visual settings
        self.setWindowTitle('iTBS Interface')
        self.resize(800,0)
        self.layout = QGridLayout()

        # State settings
        self.update_request = False
        self.stop_request = False
        self.running = False

        # ======== DROP DOWN FIELDS ========
        # choose stim type
        self.drop_stim_select = QComboBox()
        self.drop_stim_select.addItems(["Select Stimulation","iTBS","cTBS"])
        self.drop_stim_select.currentTextChanged.connect(self.stim_selected)
        self.layout.addWidget(self.drop_stim_select,8,0)


        # ======== VALUE FIELDS ========
        # total stimulation time
        self.layout.addWidget(QLabel('Total Duration (seconds):'), 0, 0)
        self.total_iTBS_time_edit = QLineEdit(str(util.total_iTBS_time))
        self.layout.addWidget(self.total_iTBS_time_edit,0,1)

        # time of stimulation in one cycle (train)
        self.layout.addWidget(QLabel('Ramp-up Time (seconds):'), 1, 0)
        self.ramp_up_time_edit = QLineEdit(str(util.ramp_up_time))
        self.layout.addWidget(self.ramp_up_time_edit,1,1)

        # time of break in on cycle (train)
        self.layout.addWidget(QLabel('Ramp-down Time (seconds):'), 2, 0)
        self.ramp_down_time_edit = QLineEdit(str(util.ramp_down_time))
        self.layout.addWidget(self.ramp_down_time_edit,2,1)

        # pulse frequency
        self.layout.addWidget(QLabel('Pulse Frequency (Hz):'), 3, 0)
        self.freq_of_pulse_edit = QLineEdit(str(util.freq_of_pulse))
        self.layout.addWidget(self.freq_of_pulse_edit,3,1)

        # cycle frequency
        self.layout.addWidget(QLabel('Burst Frequency (Hz):'), 4, 0)
        self.burst_freq_edit = QLineEdit(str(util.burst_freq))
        self.layout.addWidget(self.burst_freq_edit,4,1)

        # carrier frequency
        self.layout.addWidget(QLabel('Carrier Frequency (Hz):'), 5, 0)
        self.carrier_f_edit = QLineEdit(str(util.carrier_f))
        self.layout.addWidget(self.carrier_f_edit,5,1)

        # sum of amplitudes
        self.layout.addWidget(QLabel('Amplitude Sum (mA):'), 6, 0)
        self.A_sum_edit = QLineEdit(str(util.A_sum))
        self.layout.addWidget(self.A_sum_edit,6,1)

        # ratio of amplitudes
        self.layout.addWidget(QLabel('Amplitude Ratio (A1/A2):'), 7, 0)
        self.A_ratio_edit = QLineEdit(str(util.A_ratio))
        self.layout.addWidget(self.A_ratio_edit,7,1)


        # ======== BUTTON FIELDS ========
        # reset (default set in util.py)
        self.btn_reset_defaults = QPushButton("Reset to Default Values")
        self.btn_reset_defaults.clicked.connect(self.reset_defaults)
        self.layout.addWidget(self.btn_reset_defaults,8,1)

        # create signals/waveforms
        self.btn_create_signals = QPushButton("Create Waveform")
        self.btn_create_signals.setEnabled(False)
        self.btn_create_signals.clicked.connect(lambda: self.create_signals(rampup=True))
        self.btn_create_signals.clicked.connect(lambda: self.graph_waveform())
        self.btn_create_signals.clicked.connect(lambda: self.btn_run_stimulation.setEnabled(True)) #enable run button
        self.layout.addWidget(self.btn_create_signals,9,0,1,2)

        # run stimulation
        self.btn_run_stimulation = QPushButton("Run Stimulation")
        self.btn_run_stimulation.setEnabled(False)  #can't run unless signal is created
        self.btn_run_stimulation.clicked.connect(lambda: self.btn_run_stimulation.setEnabled(False))# disable button after run; forces to recreate signal before running
        self.btn_run_stimulation.clicked.connect(self.run_stimulation)
        self.layout.addWidget(self.btn_run_stimulation,10,0,1,2)

        # update stimulation
        self.btn_update = QPushButton("Update Stimulation")
        self.btn_update.setEnabled(False) #can't update unless running
        self.btn_update.clicked.connect(self.request_update)
        self.layout.addWidget(self.btn_update,11,0)

        # stop stimulation
        self.btn_stop = QPushButton("Stop Stimulation")
        self.btn_stop.setEnabled(False) #can't stop unless running
        self.btn_stop.clicked.connect(self.request_stop)
        self.layout.addWidget(self.btn_stop,11,1)


        # ======== BLIND MODE ========
        # blind mode toggle
        self.blind_mode = QCheckBox('Blind Mode')
        self.layout.addWidget(self.blind_mode,12,1)
        self.blind_mode.stateChanged.connect(self.toggle_mode)

        # subject 
        self.label_subject = QLabel('Subject:')
        self.layout.addWidget(self.label_subject, 0, 0)
        self.subject_edit = QLineEdit("")
        self.subject_edit.setPlaceholderText("Subject ID")
        self.layout.addWidget(self.subject_edit,0,1)
        self.label_subject.hide()
        self.subject_edit.hide()

        # session
        self.label_session = QLabel('Session:')
        self.layout.addWidget(self.label_session, 1, 0)
        self.session_edit = QLineEdit("")
        self.session_edit.setPlaceholderText("Session ID")
        self.layout.addWidget(self.session_edit,1,1)
        self.label_session.hide()
        self.session_edit.hide()

        # file name storing data for stimulation
        self.label_file = QLabel('File storing data for stimulation:')
        self.layout.addWidget(self.label_file, 2, 0)
        self.file_edit = QLineEdit("")
        self.file_edit.setPlaceholderText("your\\file\\path\\here\\for\\stim\\data.xlxs")
        self.layout.addWidget(self.file_edit,2,1)
        self.label_file.hide()
        self.file_edit.hide()

        # choose save params or not
        self.box_save = QCheckBox('Save Parameters')
        self.layout.addWidget(self.box_save,13,1)       


        # ======== GRAPH FIELDS ========
        self.dt = [0,1]
        self.TBS_signals = np.zeros((2,2))
        self.plot_waveform = pg.PlotWidget()
        self.plot_waveform.getAxis("bottom").setLabel("Time", units="s")
        self.plot_waveform.getAxis("left").setLabel("Amplitude", units="mA")
        self.plot_waveform.plot(self.dt, self.TBS_signals[0]+self.TBS_signals[1])
        self.layout.addWidget(self.plot_waveform,0,2,14,1)


        # ======== LABEL FIELDS ========
        self.run_status = QLabel("Select Stimulation")
        self.run_status.setStyleSheet("color: orange; font-weight: bold;")
        self.layout.addWidget(self.run_status, 12, 0)


        # ======== APPLY LAYOUT ========
        self.setLayout(self.layout)
        self.show()
        # choose which window to open on start
        if util.default_mode=="Blind":
            self.blind_mode.setCheckState(Qt.CheckState.Checked)



    # FUNCTIONS
    def assign_values(self):
        """
        Description
        -----------
        Read values from GUI fields and store them
        """
        self.total_iTBS_time = int(self.total_iTBS_time_edit.text())
        self.train_stim_time = util.train_stim_time
        self.train_break_time = util.train_break_time
        self.freq_of_pulse = int(self.freq_of_pulse_edit.text())
        self.burst_freq = int(self.burst_freq_edit.text())
        self.carrier_f = int(self.carrier_f_edit.text())
        self.A_sum = float(self.A_sum_edit.text())
        self.A_ratio = float(self.A_ratio_edit.text())
        self.A1 = self.A_sum/(1+self.A_ratio)
        self.A2 = self.A_ratio*self.A_sum/(1+self.A_ratio)
        self.ramp_up_time = float(self.ramp_up_time_edit.text())
        self.ramp_down_time = float(self.ramp_down_time_edit.text())

    def create_signals(self, rampup=True):
        """
        Description
        -----------
        Creates signals from GUI values (calls assign_values() before running)
        and selected stimulation type, and stores signals
        """
        self.assign_values()

        if self.drop_stim_select.currentText() == "iTBS":
            self.dt, self.TBS_signals = iTBS.iTBS(self.total_iTBS_time,
                                        self.train_stim_time,
                                        self.train_break_time,
                                        self.freq_of_pulse,
                                        self.burst_freq,
                                        self.carrier_f,
                                        self.A1, self.A2,
                                        self.ramp_up_time,
                                        self.ramp_down_time,
                                        rampup=rampup)
            
        elif self.drop_stim_select.currentText() == "cTBS":
            self.dt, self.TBS_signals = cTBS.cTBS(self.total_iTBS_time,
                                        self.freq_of_pulse,
                                        self.burst_freq,
                                        self.carrier_f,
                                        self.A1, self.A2,
                                        self.ramp_up_time,
                                        self.ramp_down_time,
                                        rampup=rampup)
            
            
        
    def create_stop_signal(self):
        """
        Description
        -----------
        Creates a ramp down signal with null envelope
        """
        #named TBS_signals for code, 
        #but is simply high f signals,
        #with decreasing amplitude and null envelope
        self.TBS_signals = util.ramp(direction="down",
                                 carrier_f=self.carrier_f,
                                 ramp_time=self.ramp_down_time,
                                 A1_max=self.A1,
                                 A2_max=self.A2)
        
        
    def graph_waveform(self, lines=True):
        """
        Description
        -----------
        Plot the sum of signals stored in GUI and shows the result in a widget
        """
        #only run if mode is not blind
        if self.blind_mode.checkState() == Qt.CheckState.Unchecked:
            self.plot_waveform = pg.PlotWidget()
            self.plot_waveform.plotItem.setMouseEnabled(y=False) # Only allow zoom in X-axis
            self.plot_waveform.plot(self.dt,self.TBS_signals[0]+self.TBS_signals[1],)
            self.plot_waveform.getAxis("bottom").setLabel("Time", units="s")
            self.plot_waveform.getAxis("left").setLabel("Amplitude", units="mA")

            #plot lines surrounding main signal (exclude ramps)
            if lines:
                self.ramp_up_line = pg.InfiniteLine(pos=0, angle=90, movable=False)
                self.ramp_down_line = pg.InfiniteLine(pos=self.total_iTBS_time, angle=90, movable=False)
                self.plot_waveform.addItem(self.ramp_up_line)
                self.plot_waveform.addItem(self.ramp_down_line)

            self.layout.addWidget(self.plot_waveform,0,2,14,1)

        
    def reset_defaults(self):
        """
        Description
        -----------
        Reset all GUI fields to default values of util.py
        """
        self.total_iTBS_time_edit.setText(str(util.total_iTBS_time))
        self.ramp_up_time_edit.setText(str(util.ramp_up_time))
        self.ramp_down_time_edit.setText(str(util.ramp_down_time))
        self.freq_of_pulse_edit.setText(str(util.freq_of_pulse))
        self.burst_freq_edit.setText(str(util.burst_freq))
        self.carrier_f_edit.setText(str(util.carrier_f))
        self.A_sum_edit.setText(str(util.A_sum))
        self.A_ratio_edit.setText(str(util.A_ratio))


    def run_stimulation(self):
        """
        Description
        -----------
        Triggers the start of the stimulation by starting worker thread
        """
        self.worker_thread = WorkerThread(self)
        self.worker_thread.start()


    def send_signal(self):
        """
        Description
        -----------
        Sends signal to DAQ, usually called by worker thread to avoid GUI freezing
        """
        self.task.write(self.TBS_signals)
        self.task.start()
        self.running = True
        # continuously checks for update or stop request while task is running
        while not self.task.is_task_done():
            if self.update_request:
                # create new waveform without ramp-up
                self.task.stop()
                self.create_signals(rampup=False)
                self.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.TBS_signals)[1])
                self.worker_thread.update()
            if self.stop_request:
                # new waveform is ramp-down
                self.task.stop()
                self.create_stop_signal()
                self.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.TBS_signals)[1])
                self.worker_thread.update()
            


    def stim_selected(self):
        """
        Description
        -----------
        Updates label when stim is selected
        """
        if not self.running:
            if self.drop_stim_select.currentText()=="iTBS" or self.drop_stim_select.currentText()=="cTBS":
                self.run_status.setText("Ready")
                self.run_status.setStyleSheet("color: green; font-weight: bold;")
                self.btn_create_signals.setEnabled(True)
            else:
                print("debug")
                self.run_status.setText("Select Stimulation")
                self.run_status.setStyleSheet("color: orange; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)

    
    def request_update(self):
        """
        Description
        -----------
        Changes the update request to True
        """
        self.update_request = True


    def request_stop(self):
        """
        Description
        -----------
        Changes the stop request to True
        """
        self.stop_request = True


    def toggle_mode(self):
        """
        Description
        -----------
        Toggles GUI widgets between Blind mode and Testing mode
        """
        #turn on blind mode
        if self.blind_mode.checkState() == Qt.CheckState.Checked:
            for widget in self.findChildren(QWidget):
                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.drop_stim_select and
                    widget != self.btn_run_stimulation and
                    widget != self.btn_create_signals and
                    widget != self.btn_update and
                    widget != self.run_status and
                    widget != self.btn_stop
                    ): 
                    widget.setVisible(not widget.isVisible())
                # widgets present in blind mode only
                if (widget == self.box_save):
                    widget.setVisible(True)

        #back to testing mode
        if self.blind_mode.checkState() == Qt.CheckState.Unchecked:
            for widget in self.findChildren(QWidget):
                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.drop_stim_select and
                    widget != self.btn_run_stimulation and
                    widget != self.btn_create_signals and
                    widget != self.btn_update and
                    widget != self.run_status and
                    widget != self.btn_stop
                    ): 
                    widget.setVisible(not widget.isVisible())
                # widgets present in blind mode only
                if (widget == self.box_save):
                    widget.setVisible(False)

            # recall graphing to show signals in Testing mode        
            self.assign_values()
            self.graph_waveform(lines=False)
        
        # handling view toggle of ComboBox
        for drops in self.drop_stim_select.findChildren(QWidget):
            drops.setVisible(True)
        self.drop_stim_select.hidePopup()


    def save_params(self, file_name):
        """
        Description
        -----------
        Handles saving of parameters to a CSV file at the end of a stimulation.
        A directory called "parameter_history" is created in the working directory.
        The file is created inside "parameter_history".
        If the file already exists in "parameter_history", new data are appended to the end of the existing file, without overwriting.

        Parameters
        ----------
        file_name : string
            name of the file to save data
        """
        #only save if box is checked
        if self.box_save.checkState() == Qt.CheckState.Checked:
            directory = "parameter_history"
            parent_dir = os.getcwd()
            path = os.path.join(parent_dir, directory) 

            if not os.path.exists(path):
                os.makedirs(path)

            file_name = os.path.join(path, file_name) 
            with open(file_name, 'a', newline='') as file:
                file.write("\ntime,"+str(time.ctime(time.time())))
                file.write("\n"+self.subject_edit.text()+','+self.session_edit.text())
                file.write("\ntotal_time,"+str(self.total_iTBS_time))
                file.write("\ntrain_stim_time,"+str(self.train_stim_time))
                file.write("\ntrain_break_time,"+str(self.train_break_time))
                file.write("\npulse_freq,"+str(self.freq_of_pulse))
                file.write("\nburst_freq,"+str(self.burst_freq))
                file.write("\ncarrier_freq,"+str(self.carrier_f))
                file.write("\nampl_sum,"+str(self.A_sum))
                file.write("\nampl_ratio,"+str(self.A_ratio))
                file.write("\nampl1,"+str(self.A1))
                file.write("\nampl2,"+str(self.A2))
                file.write("\nramp_up_time,"+str(self.ramp_up_time))
                file.write("\nramp_down_time,"+str(self.ramp_down_time))
                file.write("\n")




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

        self.parent.send_signal()

    def run(self):
        """
        Description
        -----------
        Run and send signals to DAQ, as triggered by parent.
        """
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

        # save parameters of experiment to csv
        self.parent.save_params(util.save_filename)


            

"""
CURRENT ISSUES:
-with stop: works in both multi_channel_test.py and GUI, but ONLY IF stim is in break (outputting zeros).
            else: spikes as usual
-update works at any time --> for stop, update to null function, for 2/3 seconds and then call stop
-next:  -put correct value fields in GUI/clean GUI, with more headers, information etc/compare with MATLAB GUI and build towards that
        -make GUI nicer looking
        -add drop down menu to choose waveform?
        -with trigger?

-next:  DONE - 1) Rename cycle durations to train durations
        DONE - 2) Rename cycle freq to burst freq
        DONE - 3) Amplitudes should be defined by sum and ratio
        DONE - 4) Default amplitudes are 2 (sum is 4)
        DONE - 5) Add axis titles to graphing
        DONE - 6) Add ramp ups and ramp downs (No shift in carrier freqs, Amplitude gradually increase)
        DONE - 6b) Between trains: no shift in high stim, not simply 0
        DONE - 6c) Add ramp params to GUI, and add lines on graph after rampup and befor rampdown (for visu)
        DONE - 7) Add stop function with better functionality (update to ramp down)
        DONE - 7b) When calling update, do not want ramp up (keep ramp down, as it is needed for stim termination)
        8) Add menu to choose stimulation type
        DONE - 9) Save file with all parameters used after stimulation
        STARTED - 10) Add blind mode
                ->need to add reading from excel data if exp mode.
                    ->which data are stored in excel file?
        11) Trigger
"""