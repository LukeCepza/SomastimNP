from pylsl import StreamInlet, resolve_stream
import pyedflib
import numpy as np
import time

# Resolve the EEG stream
print("Looking for an EEG stream...")
streams = resolve_stream('name', 'EEGDataStream')

# Create an EDF file
num_channels = streams[0].channel_count()
sample_rate = int(streams[0].nominal_srate())
signal_labels = [f"Channel_{i+1}" for i in range(num_channels)]
channel_info = []

for i in range(num_channels):
    ch_dict = {'label': signal_labels[i], 'dimension': 'uV', 'sample_frequency': sample_rate,
               'physical_max': 100, 'physical_min': -100, 'digital_max': 32767, 'digital_min': -32768}
    channel_info.append(ch_dict)

# Create a buffer to store the data
data_buffer = []

# Create a new inlet to read from the stream
inlet = StreamInlet(streams[0])

# List of markers (description, onset_in_seconds)
markers = [
    ("33031", 2),
    ("33032", 4),
    ("33033", 5),
    ("33034", 6),
    ("33035", 8),
    ("33036", 10)
]

try:
    marker_index = 0
    start_time = time.time()
    while True:
        chunk, timestamps = inlet.pull_chunk()
        current_time = time.time()

        if timestamps:
            data_buffer.extend(chunk)
        
        # Check for markers and trigger stimuli
        if marker_index < len(markers) and current_time - start_time >= markers[marker_index][1]:
            print("Triggering stimulus:", markers[marker_index][0])
            marker_index += 1

except KeyboardInterrupt:
    pass

# Save the collected data to an EDF file
if data_buffer:
    data_array = np.array(data_buffer).T  # Transpose data
    
    edf_file = pyedflib.EdfWriter("output.edf", num_channels, file_type=pyedflib.FILETYPE_EDFPLUS)
    edf_file.setSignalHeaders(channel_info)
    edf_file.writeSamples(data_array)
    for A in markers:
        edf_file.writeAnnotation(A[1],-1, A[0])
    edf_file.close()
    print("Data saved to output.edf")
else:
    print("No data collected.")