import os

import numpy as np
import matplotlib.pyplot as plt
import RecordMicro


def get_correlation_dict(folder='correlation'):
    correlation_dict = {}
    for key_name in os.listdir(folder):
        correlation_dict[key_name] = [np.load(f'{folder}/{key_name}/{filename}', allow_pickle=True) for filename in os.listdir(f"{folder}/{key_name}") if filename.endswith('.npy')]
    return correlation_dict

def create_key_name(number_of_slices):
    keys_unsliced = ["C4", "C-4", "D4", "D-4", "E4", "F4", "F-4", "G4", "G-4", "A4", "A-4", "B4", "C5"]
    names_sliced = []

    for key_name in keys_unsliced:
        if key_name.__contains__('-'):
            names_sliced.append(key_name)
            break
        for i in range(1, number_of_slices + 1):
            names_sliced.append(f"{key_name}_{i}")
    return names_sliced

class PlayNotes:
    def __init__(self):
        self._correlation_dict = None
        self.keys_name = create_key_name(2)

    @property
    def correlation_dict(self):
        if self._correlation_dict is None:
            self._correlation_dict = get_correlation_dict()
        return self._correlation_dict

    def correlate(self, peak):
        highest_correlation = ("x", 0, None) # (key_name, max_corr, corr)
        for key_name, tries in self.correlation_dict.items():
            for i, try_ in enumerate(tries):
                corr = np.correlate(peak, try_, mode='same')
                max_corr = np.max(corr)
                print(f"{key_name} try {i} max correlation: {max_corr}")
                if highest_correlation[1]<max_corr:
                    highest_correlation = (key_name, max_corr, corr)
        return highest_correlation


if __name__ == '__main__':
    # Enregistrer un signal et garder le peak
    recorder = RecordMicro.RecordMicro()
    t, recording = recorder.record()
    norm_recording = RecordMicro.normalize(recording)
    peak = recorder.find_highest_peak(t, norm_recording)

    notesPlayer = PlayNotes()
    key_name, max_corr, corr = notesPlayer.correlate(peak)
    print(f"Note played: {key_name} with max correlation: {max_corr}")