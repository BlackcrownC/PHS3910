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

            if filename != '':
                np.save(f"correlation/{filename}.npy", peak_normalized)

            return peak_normalized
        else:
            print("Aucun pic trouvé")
            return None

    async def inputstream_generator(channels=1, **kwargs):
        """Generator that yields blocks of input data as NumPy arrays."""
        q_in = asyncio.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))

        stream = sd.InputStream(callback=callback, channels=channels, **kwargs)
        with stream:
            while True:
                indata, status = await q_in.get()
                yield indata, status

    async def stream_generator(self, blocksize, *, channels=1, dtype='float32',
                               pre_fill_blocks=10, **kwargs):
        """Generator that yields blocks of input/output data as NumPy arrays.

        The output blocks are uninitialized and have to be filled with
        appropriate audio signals.

        """
        assert blocksize != 0
        q_in = asyncio.Queue()
        q_out = queue.Queue()
        loop = asyncio.get_event_loop()

        def callback(indata, outdata, frame_count, time_info, status):
            loop.call_soon_threadsafe(q_in.put_nowait, (indata.copy(), status))
            outdata[:] = q_out.get_nowait()

        # pre-fill output queue
        for _ in range(pre_fill_blocks):
            q_out.put(np.zeros((blocksize, channels), dtype=dtype))

        stream = sd.Stream(blocksize=blocksize, callback=callback, dtype=dtype,
                           channels=channels, **kwargs)
        with stream:
            while True:
                indata, status = await q_in.get()
                outdata = np.empty((blocksize, channels), dtype=dtype)
                yield indata, outdata, status
                q_out.put_nowait(outdata)

    async def print_input_infos(self, **kwargs):
        """Show minimum and maximum value of each incoming audio block."""
        async for indata, status in self.inputstream_generator(**kwargs):
            if status:
                print(status)
            print('min:', indata.min(), '\t', 'max:', indata.max())

    async def wire_coro(self, **kwargs):
        """Create a connection between audio inputs and outputs.

        Asynchronously iterates over a stream generator and for each block
        simply copies the input data into the output block.

        """
        async for indata, outdata, status in self.stream_generator(**kwargs):
            if status:
                print(status)
            outdata[:] = indata

    async def main(self, **kwargs):
        print('Some informations about the input signal:')
        try:
            await asyncio.wait_for(self.print_input_infos(), timeout=2)
        except asyncio.TimeoutError:
            pass
        print('\nEnough of that, activating wire ...\n')
        audio_task = asyncio.create_task(self.wire_coro(**kwargs))
        for i in range(10, 0, -1):
            print(i)
            await asyncio.sleep(1)
        audio_task.cancel()
        try:
            await audio_task
        except asyncio.CancelledError:
            print('\nwire was cancelled')

if __name__ == "__main__":
    try:
        asyncio.run(RecordMicro().main(blocksize=1024))
    except KeyboardInterrupt:
        sys.exit('\nInterrupted by user')