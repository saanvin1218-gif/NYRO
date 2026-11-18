
from commands import process_command

devices = {
    "lights": False,
    "fan": False,
    "mains_present": True
}

test_commands = [

    # Natural language
    "could you please switch on the lights",
    "can you turn the fan off",

    # Context memory
    "actually turn them off",

    # Multiple devices
    "turn the lights and fan on",

    # Possible intentions and confirmation
    "it's dark in here",
    "yes",

    # Good Night mode
    "I'm going to sleep",
    "no",

    # Study mode
    "I need to concentrate",
    "go ahead",

    # Cancellation
    "it's dark in here",
    "never mind",

    # Room status
    "what's happening in my room"
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
