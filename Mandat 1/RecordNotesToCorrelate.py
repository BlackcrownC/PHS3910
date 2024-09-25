import RecordMicro
import PlayNotesV2 as PlayNotes

recorder = RecordMicro.RecordMicro()
playNotes = PlayNotes.PlayNotes()

number_of_times = 5

def record_and_save(name, time):
    try:
        print(f"Record time {time}")
        t, recording = recorder.record()
        norm_recording = RecordMicro.normalize(recording)
        peak = recorder.find_highest_peak(t, norm_recording, filename=name)
        recorder.save_peak(peak, name, time)
    except:
        print(f"Error in record_and_save for {name} time {time}")
        record_and_save(name, time)

for name in playNotes.keys_name:
    print(f"Time to learn note {name}")

    for i in range(1, number_of_times + 1):
        record_and_save(name, i)
