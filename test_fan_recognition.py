
import sounddevice as sd
import numpy as np
import wave
import json
from vosk import Model, KaldiRecognizer

print("Loading Vosk...")
model = Model("vosk-model-small-en-us-0.15")

print("Say: FAN")
audio = sd.rec(
    3 * 16000,
    samplerate=16000,
    channels=1,
    dtype="int16",
    device=1
)
sd.wait()

with wave.open("fan_test.wav", "wb") as f:
    f.setnchannels(1)
    f.setsampwidth(2)
    f.setframerate(16000)
    f.writeframes(audio.tobytes())

recognizer = KaldiRecognizer(model, 16000)
recognizer.AcceptWaveform(audio.tobytes())

result = json.loads(recognizer.FinalResult())
print("Vosk recognised:", result.get("text"))

