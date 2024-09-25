# Vous devez installer la librairie sounddevice
# PIP :  pip install sounddevice
# Anaconda : conda install -c conda-forge python-sounddevice
import asyncio
import queue
import sys

import sounddevice as sd
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import find_peaks
import os


def normalize(recording):
    return (recording / np.linalg.norm(recording)).flatten()


class RecordMicro:
    def __init__(self, seconds=5, fs=44100, default=True):
        self.seconds = seconds
        self.fs = fs
        self.default = default
        self.devices = sd.query_devices()
        self.time_around_peak = 0.25 # in seconds

        self.select_devices()

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
        rec = sd.rec(int(self.seconds * self.fs), samplerate=self.fs, channels=1)
        sd.wait()
        t = np.arange(0, self.seconds, 1/self.fs)
        return t, rec

    def find_highest_peak(self, t, recording, filename=''):
        peaks, _ = find_peaks(recording, height=0.025)

        # Show the peaks on graph
        # plt.plot(t, recording)
        # plt.plot(t[peaks], recording[peaks], "x")
        # plt.xlabel('Temps [s]')
        # plt.ylabel('Amplitude')
        # plt.title(f'Peaks {filename}')
        # plt.show()

        if len(peaks) > 0:
            highest_peak = peaks[np.argmax(recording[peaks])]
            print(f"Le plus haut pic est à l'indice {highest_peak} avec une amplitude de {recording[highest_peak]}")
            print(f"Un temps de {self.seconds * highest_peak / len(t)}")

            # Prendre seulement 250ms avant et après le pic
            start = max(0, highest_peak - int(self.time_around_peak * self.fs))
            end = min(len(recording), highest_peak + int(self.time_around_peak * self.fs))

            # plt.plot(t[start:end], recording[start:end])
            # plt.xlabel('Temps [s]')
            # plt.ylabel('Amplitude')
            # plt.title(f'Peak {filename}')
            # plt.show()

            # just to be sure that the peak is normalized
            peak_normalized = normalize(recording[start:end])

            plt.plot(t[start:end], peak_normalized)
            plt.xlabel('Temps [s]')
            plt.ylabel('Amplitude')
            plt.title(f'Peak normalized {filename}')
            plt.show()

            return peak_normalized
        else:
            raise Exception("Aucun pic trouvé")

    def save_peak(self, peak, dir_name, filename):
        dir = f"correlation/{dir_name}"
        # Créer le répertoire s'il n'existe pas déjà
        os.makedirs(dir, exist_ok=True)
        np.save(f"{dir}/{filename}.npy", peak)