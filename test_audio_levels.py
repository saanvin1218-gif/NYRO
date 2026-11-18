
import sounddevice as sd
import numpy as np
import time

print("Testing microphone levels...")
print("First: stay silent for 5 seconds.")
print("Then: speak normally for 5 seconds.")

with sd.RawInputStream(
    samplerate=16000,
    blocksize=1600,
    device=1,
    dtype="int16",
    channels=1
) as stream:

    for i in range(10):
        data, overflowed = stream.read(1600)
        samples = np.frombuffer(bytes(data), dtype=np.int16)

        rms = np.sqrt(np.mean(samples.astype(np.float32) ** 2))

        print(f"Second {i + 1}: RMS = {rms:.2f}")
        time.sleep(0.0)
