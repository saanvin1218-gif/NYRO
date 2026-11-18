
from commands import (
    process_command,
    restore_context,
    get_context,
    clear_pending_confirmation,
)
from voice import wait_for_wake_word, listen, speak
from memory import load_memory, save_memory


SLEEP_COMMANDS = {
    "go to sleep",
    "sleep",
    "stop listening",
}

STOP_COMMANDS = {
    "stop",
    "stop nyro",
    "shut down",
    "shutdown",
    "exit",
    "quit",
}


def main():
    print("==============================")
    print("          NYRO SYSTEM")
    print("==============================")

    memory = load_memory()
    devices = memory["devices"]
    restore_context(memory["conversation"])

    def update_memory():
        memory["devices"] = devices.copy()
        memory["conversation"] = get_context()
        save_memory(memory)

    speak("Hello! I am Nyro. Your offline room assistant is ready.")

    try:
        while True:
            # WAIT FOR THE WAKE PHRASE
            wait_for_wake_word()

            speak("Yes? I'm listening.")

            # ACTIVE CONVERSATION SESSION
            while True:
                command = listen()

                if not command:
                    speak("Sorry, I couldn't understand that. Please try again.")
                    continue

                cleaned_command = command.lower().strip()
                cleaned_command = cleaned_command.rstrip(" .!?")

                # END THE SESSION AND RETURN TO SLEEP
                if cleaned_command in SLEEP_COMMANDS:
                    clear_pending_confirmation()
                    update_memory()
                    speak("Okay. I'll go to sleep. Say Nyro, listen when you need me.")
                    break

                # COMPLETELY SHUT DOWN NYRO
                if cleaned_command in STOP_COMMANDS:
                    speak("Shutting down. Goodbye!")
                    return

                # PROCESS NORMAL COMMANDS
                response, should_exit = process_command(command, devices)

                update_memory()
                speak(response)

                if should_exit:
                    return

    except KeyboardInterrupt:
        print("\nNyro was stopped from the keyboard.")

    except Exception as error:
        print(f"Nyro encountered an unexpected error: {error}")
        speak("I encountered a problem and need to stop.")

    finally:
        clear_pending_confirmation()
        update_memory()
        print("Nyro memory saved successfully.")


if __name__ == "__main__":
    main()
