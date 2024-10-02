import asyncio
import queue
import sys

import numpy as np
import sounddevice as sd
from collections import deque
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
import PlayNotes

fs = 44100
time_around_peak = 0.25
peak_height = 0.001

reading_length = 4 * int(fs * time_around_peak) # Lire 1 seconde de signal
saved_length = 2 * reading_length # Garder 2 secondes de signal

playNotes = PlayNotes.PlayNotes()

def normalize(recording):
    return (recording / np.linalg.norm(recording)).flatten()

async def inputstream_generator(channels=1, **kwargs):
    """Generator that yields blocks of input data as NumPy arrays."""
    q_in = asyncio.Queue(maxsize=saved_length)
    loop = asyncio.get_event_loop()

    def callback(indata, frame_count, time_info, status):
        loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

    stream = sd.InputStream(callback=callback, channels=channels, samplerate=fs, **kwargs)
    with stream:
        while True:
            indata, status = await q_in.get()
            yield indata, status


async def manage_input_stream(**kwargs):
    """Show minimum and maximum value of each incoming audio block."""
    stash = deque(maxlen=saved_length)
    async for indata, status in inputstream_generator(**kwargs):
        if status:
            print(status)
        stash.extend(indata)
        if len(stash) >= reading_length: # Il le fait peut-être trop rapidement
            part_of_signal = np.array(stash)[:reading_length].flatten()
            norm_signal = normalize(part_of_signal)
            _ = asyncio.create_task(peak_verification(norm_signal))

async def peak_verification(recording):
    peaks, _ = find_peaks(recording, height=peak_height)
    if len(peaks) == 0:
        return None
    highest_peak = peaks[np.argmax(recording[peaks])]

    # Prendre seulement 250ms avant et après le pic
    start = max(0, highest_peak - int(time_around_peak * fs))
    end = min(len(recording), highest_peak + int(time_around_peak * fs))

    # just to be sure that the peak is normalized
    peak_normalized = normalize(recording[start:end])

    _ = asyncio.create_task(correlate_stash(peak_normalized))

async def correlate_stash(peak):
    max_key, max_corr = playNotes.max_correlation_parallel(peak, PlayNotes.get_correlation_dict())
    # (key_name, max_corr, corr), max_per_touch = playNotes.correlate(peak)
    print(f"La note est {max_key} avec une corrélation de {max_corr}")


try:
    asyncio.run(manage_input_stream())
except KeyboardInterrupt:
    sys.exit('\nInterrupted by user')