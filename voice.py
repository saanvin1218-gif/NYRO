
import json
import wave

import pyttsx3
import sounddevice as sd
import vosk


MODEL_PATH = "vosk-model-small-en-us-0.15"
MICROPHONE_ID = 1
SAMPLE_RATE = 16000
WAKE_PHRASE = "nyro listen"

RECORD_SECONDS = 6
BLOCK_SIZE = 4000

print("Loading Nyro voice model...")
model = vosk.Model(MODEL_PATH)
print("Nyro voice model ready!")


def speak(text):
    print("Nyro:", text)

    engine = pyttsx3.init()
    engine.setProperty("rate", 170)
    engine.setProperty("volume", 1.0)

    engine.say(text)
    engine.runAndWait()
    engine.stop()
    del engine


def wait_for_wake_word():
    print("\nWaiting for 'Nyro, listen'...")

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)

    wake_names = (
        "nyro",
        "nairo",
        "nero",
        "nairobi",
        "neuro",
        "night or",
    )

    committed_text = ""

    with sd.RawInputStream(
        samplerate=SAMPLE_RATE,
        blocksize=BLOCK_SIZE,
        device=MICROPHONE_ID,
        dtype="int16",
        channels=1,
    ) as stream:

        while True:
            audio, overflowed = stream.read(BLOCK_SIZE)
            audio_bytes = bytes(audio)

            if recognizer.AcceptWaveform(audio_bytes):
                result = json.loads(recognizer.Result())
                phrase = result.get("text", "").lower()

                if phrase:
                    committed_text = (
                        committed_text + " " + phrase
                    ).strip()

                    # Keep only recent recognised words.
                    committed_text = " ".join(
                        committed_text.split()[-8:]
                    )

                partial_text = ""

            else:
                result = json.loads(recognizer.PartialResult())
                partial_text = result.get("partial", "").lower()

            candidate = (
                committed_text + " " + partial_text
            ).strip()

            name_found = any(
                name in candidate for name in wake_names
            )

            if name_found and "listen" in candidate:
                print("Nyro wake phrase detected!")
                return


def listen(max_seconds=RECORD_SECONDS):
    """Capture a fixed-length recording for speech recognition."""

    print("\nNyro is listening... Speak now!")

    recognizer = vosk.KaldiRecognizer(model, SAMPLE_RATE)
    frames = []

    try:
        with sd.RawInputStream(
            samplerate=SAMPLE_RATE,
            blocksize=BLOCK_SIZE,
            device=MICROPHONE_ID,
            dtype="int16",
            channels=1,
        ) as stream:

            total_blocks = int(
                SAMPLE_RATE * max_seconds / BLOCK_SIZE
            )

            for _ in range(total_blocks):
                data, overflowed = stream.read(BLOCK_SIZE)
                chunk = bytes(data)

                frames.append(chunk)
                recognizer.AcceptWaveform(chunk)

    except sd.PortAudioError as error:
        print(f"Microphone error: {error}")
        return ""

    print("Processing your voice...")

    # Save the exact audio captured by Nyro.
    with wave.open("nyro_live_test.wav", "wb") as audio_file:
        audio_file.setnchannels(1)
        audio_file.setsampwidth(2)
        audio_file.setframerate(SAMPLE_RATE)
        audio_file.writeframes(b"".join(frames))

    print("Live recording saved as nyro_live_test.wav")

    result = json.loads(recognizer.FinalResult())
    recognized = result.get("text", "").strip()

    if recognized:
        print("Nyro heard:", recognized)
    else:
        print("Sorry, I couldn't understand that.")

    return recognized


if __name__ == "__main__":
    speak(
        "Hello! I am Nyro. "
        "Your offline room assistant is ready."
    )
