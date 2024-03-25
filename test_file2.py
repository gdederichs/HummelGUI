import numpy as np
import threading
import time
import nidaqmx
from nidaqmx.constants import TerminalConfiguration, AcquisitionType, Signal

#generate a sine wave
def generate_signal(frequency, amplitude, sampling_rate, duration):
    num_samples = int(sampling_rate * duration)
    time_array = np.linspace(0, duration, num_samples, endpoint=False)
    signal = amplitude * np.sin(2 * np.pi * frequency * time_array)
    return signal


def continuous_output(output_task, signal):
    while True:
        output_task.write(signal, auto_start=True)

# parameters
sampling_rate = 10000  # Hz
frequency = 1000  # Hz
amplitude = 2  # Volts
duration = 10  # seconds
buffer_size = 10000  # Buffer size for continuous output
trigger_channel = "SimDev/port0/line0"  # Digital input channel for trigger
output_channel = "SimDev/ao0"  # Analog output channel


signal = generate_signal(frequency, amplitude, sampling_rate, duration)


# Create task for output
with nidaqmx.Task() as output_task:
    output_task.ao_channels.add_ao_voltage_chan(output_channel, min_val=-10, max_val=10)

    output_thread = threading.Thread(target=continuous_output, args=(output_task, signal))
    output_thread.start()

    # Monitor trigger for update
    with nidaqmx.Task() as trigger_task:
        trigger_task.di_channels.add_di_chan(trigger_channel)

        i = 0
        while i<1000:
            i+=1


            if trigger_task.read(number_of_samples_per_channel=1)[0] == True:
                print(trigger_task.read(number_of_samples_per_channel=1)[0])
                #new parameters
                frequency *= 1
                signal = generate_signal(frequency, amplitude, sampling_rate, duration)


                print("Sine wave modified.")
