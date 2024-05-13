# HummelGUI
The Graphical User Interface (GUI) proposed here controls a data aquisition system (DAQ) that can be used to control electrodes to conduct non-invasive brain stimulations. This repository contains the code for the GUI, as well as utility files, notably for defaults values. The following sections explain the GUI's dependencies and compatibility with DAQs, as well as its functionalities and features.
___
## Quick Guide
All necessary details are covered in depth in further sections. Here is a quick guide to using the GUI.
- Install dependancies
- Setup DAQ
  - BNC 1: "AI0" to stimulator 1
  - BNC 2: "AI1" to stimulator 2
  - BNC 3: "PFI0" to trigger port
  - USB: DAQ to computer running GUI
  - Enable stimulators
- Check/Set defaults in [util.py](HummelGUI/util.py), especially:
  - Stimulation parameters
  - Excel file name
  - Device (DAQ) name
- Run [main.py](HummelGUI/main.py)
  - Select mode
  - In "Settings Mode":
    - Select Stimulation    
    - Configure Parameters
    - Create Waveform
    - Check/Uncheck Trigger
    - Run Stimulation
    - Update and Stop stimulation if needed
  - In "Blind Mode":
    - Select Subject and Session   
    - Get Stimulation from file
    - Check/Uncheck parameter saving
    - Run Stimulation
    - Update and Stop stimulation if needed
___
## Installation and Dependencies
To install the GUI, download the [HummelGUI](HummelGUI/) folder in to the wanted directory (named *python_GUI* in further examples). Thereafer, the experimenter adds the excel file containing data for stimulation types for individual subjects to the [HummelGUI](HummelGUI/) folder.

The GUI is written in Python and depends on multiple Python packages. The following steps ensure proper functionning of the GUI.
1. [Install Python](https://www.python.org/downloads/) - Necessary
2. [Install Anaconda](https://docs.anaconda.com/free/anaconda/install/) - Highly Recommended (for better Python environment control)
3. [Install NI-MAX](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQwCAO&l=en-CH) - Optional (for testing DAQ, and testing code on virtual DAQs)
4. Install a code editor, such as [Visual Studio](https://code.visualstudio.com/) - Highly Recommended (for editing, running scripts, etc...)
5. Install packages - Necessary
   - Recommended to install with pip, through the terminal
   - [numpy](https://numpy.org/install/) - ```pip install numpy```
   - [PyQt6](https://pypi.org/project/PyQt6/) - ```pip install PyQt6```
   - [pyqtgraph](https://pypi.org/project/pyqtgraph/) - ```pip install pyqtgraph```
   - [nidaqmx](https://pypi.org/project/nidaqmx/) - ```pip install nidaqmx```
   - [pandas](https://pandas.pydata.org/docs/getting_started/install.html) - ```pip install pandas```
   - [matplotlib](https://pypi.org/project/matplotlib/) - ```pip install matplotlib```
___
## Launching the GUI
It is highly recommended to use a code editor such as [Visual Studio](https://code.visualstudio.com/) to interact with the GUI. This is especially true to edit code and default values, but is very helpful for ease of use to launch the GUI. This is done as follows in [Visual Studio](https://code.visualstudio.com/), assuming previous steps were followed.
1. File > Open folder... > Select the Directory in which [HummelGUI](HummelGUI/) was downloaded to (*python_GUI* in this example)
2. Select [main.py](HummelGUI/main.py)
3. Run Python file ("Play" symbol, top right)

The GUI can also be launched directly from the terminal, without needing to install an additional code editor. This is done as follows.
1. Open terminal (Windows key > Terminal)
2. Change directory to the Directory in which [HummelGUI](HummelGUI/) was downloaded to (*python_GUI* in this example)
   - For example: ```cd desktop\python_GUI```
3. Run [main.py](HummelGUI/main.py)
   - Command depends on prior installations, with or without Anaconda, etc.
   - Either: ```& C:/Users/uphummel/anaconda3/python.exe HummelGUI/main.py```
   - Or: ```python HummelGUI/main.py```

At this stage, the GUI window should open. It is recommended, prior to using on trial participants, to test all functionalities of the GUI on an oscilloscope, with the GUI window out of full-screen. This will allow to detect any errors that may occur if packages are lacking. If this is the case, follow a similar procedure as above, for example with pip, to install missing packages. All functionalities offered by the GUI are described in the following section.
___
## GUI Functionalities
The GUI proposed here offers two seperate modes: "Settings Mode" and "Blind Mode". These appear as follows.

![clean_set](demo/settings_clean.png)
![clean_bli](demo/blind_clean.png)

### Settings Mode
The "Settings Mode" is available to manually select a stimulation type, adjust parameters, and plot corresponding waveforms for visualisation. This mode is meant for testing, preparing and checking a specific setup or stimulation type.

![settings_mode](demo/settings_mode.png)

In this mode, one first selects the base stimulation type from the corresponding dropdown menu (A). Currently available stimulations include iTBS, cTBS, TBS control and TI. These can be selected as follows. As a note, how to add new stimulation types is explained further down.

Once the stimulation type is selected, the default parameters defined in [util.py](HummelGUI/util.py) can be modified directly through the GUI (B). The parameters that may be modified include duration parameters such as total duration of the stimulation, ramp-up and ramp-down time, frequency parameters such as carrier, pulse and burst frequencies, and current parameters such as the sum and ratio of currents. Default parameters can be reset thanks to the corresponding button.

Once parameters are chosen, the resulting waveform can be plotted and shown on the GUI for verification (C). Here zooming on the plot stretches the x axis, but the y axis remains between the signal's minimum and maximum. This allows for easy verification of the signal's form. Resetting the graphs view to the default view can be done in the bottom left corner of the plot. As a note, in "Settings Mode", this step is necessary before being able to run the stimulation. 

Once plotted, buttons to run the stimulation become available (D). If the "trigger" checkbox is selected, pressing this button will prime the stimulation and wait for an external trigger to begin. In addition, "update" and "stop" buttons become available during a stimulation, to update to a new stimulation type or parameters or stop the stimulation before its predefined end. Also, a number of times the stimulation is to be run ca be selected. Importantly, this count does not reset when updating the stimulation. These settings are available as follows.

Finally, a label will guide the experimenter in the use of the GUI (E). This label indicates if a stimulation is running, waiting for a trigger, ramping-down after pressing the "stop" button or waiting for the experimenter to select a stimulation. Other labels will appear in "Blind Mode". 

### Blind Mode
The "Blind Mode" is available to carry out experiments on participants for a study. In this mode, the stimulation type, waveform and all parameters are hidden from the experimenter. 

![blind_mode](demo/blind_mode.png)

Instead, the experimenter can first select the subject and session's ID from dropdown menus (A). Here only IDs that exist can be selected, depending on the data of the predefined excel file. From this same data, the stimulation type is chosen according to the IDs, and the parameters are read from default values. These default values, as well as the filename of the excel file, can be set prior to the study in [util.py](HummelGUI/util.py).

Once chosen, the experimenter uses the corresponding button to load the stimulation. The label (D) will then provide information on the status of the GUI. If all is in order, the GUI will be "Ready". Otherwise, the label will indicate to the experimenter if an issue is detected. This issue may be unselected IDs, a non-existing file or an unknown stimulation type defined in the excel file.

Before running the stimulation, the experimenter can choose to save or not the parameters to a seperate csv file for later use (B). This file (named _subjectID_sessionID.csv_) saves all parameters discussed above, as well as a time stamp of when the stimulation begun. This feature is also available in "Settings Mode". When a stimulation is updated, the new parameters are appended to the previous, in the same file. The default directory (_parameter_history_) in which these files are saved can be changed from the GUI.

Once set, the experimenter can run the stimulation as in the "Settings Mode", also with update, stop and trigger functions available (E). 

To toggle between these two modes, the experimenter must check or uncheck the "Blind Mode" chcekbox (C), as shown below.
___
## Defaults
All defaults can be set in [util.py](HummelGUI/util.py). This includes the default opening to "Blind Mode" or "Settings Mode", all default parameters for stimulations, the DAQ device name and the excel file name storing stimulations for specific IDs. Most important defauts are located at the head of the [util.py](HummelGUI/util.py) file.
___
## Setting up the DAQ
This GUI has been built for, and is intended to be used with National Instruments' [USB-6341 DAQ](https://www.ni.com/docs/en-US/bundle/usb-6341-specs/page/specs.html). The GUI might be compatible with others, but not all. In particular, certain features are **not compatible** with the [USB-6216](https://www.ni.com/docs/en-US/bundle/usb-6216-specs/page/specs.html).

To link the present GUI to the DAQ and [stimulators](https://www.digitimer.com/product/human-neurophysiology/peripheral-stimulators/ds5-isolated-bipolar-constant-current-stimulator/), the experimenter must first connect the computer running the GUI to the DAQ via a USB cable. Thereafter, two BNC cables run from the DAQ to either stimulator, and one runs to the computer running the tasks of the study (not the GUI computer) (see also the image below): 
- BNC cable 1 (red): from the **AI0** channel of the DAQ to the input channel of the first stimulator
- BNC cable 2 (red): from the **AI1** channel of the DAQ to the input channel of the second stimulator
- BNC cable 3 (blue): from the **PFI0** channel of the DAQ to trigger port of the task computer

![pinout](demo/pinout.png)

In addition to the labels proposed by the GUI, it is important to check the status of the physcial DAQ through the informative LEDs. In particular, when connected to a computer, the DAQ becomes "Ready" (one LED); when sending data through to the stimulators, the DAQ becomes "Active" (two LEDs). To ensure proper function, the correct DAQ device name must be set in [util.py](HummelGUI/util.py). This device name can be found through the [NI-MAX](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA03q000000YGQwCAO&l=en-CH) software, if the automatic pop-up window does not open when connecting the computer to the DAQ.

