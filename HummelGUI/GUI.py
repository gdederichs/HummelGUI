"""
Description
-----------
Module supporting the entire graphical user interface for TBS

Author
------
Gregor Dederichs, EPFL School of Life Sciences
"""

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

from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf

import numpy as np
import pandas as pd

import util
import iTBS
import cTBS
import TBS_ctrl
import GUI_worker


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
        Initialise main window of the GUI and sets its layout
        The main GUI window handles all events linked to the GUI, 
        notably storing all parameters and functions necessary for TI
        """
        super().__init__(*args, **kwargs)

        # Visual settings
        self.setWindowTitle('TI Interface')
        self.resize(800,500)
        self.showFullScreen()
        self.layout = QGridLayout()
        
        # State settings
        self.update_request = False
        self.stop_request = False
        self.running = False

        # ======== DROP DOWN FIELDS ========
        # label
        self.select_stim_label = QLabel("Stimulation Type")
        self.select_stim_label.setStyleSheet("color: black; font-weight: bold; font-size: 14pt;")
        self.layout.addWidget(self.select_stim_label, 0, 0)
        # choose stim type
        self.drop_stim_select = QComboBox()
        self.drop_stim_select.addItems(["Select Stimulation","iTBS","cTBS","TBS_control"])
        self.drop_stim_select.currentTextChanged.connect(self.stim_selected)
        self.layout.addWidget(self.drop_stim_select,1,0)

        # settings mode label
        self.settings_label = QLabel("Settings\nMode")
        self.settings_label.setStyleSheet("color: white; font-weight: bold; font-size: 75pt;")
        self.settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.settings_label,2,0,1,2)

        # ======== VALUE FIELDS ========
        # labels
        self.parameter_label = QLabel("Stimulation Parameters")
        self.parameter_label.setStyleSheet("color: black; font-weight: bold; font-size: 14pt;")
        self.layout.addWidget(self.parameter_label,3,0)

        # time label
        self.time_label = QLabel("Duration Parameters")
        self.time_label.setStyleSheet("color: black; font-weight: bold;")
        self.layout.addWidget(self.time_label,4,0)

        # total stimulation time
        self.layout.addWidget(QLabel('Total Duration (seconds):'), 5, 0)
        self.total_TBS_time_edit = QLineEdit(str(util.total_TBS_time))
        self.layout.addWidget(self.total_TBS_time_edit,5,1)

        # time of stimulation in one cycle (train)
        self.layout.addWidget(QLabel('Ramp-up Time (seconds):'), 6, 0)
        self.ramp_up_time_edit = QLineEdit(str(util.ramp_up_time))
        self.layout.addWidget(self.ramp_up_time_edit,6,1)

        # time of break in on cycle (train)
        self.layout.addWidget(QLabel('Ramp-down Time (seconds):'), 7, 0)
        self.ramp_down_time_edit = QLineEdit(str(util.ramp_down_time))
        self.layout.addWidget(self.ramp_down_time_edit,7,1)

        # time label
        self.freq_label = QLabel("Frequency Parameters")
        self.freq_label.setStyleSheet("color: black; font-weight: bold;")
        self.layout.addWidget(self.freq_label,8,0)

        # pulse frequency
        self.layout.addWidget(QLabel('Pulse Frequency (Hz):'), 9, 0)
        self.freq_of_pulse_edit = QLineEdit(str(util.freq_of_pulse))
        self.layout.addWidget(self.freq_of_pulse_edit,9,1)

        # cycle frequency
        self.layout.addWidget(QLabel('Burst Frequency (Hz):'), 10, 0)
        self.burst_freq_edit = QLineEdit(str(util.burst_freq))
        self.layout.addWidget(self.burst_freq_edit,10,1)

        # carrier frequency
        self.layout.addWidget(QLabel('Carrier Frequency (Hz):'), 11, 0)
        self.carrier_f_edit = QLineEdit(str(util.carrier_f))
        self.layout.addWidget(self.carrier_f_edit,11,1)

        # current label
        self.currents_label = QLabel("Current Parameters")
        self.currents_label.setStyleSheet("color: black; font-weight: bold;")
        self.layout.addWidget(self.currents_label,12,0)

        # sum of amplitudes
        self.layout.addWidget(QLabel('Amplitude Sum (mA):'), 13, 0)
        self.A_sum_edit = QLineEdit(str(util.A_sum))
        self.layout.addWidget(self.A_sum_edit,13,1)

        # ratio of amplitudes
        self.layout.addWidget(QLabel('Amplitude Ratio (A1/A2):'), 14, 0)
        self.A_ratio_edit = QLineEdit(str(util.A_ratio))
        self.layout.addWidget(self.A_ratio_edit,14,1)


        # ======== BUTTON FIELDS ========
        # reset (default set in util.py)
        self.btn_reset_defaults = QPushButton("Reset to Default Values")
        self.btn_reset_defaults.clicked.connect(self.reset_defaults)
        self.layout.addWidget(self.btn_reset_defaults,16,1)

        # create signals/waveforms
        self.btn_create_signals = QPushButton("Create Waveform")
        self.btn_create_signals.setEnabled(False)
        self.btn_create_signals.clicked.connect(lambda: self.create_signals(rampup=True))
        self.btn_create_signals.clicked.connect(lambda: self.graph_waveform())
        self.btn_create_signals.clicked.connect(lambda: self.btn_run_stimulation.setEnabled(True)) #enable run button
        self.layout.addWidget(self.btn_create_signals,1,2,1,2)

        # run stimulation
        self.btn_run_stimulation = QPushButton("Run Stimulation")
        self.btn_run_stimulation.setEnabled(False)  #can't run unless signal is created
        self.btn_run_stimulation.clicked.connect(lambda: self.btn_run_stimulation.setEnabled(False))# disable button after run; forces to recreate signal before running
        self.btn_run_stimulation.clicked.connect(self.run_stimulation)
        self.layout.addWidget(self.btn_run_stimulation,12,2,1,2)

        # update stimulation
        self.btn_update = QPushButton("Update Stimulation")
        self.btn_update.setEnabled(False) #can't update unless running
        self.btn_update.clicked.connect(self.request_update)
        self.layout.addWidget(self.btn_update,13,2)

        # stop stimulation
        self.btn_stop = QPushButton("Stop Stimulation")
        self.btn_stop.setEnabled(False) #can't stop unless running
        self.btn_stop.clicked.connect(self.request_stop)
        self.layout.addWidget(self.btn_stop,13,3)

        # trigger toggle
        self.trigger_toggle = QCheckBox('Trigger')
        self.layout.addWidget(self.trigger_toggle,14,2,alignment=Qt.AlignmentFlag.AlignRight)
        self.trigger_toggle.stateChanged.connect(self.toggle_trigger)
        self.trigger_toggle.setCheckState(Qt.CheckState.Checked) #by default wait for trigger


        # ======== BLIND MODE ========
        # blind mode toggle
        self.blind_mode = QCheckBox('Blind Mode')
        self.layout.addWidget(self.blind_mode,0,1)
        self.blind_mode.stateChanged.connect(self.toggle_mode)

        # blind mode label
        self.blind_label = QLabel("Blind Mode")
        self.blind_label.setStyleSheet("color: white; font-weight: bold; font-size: 100pt;")
        self.blind_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.blind_label,7,0,5,4)
        self.blind_label.hide()

        # get session button
        self.btn_session = QPushButton("Get Stimulation from file")
        self.btn_session.clicked.connect(lambda: self.read_from_data(self.file_edit.text()))
        self.layout.addWidget(self.btn_session, 1, 0)
        self.btn_session.hide()

        # subject 
        self.label_subject = QLabel('Subject:')
        self.layout.addWidget(self.label_subject, 4, 0)
        self.subject_edit = QLineEdit("")
        self.subject_edit.setPlaceholderText("Subject ID")
        self.layout.addWidget(self.subject_edit,4,1)
        self.label_subject.hide()
        self.subject_edit.hide()

        # session
        self.label_session = QLabel('Session:')
        self.layout.addWidget(self.label_session, 4, 2)
        self.session_edit = QLineEdit("")
        self.session_edit.setPlaceholderText("Session ID")
        self.layout.addWidget(self.session_edit,4,3)
        self.label_session.hide()
        self.session_edit.hide()

        # file name storing data for stimulation
        self.label_file = QLabel('Stimulation Data:')
        self.layout.addWidget(self.label_file, 5, 2)
        self.file_edit = QLineEdit("")
        self.file_edit.setPlaceholderText("file containing stimulation data")
        self.layout.addWidget(self.file_edit,5,3)
        self.label_file.hide()
        self.file_edit.hide()

        # save location
        self.label_save = QLabel('Save Location')
        self.layout.addWidget(self.label_save, 5, 0)
        self.save_edit = QLineEdit("")
        self.save_edit.setPlaceholderText("default folder: parameter_history")
        self.layout.addWidget(self.save_edit,5,1)
        self.label_save.hide()
        self.save_edit.hide()

        # choose save params or not
        self.box_save = QCheckBox('Save Parameters')
        self.layout.addWidget(self.box_save,3,1, alignment=Qt.AlignmentFlag.AlignBottom)       


        # ======== GRAPH FIELDS ========
        self.dt = [0,1]
        self.TBS_signals = np.zeros((2,2))
        self.plot_waveform = pg.PlotWidget()
        self.plot_waveform.getAxis("bottom").setLabel("Time", units="s")
        self.plot_waveform.getAxis("left").setLabel("Amplitude", units="mA")
        self.plot_waveform.plot(self.dt, self.TBS_signals[0]+self.TBS_signals[1])
        self.layout.addWidget(self.plot_waveform,2,2,2,2)


        # ======== LABEL FIELDS ========
        self.run_status = QLabel("Select Stimulation")
        self.run_status.setStyleSheet("color: orange; font-weight: bold;")
        self.layout.addWidget(self.run_status, 16, 3)

        
        # ======== APPLY LAYOUT ========
        self.setLayout(self.layout)
        self.show()
        for widget in self.findChildren(QWidget):
            if (isinstance(widget, QLabel) and 
                widget != self.blind_label and
                widget != self.settings_label and
                widget != self.select_stim_label and
                widget != self.parameter_label and
                widget != self.freq_label and
                widget != self.time_label and
                widget != self.currents_label):
                widget.setAlignment(Qt.AlignmentFlag.AlignRight)
            elif isinstance(widget, QLabel) and widget != self.blind_label and widget != self.settings_label:
                widget.setAlignment(Qt.AlignmentFlag.AlignBottom)

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

        self.total_TBS_time = int(self.total_TBS_time_edit.text())
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
            self.dt, self.TBS_signals = iTBS.iTBS(self.total_TBS_time,
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
            self.dt, self.TBS_signals = cTBS.cTBS(self.total_TBS_time,
                                        self.freq_of_pulse,
                                        self.burst_freq,
                                        self.carrier_f,
                                        self.A1, self.A2,
                                        self.ramp_up_time,
                                        self.ramp_down_time,
                                        rampup=rampup)
            
        elif self.drop_stim_select.currentText() == "TBS_control":
            self.dt, self.TBS_signals = TBS_ctrl.TBS_control(self.total_TBS_time,
                                                             self.carrier_f,
                                                             self.A1,
                                                             self.A2,
                                                             self.ramp_up_time,
                                                             self.ramp_down_time,
                                                             rampup=rampup)
            
        else:
            self.dt = [0,1]
            self.TBS_signals = np.zeros((2,2))
            
               
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
            self.plot_waveform.setYRange(-self.A_sum,self.A_sum)
            self.plot_waveform.getAxis("bottom").setLabel("Time", units="s")
            self.plot_waveform.getAxis("left").setLabel("Amplitude", units="mA")

            #plot lines surrounding main signal (exclude ramps)
            if lines:
                self.ramp_up_line = pg.InfiniteLine(pos=self.ramp_up_time, angle=90, movable=False)
                self.ramp_down_line = pg.InfiniteLine(pos=self.total_TBS_time+self.ramp_up_time, angle=90, movable=False)
                self.plot_waveform.addItem(self.ramp_up_line)
                self.plot_waveform.addItem(self.ramp_down_line)

            self.layout.addWidget(self.plot_waveform,2,2,2,2)

        
    def reset_defaults(self):
        """
        Description
        -----------
        Reset all GUI fields to default values of util.py
        """
        self.total_TBS_time_edit.setText(str(util.total_TBS_time))
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
        self.worker_thread = GUI_worker.WorkerThread(self)
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
                if self.use_trigger: #trigger disable necessary before updating task to avoid DAQ overload and spike
                    self.task.triggers.start_trigger.disable_start_trig()
                self.create_signals(rampup=False)
                self.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.TBS_signals)[1])
                self.worker_thread.update()
            if self.stop_request:
                # new waveform is ramp-down
                self.task.stop()
                if self.use_trigger: #trigger disable necessary before updating task to avoid DAQ overload and spike
                    self.task.triggers.start_trigger.disable_start_trig()
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
            if (self.drop_stim_select.currentText()=="iTBS" 
                or self.drop_stim_select.currentText()=="cTBS"
                or self.drop_stim_select.currentText() == "TBS_control"):
                self.run_status.setText("Ready")
                self.run_status.setStyleSheet("color: green; font-weight: bold;")
                self.btn_create_signals.setEnabled(True)
            else:
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
        if self.blind_mode.isChecked():
            for widget in self.findChildren(QWidget):
                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.btn_run_stimulation and
                    widget != self.btn_create_signals and
                    widget != self.btn_update and
                    widget != self.run_status and
                    widget != self.btn_stop and 
                    widget != self.select_stim_label and
                    widget != self.parameter_label and
                    widget != self.trigger_toggle
                    ): 
                    widget.setVisible(not widget.isVisible())
                # widgets present in blind mode only
                if (widget == self.box_save):
                    widget.setVisible(True)

        #back to testing mode
        else:
            for widget in self.findChildren(QWidget):
                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.btn_run_stimulation and
                    widget != self.btn_create_signals and
                    widget != self.btn_update and
                    widget != self.run_status and
                    widget != self.btn_stop and
                    widget != self.select_stim_label and
                    widget != self.parameter_label and
                    widget != self.trigger_toggle
                    ): 
                    widget.setVisible(not widget.isVisible())
                # widgets present in blind mode only
                if (widget == self.box_save):
                    widget.setVisible(False)

            # recall graphing to show signals in Testing mode        
            self.create_signals()
            self.graph_waveform(lines=False)
        
        # handling view toggle of ComboBox
        for drops in self.drop_stim_select.findChildren(QWidget):
            drops.setVisible(True)
        self.drop_stim_select.hidePopup()

    
    def toggle_trigger(self):
        """
        Description
        -----------
        Allows to choose to use trigger or not to start stimulations
        """
        if self.trigger_toggle.isChecked():
            self.use_trigger = True
        else:
            self.use_trigger = False


    def read_from_data(self, file_name):
        """
        Description
        -----------
        Choose stimulation protocol from excel file (for blind mode)

        Parameters
        ----------
        file_name : string
            name of the file storing protocol information; the file should contain a 3 x m matrix. 
            Column 1 contains subject ID. Column 2 contains protocol of session T3. Column 3 contains protocol of session T5.
        """
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir,"HummelGUI", file_name) 

        if not os.path.exists(path):
            self.run_status.setText("File not found")
            self.run_status.setStyleSheet("color: red; font-weight: bold;")
        else:
            try:
                df = pd.read_excel(path)
            except:
                self.run_status.setText("Check filename")
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)
                return
            
            session = self.session_edit.text()
            subject = self.subject_edit.text()
            df.index = df["Subj"]
            try:
                stim_type = df.at[subject, session]
            except:
                self.run_status.setText("Check session and subject ID")
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)
                return

            if stim_type == "iTBS":
                self.drop_stim_select.setCurrentText("iTBS")
                self.stim_selected()
            elif stim_type == "cTBS":
                self.drop_stim_select.setCurrentText("cTBS")
                self.stim_selected()
            elif stim_type == "TBS_control":
                self.drop_stim_select.setCurrentText("TBS_control")
                self.stim_selected()
            else:
                self.run_status.setText("Stimulation type ({}) not recognised".format(stim_type))
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)


    def save_params(self, directory="parameter_history"):
        """
        Description
        -----------
        Handles saving of parameters to a CSV file at the end of a stimulation.
        A directory called "parameter_history" is created in the working directory.
        The file is created inside "parameter_history".
        If the file already exists in "parameter_history", new data are appended to the end of the existing file, without overwriting.

        Parameters
        ----------
        directory : string
            name of the diectory to save data (if other than paramter_history)
        """
        #only save if box is checked
        if self.box_save.checkState() == Qt.CheckState.Checked:
            parent_dir = os.getcwd()
            path = os.path.join(parent_dir, directory) 

            if not os.path.exists(path):
                os.makedirs(path)

            file_name = os.path.join(path, 
                                    self.subject_edit.text()+
                                    "_"+
                                    self.session_edit.text()+
                                    ".csv") 
            
            with open(file_name, 'a', newline='') as file:
                file.write("\ntime,"+str(time.ctime(time.time())))
                file.write("\n"+self.subject_edit.text()+','+self.session_edit.text())
                file.write("\ntotal_time,"+str(self.total_TBS_time))
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


    def keyPressEvent(self, event):
        """Exit full screen mode"""
        if event.key() == Qt.Key.Key_Escape:
            self.showNormal()

            

"""

-new tasks:
    1) Implement start trigger
        -also needs new value field: number of stimulation repetitions
        -also needs check box: listen to trigger only if checked, otherwise stimulate as now
        -therefore, if trigger is checked: button run stimulation calls waiting for trigger (at beginning of run()?)
    
    2) README
        -Description of all files (with list of all functions (maybe annex with list of files and what they contain))
        -where to modify things for future implementations, and how (ex: add new signal in dropdown)
        -what to install and how
        
    3) Implement stop trigger
        -if trigger, calls stop()

    4) Modifications:
        DONE -Default is exp mode
        DONE -Remove shift in dt if rampup
        -refactor code by creating new GUI_Vault class; MainWindow then adds values to GUI_Vault, not self
        (-Add time stamp to save file name) (may not be ideal as creates new file each time (time will always be different to previous file, even with update durig same stim))
        -Add padding around GUI for full screen
        -Excel to read is coded (add to util.py), not GUI accessible
        -Subject/Session ID is drop down from elements in excel file
        -If blind mode, run stim without needing to press "create waveform"
        -Add TI signal; if TI is selected, "pulse frequency" label becomes "shift frequency", and "burst frequency is disabled"
        -Carrier frequency first in order in GUI
        -Labels showing what A1 and A2 values are
        
"""