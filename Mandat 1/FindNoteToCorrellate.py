import numpy as np
import sounddevice as sd
import matplotlib.pyplot as plt
import RecordMicro
from scipy.signal import find_peaks


# Enregistrer un signal
recorder = RecordMicro.RecordMicro(seconds=5, fs=44100, default=True)
t, myrecording = recorder.record()

plt.plot(t, myrecording)
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.show()

myrecording = recorder.normalize(myrecording)

plt.plot(t, myrecording)
plt.xlabel('Temps [s]')
plt.ylabel('Amplitude')
plt.show()

recorder.find_highest_peak(t, myrecording, filename='B')

