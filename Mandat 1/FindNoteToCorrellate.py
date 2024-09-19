import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import RecordMicro
from scipy.signal import find_peaks


# Enregistrer un signal
recorder = RecordMicro.RecordMicro()
t, recording = recorder.record()

plt.plot(t, recording)
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.show()

# use the normalized version

norm_recording = recorder.normalize(recording)

plt.plot(t, norm_recording)
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.show()

recorder.find_highest_peak(t, norm_recording, filename='D')

