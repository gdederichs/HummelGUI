import sys
from PyQt6.QtWidgets import (QApplication,
                            QLineEdit,
                            QLabel,
                            QWidget,
                            QPushButton,
                            QGridLayout)

import pyqtgraph as pg
from PyQt6.QtCore import pyqtSignal, Qt

import nidaqmx
from nidaqmx.constants import AcquisitionType
from nidaqmx.constants import WAIT_INFINITELY as inf

import numpy as np
from matplotlib import pyplot as plt
import time
import util
import threading


class WorkerThread(threading.Thread):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent # access to main window's attributes/functions

    def update(self):
        self.parent.update_request = False
        self.parent.send_signal()

    def run(self):
        # status labels for GUI
        self.parent.run_status.setText("Stimulation Ongoing")
        self.parent.run_status.setStyleSheet("color: red; font-weight: bold;")

        # handle button enabling/disabling while running
        self.parent.btn_update.setEnabled(True) 
        self.parent.btn_stop.setEnabled(True)
        self.parent.btn_create_signals.setEnabled(False) #while running, update() handles this

        # task handling/settings
        self.parent.task = nidaqmx.Task()
        self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao0")
        self.parent.task.ao_channels.add_ao_voltage_chan(util.device+"/ao1")
        self.parent.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.parent.iTBS_signals)[1])

        # write signals to DAQ
        self.parent.send_signal()

        # task closing handling
        self.parent.task.wait_until_done(inf)
        self.parent.task.close()

        # handle button enabling/disabling after run
        self.parent.btn_update.setEnabled(False)
        self.parent.btn_stop.setEnabled(False)
        self.parent.btn_create_signals.setEnabled(True) 

        # status labels
        self.parent.run_status.setText("Ready")
        self.parent.run_status.setStyleSheet("color: green; font-weight: bold;")


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # visual settings
        self.setWindowTitle('iTBS Interface')
        self.resize(800,0)
        self.layout = QGridLayout()


        # VALUE FIELDS
        # total stimulation time
        self.layout.addWidget(QLabel('Total Duration (seconds):'), 0, 0)
        self.total_iTBS_time_edit = QLineEdit(str(util.total_iTBS_time))
        self.layout.addWidget(self.total_iTBS_time_edit,0,1)

        # time of stimulation in one cycle
        self.layout.addWidget(QLabel('Cycle Stimulation Duration (seconds):'), 1, 0)
        self.cycle_stim_time_edit = QLineEdit(str(util.cycle_stim_time))
        self.layout.addWidget(self.cycle_stim_time_edit,1,1)

        # time of break in on cycle 
        self.layout.addWidget(QLabel('Cycle Break Duration (seconds):'), 2, 0)
        self.cycle_break_time_edit = QLineEdit(str(util.cycle_break_time))
        self.layout.addWidget(self.cycle_break_time_edit,2,1)

        # pulse frequency
        self.layout.addWidget(QLabel('Pulse Frequency (Hz):'), 3, 0)
        self.freq_of_pulse_edit = QLineEdit(str(util.freq_of_pulse))
        self.layout.addWidget(self.freq_of_pulse_edit,3,1)

        # cycle frequency
        self.layout.addWidget(QLabel('Cycle Frequency (Hz):'), 4, 0)
        self.cycle_freq_edit = QLineEdit(str(util.cycle_freq))
        self.layout.addWidget(self.cycle_freq_edit,4,1)

        # carrier frequency
        self.layout.addWidget(QLabel('Carrier Frequency (Hz):'), 5, 0)
        self.carrier_f_edit = QLineEdit(str(util.carrier_f))
        self.layout.addWidget(self.carrier_f_edit,5,1)


        # amplitude of signal 1
        self.layout.addWidget(QLabel('Amplitude 1 ():'), 6, 0)
        self.A1_edit = QLineEdit(str(util.ampli1))
        self.layout.addWidget(self.A1_edit,6,1)

        # amplitude of signal 2
        self.layout.addWidget(QLabel('Amplitude 2 ():'), 7, 0)
        self.A2_edit = QLineEdit(str(util.ampli2))
        self.layout.addWidget(self.A2_edit,7,1)


        # BUTTON FIELDS
        # reset (default set in util.py)
        self.btn_reset_defaults = QPushButton("Reset to Default Values")
        self.btn_reset_defaults.clicked.connect(self.reset_defaults)
        self.layout.addWidget(self.btn_reset_defaults,8,1)

        # create signals/waveforms
        self.btn_create_signals = QPushButton("Create Waveform")
        self.btn_create_signals.clicked.connect(self.create_signals)
        self.btn_create_signals.clicked.connect(self.graph_waveform)
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


        # GRAPH FIELDS
        self.dt = [0,1]
        self.iTBS_signals = np.zeros((2,2))
        self.plot_waveform = pg.PlotWidget()
        self.plot_waveform.plot(self.dt, self.iTBS_signals[0]+self.iTBS_signals[1])
        self.layout.addWidget(self.plot_waveform,0,2,14,1)


        # LABEL FIELDS
        self.run_status = QLabel("Ready")
        self.run_status.setStyleSheet("color: green; font-weight: bold;")
        self.layout.addWidget(self.run_status, 12, 0)
        
        self.update_request = False
        self.stop_request = False


        self.setLayout(self.layout)
        self.show()

    # FUNCTIONS
    def create_signals(self):
        self.total_iTBS_time = int(self.total_iTBS_time_edit.text())
        self.cycle_stim_time = int(self.cycle_stim_time_edit.text())
        self.cycle_break_time = int(self.cycle_break_time_edit.text())
        self.freq_of_pulse = int(self.freq_of_pulse_edit.text())
        self.cycle_freq = int(self.cycle_freq_edit.text())
        self.carrier_f = int(self.carrier_f_edit.text())
        self.A1 = float(self.A1_edit.text())
        self.A2 = float(self.A2_edit.text())
        self.dt, self.iTBS_signals = util.iTBS(self.total_iTBS_time,
                                     self.cycle_stim_time,
                                     self.cycle_break_time,
                                     self.freq_of_pulse,
                                     self.cycle_freq,
                                     self.carrier_f,
                                     self.A1, self.A2)
        
        
    def graph_waveform(self):
        self.plot_waveform = pg.PlotWidget()
        self.plot_waveform.plotItem.setMouseEnabled(y=False) # Only allow zoom in X-axis
        self.plot_waveform.plot(self.dt, self.iTBS_signals[0]+self.iTBS_signals[1])
        self.layout.addWidget(self.plot_waveform,0,2,14,1)

        
    def reset_defaults(self):
        self.total_iTBS_time_edit.setText(str(util.total_iTBS_time))
        self.cycle_stim_time_edit.setText(str(util.cycle_stim_time))
        self.cycle_break_time_edit.setText(str(util.cycle_break_time))
        self.freq_of_pulse_edit.setText(str(util.freq_of_pulse))
        self.cycle_freq_edit.setText(str(util.cycle_freq))
        self.carrier_f_edit.setText(str(util.carrier_f))
        self.A1_edit.setText(str(util.ampli1))
        self.A2_edit.setText(str(util.ampli2))


    def run_stimulation(self):
        # start the worker thread
        self.worker_thread = WorkerThread(self)
        self.worker_thread.start()


    def send_signal(self):
        self.task.write(self.iTBS_signals)
        self.task.start()
        #trigger check
        while not self.task.is_task_done():
            if self.update_request:
                self.task.stop()
                # create new waveform
                self.create_signals()
                self.task.timing.cfg_samp_clk_timing(rate=util.sampling_f, sample_mode=AcquisitionType.FINITE, samps_per_chan=np.shape(self.iTBS_signals)[1])
                self.worker_thread.update()
            if self.stop_request:
                self.stop_request = False
                self.task.stop() #task closed in worker thread


    def request_update(self):
        self.update_request = True


    def request_stop(self):
        self.stop_request = True




# RUN APPLICATION
app = QApplication(sys.argv)
window = MainWindow()
sys.exit(app.exec())


"""
CURRENT ISSUES:
-with stop: works in both multi_channel_test.py and GUI, but ONLY IF stim is in break (outputting zeros).
            else: spikes as usual
"""