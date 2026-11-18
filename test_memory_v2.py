
from commands import process_command

devices = {
    "lights": False,
    "fan": False,
    "mains_present": True
}

test_commands = [

    "turn on the lights and fan",
    "turn them off",

    "turn on the lights",
    "turn the other one on",

    "turn on the lights and fan",
    "turn it off",

    "study mode",
    "turn them off",

]

for command in test_commands:

    print("\n" + "=" * 40)
    print("You:", command)

    response, should_exit = process_command(
        command,
        devices
    )

    print("Nyro:", response)
    print("Devices:", devices)
