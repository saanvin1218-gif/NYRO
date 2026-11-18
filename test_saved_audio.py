
import json
import wave
import vosk

MODEL_PATH = "vosk-model-small-en-us-0.15"
AUDIO_PATH = "nyro_live_test.wav"

model = vosk.Model(MODEL_PATH)

with wave.open(AUDIO_PATH, "rb") as audio:
    recognizer = vosk.KaldiRecognizer(
        model,
        audio.getframerate()
    )

    while True:
        data = audio.readframes(4000)

        if not data:
            break

        recognizer.AcceptWaveform(data)

result = json.loads(recognizer.FinalResult())

print("Vosk recognised:", result.get("text"))
