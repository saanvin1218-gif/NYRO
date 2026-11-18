from understanding import NyroUnderstanding
from powerwatch import process_power_command

brain = NyroUnderstanding()


def restore_context(context):
    brain.last_devices = [
        item for item in context.get("last_devices", [])
        if item in ("lights", "fan")
    ]
    brain.last_action = context.get("last_action") if context.get("last_action") in ("on", "off") else None
    # An unfinished confirmation is deliberately never restored.
    brain.pending_action = None
    print("Nyro's conversational context restored.")


def get_context():
    return {
        "last_devices": brain.last_devices.copy(),
        "last_action": brain.last_action,
    }


def clear_pending_confirmation():
    brain.pending_action = None


def apply_action(action, devices):
    if action == "lights_on":
        devices["lights"] = True
        return "Lights turned ON."
    if action == "study_mode":
        devices["lights"] = True
        devices["fan"] = True
        return "Study mode activated."
    if action == "good_night":
        devices["lights"] = False
        devices["fan"] = False
        return "Good night! Nyro is standing by."
    return "I don't know how to perform that action yet."


def get_room_status(devices):
    lights = "ON" if devices["lights"] else "OFF"
    fan = "ON" if devices["fan"] else "OFF"
    power = "AVAILABLE" if devices["mains_present"] else "OUTAGE"
    return f"Room status: Lights {lights}, Fan {fan}, Power {power}."


def process_command(command, devices):
    result = brain.understand(command)
    kind = result["type"]

    if kind == "greeting":
        return "Hello! How can I help?", False

    if kind == "device_action":
        state = result["state"]
        for device in result["devices"]:
            devices[device] = state
        names = " and ".join(device.capitalize() for device in result["devices"])
        return f"{names} turned {'ON' if state else 'OFF'}.", False

    if kind == "multiple_device_actions":
        responses = []
        for device, state in result["actions"].items():
            devices[device] = state
            responses.append(f"{device.capitalize()} turned {'ON' if state else 'OFF'}.")
        return " ".join(responses), False

    if kind in {"confirmation", "cancel", "clarification"}:
        return result["message"], False

    if kind in {"confirmed_action", "direct_mode"}:
        return apply_action(result["action"], devices), False

    if kind == "status":
        return get_room_status(devices), False

    if kind == "power":
        return process_power_command(result["command"], devices), False

    if kind == "exit":
        return "Shutting down. Goodbye!", True

    return "Sorry, I don't understand that yet. Could you say it another way?", False
