# Vous devez installer la librairie sounddevice
# PIP :  pip install sounddevice
# Anaconda : conda install -c conda-forge python-sounddevice

import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks

class RecordMicro:
    def __init__(self, seconds=5, fs=44100, default=True):
        self.seconds = seconds
        self.fs = fs
        self.default = default
        self.devices = sd.query_devices()
        self.myrecording = None
        self.time_around_peak = 0.25

    def select_devices(self):
        if not self.default:
            InputStr = "Choisir le # correspondant au micro parmi la liste: \n"
            OutputStr = "Choisir le # correspondant au speaker parmi la liste: \n"
            for i in range(len(self.devices)):
                if self.devices[i]['max_input_channels']:
                    InputStr += ('%d : %s \n' % (i, ''.join(self.devices[i]['name'])))
                if self.devices[i]['max_output_channels']:
                    OutputStr += ('%d : %s \n' % (i, ''.join(self.devices[i]['name'])))
            DeviceIn = input(InputStr)
            DeviceOut = input(OutputStr)
            sd.default.device = [int(DeviceIn), int(DeviceOut)]
        print("Recording with : {} \n".format(self.devices[sd.default.device[0]]['name']))

    def record(self):
        self.select_devices()
        self.myrecording = sd.rec(int(self.seconds * self.fs), samplerate=self.fs, channels=1)
        sd.wait()
        t = np.arange(0, self.seconds, 1/self.fs)
        return t, self.myrecording

    def normalize(self, myrecording):
        self.myrecording = (myrecording / np.linalg.norm(myrecording)).flatten()
        return self.myrecording

    def find_highest_peak(self, t, myrecording, filename=''):
        peaks, _ = find_peaks(myrecording, height=0.025)
        if len(peaks) > 0:
            highest_peak = peaks[np.argmax(myrecording[peaks])]
            print(f"Le plus haut pic est à l'indice {highest_peak} avec une amplitude de {myrecording[highest_peak]}")
            print(f"Un temps de {self.seconds * highest_peak / len(t)}")

            # Prendre seulement 250ms avant et après le pic
            start = max(0, highest_peak - int(self.time_around_peak * self.fs))
            end = min(len(myrecording), highest_peak + int(self.time_around_peak * self.fs))
            plt.plot(t[start:end], myrecording[start:end])
            plt.xlabel('Temps [s]')
            plt.ylabel('Amplitude')
            plt.show()

            if filename != '':
                np.save(f"correlation/{filename}.npy", myrecording)

            return myrecording[start:end]
        else:
            print("Aucun pic trouvé")
            return None