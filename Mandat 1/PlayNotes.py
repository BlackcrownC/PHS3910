import os

import numpy as np
import matplotlib.pyplot as plt
import RecordMicro
from concurrent.futures import ThreadPoolExecutor, as_completed
from IPython import embed


def get_correlation_dict(folder='correlation'):
    correlation_dict = {}
    for key_name in os.listdir(folder):
        for try_ in os.listdir(f"{folder}/{key_name}"):
            number = try_.split('.')[0]
            correlation_dict[f'{key_name}_{number}'] = np.load(f'{folder}/{key_name}/{try_}') # [np.load(f'{folder}/{key_name}/{filename}', allow_pickle=True) for filename in os.listdir(f"{folder}/{key_name}") if filename.endswith('.npy')]
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
    
    # Function that compute the correlation between two signal and outputs the maximum amplitude
    def correlate_two_signal(self, signal1, note_name, signal2):
        correlation = np.correlate(signal1, signal2, mode='same')
        max_corr = max_corr = np.max(correlation)
        return (note_name, max_corr)
    
    # Main function to compute the maximum correlation using parallel processing
    def max_correlation_parallel(self, signal, signal_bank):
        results = []
        
        # Use ThreadPoolExecutor for parallel processing
        with ThreadPoolExecutor() as executor:
            # Submit tasks for each signal in the bank, along with its key
            futures = [executor.submit(self.correlate_two_signal, signal, key, signal_bank[key]) for key in signal_bank]
            
            # Gather results as they are completed
            for future in as_completed(futures):
                results.append(future.result())  # result() returns a tuple (key, max_corr)
        
        # Find the key with the maximum correlation
        max_key, max_corr = max(results, key=lambda x: x[1])
        
        return max_key, max_corr  # Return the key and the corresponding maximum correlation


    def correlate(self, peak):
        folders = [folder for folder in os.listdir(r'Correlation')]
        highest_correlation = ("x", 0, None) # (key_name, max_corr, corr)
        max_per_touch = np.zeros(len(folders))
        count = 0
        for key_name, tries in self.correlation_dict.items():
            for i, try_ in enumerate(tries):
                corr = np.correlate(peak, try_, mode='same')
                max_corr = np.max(corr)
                if max_per_touch[count] < max_corr:
                    max_per_touch[count] = max_corr
                print(f"{key_name} try {i} max correlation: {max_corr}")
                if highest_correlation[1]<max_corr:
                    highest_correlation = (key_name, max_corr, corr)
            count += 1
        return highest_correlation, max_per_touch


if __name__ == '__main__':
    #Enregistrer un signal et garder le peak
    recorder = RecordMicro.RecordMicro()
    t, recording = recorder.record()
    norm_recording = RecordMicro.normalize(recording)
    peak = recorder.find_highest_peak(t, norm_recording)

    notesPlayer = PlayNotes()
    max_key, max_corr = notesPlayer.max_correlation_parallel(peak, get_correlation_dict())
    print(f"Note played: {max_key} with correlation of {max_corr}")
    # highest_correlation, max_per_touch = notesPlayer.correlate(peak)
    # np.save('max_per_touch.npy', max_per_touch)
    # print(f"Note played: {highest_correlation[0]} with max correlation: {highest_correlation[1]}")

    embed()