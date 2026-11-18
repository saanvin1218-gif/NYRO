from commands import process_command

devices = {"lights": False, "fan": False, "mains_present": True}

tests = [
    "please turn on the lights",
    "could you switch off the fan",
    "turn on the lights and fan",
    "turn on the lights actually turn them off",
    "turn on the lights",
    "turn them off",
    "what's the status of my room",
    "what is the current status of the lights",
    "check the fans status",
    "turn on the lights and turn off the fan",
    "switch off the lights but keep the fan on",
    "turn everything off",
    "turn on the fan",
    "turn it off",
    "turn on the lights and fan",
    "turn them off",
    "turn the lights and fan on",
    "turn on the lights and fan",
    "turn the lights off and the fan on",
]

print("\n========== NYRO UNDERSTANDING TEST ==========\n")
for command in tests:
    print("\nInput:", command)
    response, should_exit = process_command(command, devices)
    print("Nyro:", response)
    print("Device states:", devices)
print("\n========== TEST FINISHED ==========")
