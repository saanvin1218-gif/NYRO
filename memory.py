import json
import os

MEMORY_FILE = "nyro_memory.json"


def default_memory():
    return {
        "devices": {"lights": False, "fan": False, "mains_present": True},
        "conversation": {"last_devices": [], "last_action": None},
    }


def load_memory():
    if not os.path.exists(MEMORY_FILE):
        print("No previous memory found. Starting fresh.")
        return default_memory()

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file:
            saved = json.load(file)

        memory = default_memory()
        if not isinstance(saved, dict):
            raise ValueError("Memory root must be an object.")

        saved_devices = saved.get("devices", {})
        if isinstance(saved_devices, dict):
            for key in memory["devices"]:
                value = saved_devices.get(key)
                if isinstance(value, bool):
                    memory["devices"][key] = value

        conversation = saved.get("conversation", {})
        if isinstance(conversation, dict):
            last_devices = conversation.get("last_devices", [])
            if isinstance(last_devices, list):
                memory["conversation"]["last_devices"] = [
                    d for d in last_devices if d in ("lights", "fan")
                ]
            last_action = conversation.get("last_action")
            if last_action in ("on", "off"):
                memory["conversation"]["last_action"] = last_action

        print("Nyro's previous memory loaded.")
        return memory

    except (json.JSONDecodeError, OSError, ValueError, TypeError):
        print("Memory could not be loaded. Starting fresh.")
        return default_memory()


def save_memory(memory):
    temporary_file = MEMORY_FILE + ".tmp"
    try:
        with open(temporary_file, "w", encoding="utf-8") as file:
            json.dump(memory, file, indent=4)
            file.flush()
            os.fsync(file.fileno())
        os.replace(temporary_file, MEMORY_FILE)
        print("Nyro's memory saved.")
    except OSError as error:
        print(f"Warning: Nyro could not save memory: {error}")
        try:
            if os.path.exists(temporary_file):
                os.remove(temporary_file)
        except OSError:
            pass
