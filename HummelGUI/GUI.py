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

import numpy as np
import pandas as pd

import util
import iTBS
import cTBS
import TBS_ctrl
import TI
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
        self.layout.setColumnStretch(0, 0)
        
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
        self.drop_stim_select.setFixedWidth(300)
        self.drop_stim_select.addItems(["Select Stimulation","iTBS","cTBS","TBS_control","TI"])
        self.drop_stim_select.currentTextChanged.connect(self.stim_selected)
        self.layout.addWidget(self.drop_stim_select,1,0)

        # settings mode label
        self.settings_label = QLabel("Settings\nMode")
        self.settings_label.setStyleSheet("color: white; font-weight: bold; font-size: 80pt;")
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

        # carrier frequency
        self.layout.addWidget(QLabel('Carrier Frequency (Hz):'), 9, 0)
        self.carrier_f_edit = QLineEdit(str(util.carrier_f))
        self.layout.addWidget(self.carrier_f_edit,9,1)

        # pulse frequency
        self.pulse_freq_label = QLabel('Pulse Frequency (Hz):')
        self.layout.addWidget(self.pulse_freq_label, 10, 0)
        self.freq_of_pulse_edit = QLineEdit(str(util.freq_of_pulse))
        self.layout.addWidget(self.freq_of_pulse_edit,10,1)

        # burst frequency
        self.layout.addWidget(QLabel('Burst Frequency (Hz):'), 11, 0)
        self.burst_freq_edit = QLineEdit(str(util.burst_freq))
        self.layout.addWidget(self.burst_freq_edit,11,1)

        # current label
        self.currents_label = QLabel("Current Parameters")
        self.currents_label.setStyleSheet("color: black; font-weight: bold;")
        self.layout.addWidget(self.currents_label,12,0)

        # sum of amplitudes
        self.layout.addWidget(QLabel('Amplitude Sum (mA):'), 13, 0)
        self.A_sum_edit = QLineEdit(str(util.A_sum))
        self.A_sum_edit.textChanged.connect(self.update_ratio_labels)
        self.layout.addWidget(self.A_sum_edit,13,1)

        # ratio of amplitudes
        self.layout.addWidget(QLabel('Amplitude Ratio (A1/A2):'), 14, 0)
        self.A_ratio_edit = QLineEdit(str(util.A_ratio))
        self.A_ratio_edit.textChanged.connect(self.update_ratio_labels)
        self.layout.addWidget(self.A_ratio_edit,14,1)

        # labels indicating amplitudes
        self.layout.addWidget(QLabel('Amplitude Values:'), 15, 0)
        self.a_label = QLabel('A1 = {} [mA]; A2 = {} [mA]'.format(util.ampli1, util.ampli2))
        self.layout.addWidget(self.a_label, 15, 1)

        # repetition label
        self.rep_label = QLabel("Repetition Parameters")
        self.rep_label.setStyleSheet("color: black; font-weight: bold;")
        self.layout.addWidget(self.rep_label,8,2)

        # number of stimulation repetition
        self.layout.addWidget(QLabel('Number of Stimulation Repetitions:'), 9, 2)
        self.rep_num_edit = QLineEdit(str(util.rep_num))
        self.layout.addWidget(self.rep_num_edit, 9, 3)


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
        self.blind_label = QLabel("Blind\nMode")
        self.blind_label.setStyleSheet("color: white; font-weight: bold; font-size: 80pt;")
        self.blind_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.layout.addWidget(self.blind_label,0,2,6,2)
        self.blind_label.hide()

        # get session button
        self.btn_session = QPushButton("Get Stimulation from file")
        self.btn_session.clicked.connect(self.read_from_data)
        self.layout.addWidget(self.btn_session, 2,0,1,2)
        self.btn_session.hide()

        # read available subjects and sessions
        self.subj, self.sess = util.get_subject_and_session_IDs(util.excel_file_name)

        # subject 
        self.subject_edit = QComboBox()
        self.subject_edit.addItems(self.subj)
        self.layout.addWidget(self.subject_edit,1,0)
        self.subject_edit.hide()

        # session
        self.session_edit = QComboBox()
        self.session_edit.addItems(self.sess)
        self.layout.addWidget(self.session_edit,1,1)
        self.session_edit.hide()

        # save location
        self.save_edit = QLineEdit("")
        self.save_edit.setPlaceholderText("Default Folder to Save Parameters: parameter_history")
        self.save_edit.setFixedWidth(300)
        self.layout.addWidget(self.save_edit,4,0)
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
                widget != self.currents_label and
                widget != self.a_label and
                widget != self.rep_label):
                widget.setAlignment(Qt.AlignmentFlag.AlignRight)
            elif isinstance(widget, QLabel) and widget != self.blind_label and widget != self.settings_label:
                widget.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # choose which window to open on start
        if util.default_mode=="Blind":
            self.blind_mode.setCheckState(Qt.CheckState.Checked)



    # =============== FUNCTIONS ===============
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
        self.rep_num_edit.setText(str(util.rep_num))
    

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
        self.rep_num = int(self.rep_num_edit.text())


    def graph_waveform(self, lines=True):
        """
        Description
        -----------
        Plot the sum of signals stored in GUI and shows the result in a widget

        Parameters
        ----------
        lines : bool
            decides whether lines are plotted around the main signal
        """
        #only plot waveform if mode is not blind
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

            # update graph widget
            self.layout.addWidget(self.plot_waveform,2,2,2,2)


    def create_signals(self, rampup=True):
        """
        Description
        -----------
        Creates signals from GUI values (calls assign_values() before running)
        and selected stimulation type, and stores signals

        Parameters
        ----------
        rampup: bool
            decides whether a ramping signal with no shift is added to the main signal
        """
        self.assign_values()

        # signal for iTBS
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
        # signal for cTBS    
        elif self.drop_stim_select.currentText() == "cTBS":
            self.dt, self.TBS_signals = cTBS.cTBS(self.total_TBS_time,
                                        self.freq_of_pulse,
                                        self.burst_freq,
                                        self.carrier_f,
                                        self.A1, self.A2,
                                        self.ramp_up_time,
                                        self.ramp_down_time,
                                        rampup=rampup)
        # signal for TBS_control
        elif self.drop_stim_select.currentText() == "TBS_control":
            self.dt, self.TBS_signals = TBS_ctrl.TBS_control(self.total_TBS_time,
                                                             self.carrier_f,
                                                             self.A1,
                                                             self.A2,
                                                             self.ramp_up_time,
                                                             self.ramp_down_time,
                                                             rampup=rampup)
        # signal for TI
        elif self.drop_stim_select.currentText() == "TI":
            self.dt, self.TBS_signals = TI.TI(self.total_TBS_time,
                                              self.freq_of_pulse,
                                              self.carrier_f,
                                              self.A1,
                                              self.A2,
                                              self.ramp_up_time,
                                              self.ramp_down_time,
                                              rampup=rampup)
        # blank signal    
        else:
            self.dt = [0,1]
            self.TBS_signals = np.zeros((2,2))
            
               
    def create_stop_signal(self):
        """
        Description
        -----------
        Creates a ramp down signal with null envelope
        """
        #named TBS_signals for code usability, 
        #but is simply high f signals,
        #with decreasing amplitude and null envelope
        self.TBS_signals = util.ramp(direction="down",
                                 carrier_f=self.carrier_f,
                                 ramp_time=self.ramp_down_time,
                                 A1_max=self.A1,
                                 A2_max=self.A2)
        

    def stim_selected(self):
        """
        Description
        -----------
        Updates information label when stimulation type is selected
        """
        if not self.running:
            if (self.drop_stim_select.currentText()=="iTBS" 
                or self.drop_stim_select.currentText()=="cTBS"
                or self.drop_stim_select.currentText() == "TBS_control"
                or self.drop_stim_select.currentText() == "TI"):
                self.run_status.setText("Ready")
                self.run_status.setStyleSheet("color: green; font-weight: bold;")
                self.btn_create_signals.setEnabled(True)
            else:
                self.run_status.setText("Select Stimulation")
                self.run_status.setStyleSheet("color: orange; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)

            #special labels for TI
            if self.drop_stim_select.currentText() == "TI":
                self.pulse_freq_label.setText("Shift Frequency (Hz)")
                self.burst_freq_edit.setEnabled(False)
            else:
                self.pulse_freq_label.setText("Pulse Frequency (Hz)")
                self.burst_freq_edit.setEnabled(True)



    def read_from_data(self):
        """
        Description
        -----------
        Choose stimulation protocol from excel file (for blind mode)

        Parameters
        ----------
        file_name : string
            name of the file storing protocol information; the file should contain a 3xN matrix. 
            Column 1 contains subject ID. Column 2 contains protocol of session T3. Column 3 contains protocol of session T5.
        """
        parent_dir = os.getcwd()
        path = os.path.join(parent_dir,"HummelGUI", util.excel_file_name) 

        # check path
        if not os.path.exists(path):
            self.run_status.setText("File not found")
            self.run_status.setStyleSheet("color: red; font-weight: bold;")
        else: # (if path exists)
            try:
                df = pd.read_excel(path)
            except:
                self.run_status.setText("Check filename")
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)
                self.btn_run_stimulation.setEnabled(False)
                return # quit function if filename does not exist
            
            # read session information
            session = self.session_edit.currentText()
            subject = self.subject_edit.currentText()
            df.index = df["Subj"]
            try:
                stim_type = df.at[subject, session]
            except:
                self.run_status.setText("Check session and subject ID")
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)
                self.btn_run_stimulation.setEnabled(False)
                return

            # select stim type from file
            if stim_type == "iTBS":
                self.drop_stim_select.setCurrentText("iTBS")
                if self.blind_mode.isChecked():
                    # in blind mode, signals are auto-created
                    self.btn_run_stimulation.setEnabled(True)
                self.stim_selected()

            elif stim_type == "cTBS":
                self.drop_stim_select.setCurrentText("cTBS")
                if self.blind_mode.isChecked():
                    # in blind mode, signals are auto-created
                    self.btn_run_stimulation.setEnabled(True)
                self.stim_selected()

            elif stim_type == "TBS_control":
                self.drop_stim_select.setCurrentText("TBS_control")
                if self.blind_mode.isChecked():
                    # in blind mode, signals are auto-created
                    self.btn_run_stimulation.setEnabled(True)
                self.stim_selected()

            elif stim_type == "TI":
                self.drop_stim_select.setCurrentText("TI")
                if self.blind_mode.isChecked():
                    # in blind mode, signals are auto-created
                    self.btn_run_stimulation.setEnabled(True)
                self.stim_selected()
                
            else:
                self.run_status.setText("Stimulation type ({}) not recognised".format(stim_type))
                self.run_status.setStyleSheet("color: red; font-weight: bold;")
                self.btn_create_signals.setEnabled(False)
                self.btn_run_stimulation.setEnabled(False)


    def run_stimulation(self):
        """
        Description
        -----------
        Triggers the start of the stimulation by starting worker thread
        """
        # in blind mode, signals are auto-created by running
        if self.blind_mode.isChecked():
            self.create_signals()

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
        
        while not self.task.is_task_done():
            # continuously checks for update or stop request while task is running
            if self.update_request or self.stop_request:
                self.task.stop()
                if self.use_trigger: #trigger disable necessary before updating task to avoid DAQ overload and spike
                    self.task.triggers.start_trigger.disable_start_trig()
                
                # update
                if self.update_request:
                    self.create_signals(rampup=False)

                # stop
                else: #self.stop_request:
                    self.create_stop_signal()

                self.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.TBS_signals)[1])
                self.worker_thread.update()
            
    
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
        Toggles GUI widgets between Blind mode and settings mode
        """
        #turn on blind mode
        if self.blind_mode.isChecked():
            for widget in self.findChildren(QWidget):
                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.btn_run_stimulation and
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

        #back to settings mode
        else:
            for widget in self.findChildren(QWidget):

                # widgets that do not change
                if (widget != self.blind_mode and
                    widget != self.btn_run_stimulation and
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

                # handling view toggle of ComboBox
                for drops in self.session_edit.findChildren(QWidget):
                    drops.setVisible(False)

                for drops in self.subject_edit.findChildren(QWidget):
                    drops.setVisible(False)

            # recall graphing to show signals in Testing mode        
            self.create_signals()
            self.graph_waveform(lines=False)
        
        # handling view toggle of ComboBox
        for drops in self.drop_stim_select.findChildren(QWidget):
            drops.setVisible(True)    
        self.drop_stim_select.hidePopup()
        self.subject_edit.hidePopup()
        self.session_edit.hidePopup()

    
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
                                    self.subject_edit.currentText()+
                                    "_"+
                                    self.session_edit.currentText()+
                                    ".csv") 
            
            with open(file_name, 'a', newline='') as file:
                file.write("\ntime,"+str(time.ctime(time.time())))
                file.write("\n"+self.subject_edit.currentText()+','+self.session_edit.currentText())
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

    
    def update_ratio_labels(self):
        """Updates ratio labels"""
        summ = float(self.A_sum_edit.text())
        ratioo = float(self.A_ratio_edit.text())
        aa1 = summ/(1+ratioo)
        aa2 = ratioo*aa1
        self.a_label.setText('A1 = {:.3f} [mA]; A2 = {:.3f} [mA]'.format(aa1, aa2))

            

"""

-new tasks:
    DONE - 1) Implement start trigger
        DONE -also needs new value field: number of stimulation repetitions
        DONE -also needs check box: listen to trigger only if checked, otherwise stimulate as now
    
    2) README
        -Description of all files (with list of all functions (maybe annex with list of files and what they contain))
        -where to modify things for future implementations, and how (ex: add new signal in dropdown)
        -what to install and how
        
    3) Implement stop trigger
        -if trigger, calls stop()

    4) Modifications:
        DONE -Default is exp mode
        DONE -Remove shift in dt if rampup
        NOT NECESSARY -refactor code by creating new GUI_Vault class; MainWindow then adds values to GUI_Vault, not self
        (-Add time stamp to save file name) (may not be ideal as creates new file each time (time will always be different to previous file, even with update durig same stim))
        NOT NECESSARY -Add padding around GUI for full screen
        DONE -Excel to read is coded (add to util.py), not GUI accessible
        DONE -Subject/Session ID is drop down from elements in excel file
        DONE -If blind mode, run stim without needing to press "create waveform"
        DONE -Add TI signal; if TI is selected, "pulse frequency" label becomes "shift frequency", and "burst frequency" is disabled
        DONE -Carrier frequency first in order in GUI
        DONE -Labels showing what A1 and A2 values are
        
"""