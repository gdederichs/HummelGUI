# HummelGUI
The Graphical User Interface (GUI) proposed here controls a data aquisition system (DAQ) that can be used control electrodes for non-invasive brain stimulation. This repository contains the code for the GUI, as well as utility files, notably for defaults values. The following sections explain the GUI's dependencies and compatibility with DAQs, as well as its functionalities and features.
___
## GUI Functionalities
### Mode Selection
The GUI proposed here offers two seperate modes. 

Firstly, a "Settings Mode" is available to manually select a stimulation type, adjust parameters, and plot corresponding waveforms for visualisation. This mode is meant for testing, preparing and checking a specific setup or stimulation type.

Secondly, a "Blind Mode" is available to carry out experiments on participants for a study. In this mode, the stimulation type, waveform and all parameters are hidden from the experimenter. Instead, the experimenter can enter the subject and session's ID, corresponding to a pre-prepared excel file. From this file, the stimulation type is chosen according to the IDs, and the parameters are read from default values. These default values can be preset in [util.py](HummelGUI/util.py).

To toggle between these two modes, the experimenter must check or uncheck the "Blind Mode" chcekbox, as shown below.

### Parameter setting
coming soon...
### Creating a Waveform
coming soon...
### Starting a stimulation
coming soon...
### Updating a stimulation
coming soon...
### Stopping the stimulation
coming soon...
### Checking the stimulation state
coming soon...
### Saving parameters to CSV
coming soon...
___
## How to install/Dependencies
coming soon...
___
## DAQ compatibility
coming soon...


