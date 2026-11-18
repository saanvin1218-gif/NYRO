"""Quick offline regression checks. No microphone or real appliances are used."""

from commands import brain, process_command

def run(command, initial=None, context=None):
    devices = {
        "lights": False,
        "fan": False,
        "mains_present": True,
    }
    if initial:
        devices.update(initial)
    if context is not None:
        brain.last_devices = list(context)
    response, should_exit = process_command(command, devices)
    assert should_exit is False
    return response, devices

# Shared action across two devices, both common word orders.
response, state = run("turn on the lights and fan")
assert state["lights"] is True and state["fan"] is True
response, state = run("turn the lights and fan on")
assert state["lights"] is True and state["fan"] is True

# Explicit mixed actions.
response, state = run("turn on the lights and turn off the fan")
assert state["lights"] is True and state["fan"] is False
response, state = run("turn the lights off and the fan on")
assert state["lights"] is False and state["fan"] is True

# Contextual references.
response, state = run("turn them off", context=["lights", "fan"])
assert state["lights"] is False and state["fan"] is False
response, state = run("turn it off", context=["fan"])
assert state["fan"] is False

# Group action and ambiguous group command.
response, state = run("turn everything on")
assert state["lights"] is True and state["fan"] is True
response, state = run("turn everything")
assert "on or off" in response.lower()
assert state["lights"] is False and state["fan"] is False

# Confirmation flow.
response, state = run("it's dark in here")
assert "would you like" in response.lower()
response, state = run("yes")
assert state["lights"] is True

# PowerWatch remains simulation-only.
response, state = run("power outage")
assert state["mains_present"] is False
response, state = run("power restored", initial={"mains_present": False})
assert state["mains_present"] is True

print("All Nyro regression checks passed.")
