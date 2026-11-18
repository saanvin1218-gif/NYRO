# NYRO — Offline Room Assistant

Nyro is a Python-based offline voice-controlled room assistant prototype.

## Features

- Offline speech recognition with Vosk
- Wake phrase detection: "Nyro, listen"
- Spoken responses using pyttsx3
- Simulated lights and fan commands
- Room status reporting
- PowerWatch simulation
- Natural-language command understanding
- Contextual references such as "it", "them", and "the other one"
- Corrections such as "actually"
- Study Mode and Good Night mode
- Confirmation and cancellation handling
- Persistent device and conversation context

## Project files

- `main.py` — runs the voice assistant loop
- `voice.py` — wake phrase, microphone recording, speech output
- `commands.py` — connects understanding to device-state actions
- `understanding.py` — interprets commands
- `memory.py` — loads and saves local memory
- `powerwatch.py` — simulated power status
- `nyro_memory.json` — saved local state
- `test_understanding.py` — command tests
- `test_system.py` — integration-style command test
- `test_memory_v2.py` — context reference test

## Requirements

Use Python 3.11. Install these packages inside the project's virtual environment:

    pip install vosk sounddevice numpy pyttsx3

Download and extract the Vosk small English model into the project folder. The folder should be named:

    vosk-model-small-en-us-0.15

## Windows setup

Open PowerShell in the project folder:

    py -3.11 -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install vosk sounddevice numpy pyttsx3

If the virtual environment already exists and the packages are installed, do not recreate it.

## Microphone settings

The defaults in `voice.py` are:

- Microphone device index: `1`
- Sample rate: `16000 Hz`

If Nyro cannot access the microphone, check available devices with:

    python -c "import sounddevice as sd; print(sd.query_devices())"

Then update `MICROPHONE_ID` in `voice.py` to the correct input device index.

The silence detector has a starting RMS threshold. If it cuts off too early or waits too long, the `threshold` and `silence_seconds` values in `voice.py` may need microphone-specific adjustment.

## Run Nyro

Activate the environment, then run:

    python main.py

Say:

    Nyro, listen

Then wait for the listening acknowledgement and speak a command.

## Example commands

- Turn on the lights.
- Turn the fan off.
- Turn on the lights and fan.
- Turn the lights off and the fan on.
- Turn everything off.
- Turn them off.
- Turn it on.
- Turn the other one on.
- Actually, turn them off.
- It's too dark.
- I'm going to sleep.
- I need to concentrate.
- Study mode.
- Good night.
- What's my room status?
- Power outage.
- Power restored.
- Stop Nyro.

## Run tests

    python test_understanding.py
    python test_system.py
    python test_memory_v2.py

These tests change only an in-memory device dictionary unless the main program is running. They do not operate real appliances.

## Important safety and scope

**All device control and PowerWatch functions in this project are simulations.** No household electrical appliances are connected.

Do not connect this prototype directly to household mains electricity. Any future mains-powered installation must use suitable certified equipment and be designed and installed by a qualified adult electrician.

Nyro currently recognises a limited set of English commands. It is not a general-purpose conversational assistant.
