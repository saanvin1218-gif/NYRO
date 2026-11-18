def process_power_command(command, devices):

    if command in ["power outage", "power off"]:

        if devices["mains_present"] is False:
            return "Power is already unavailable."

        devices["mains_present"] = False

        return (
            "Warning! Power outage detected in your room."
        )

    elif command in ["power restored", "power on"]:

        if devices["mains_present"] is True:
            return "Power is already available."

        devices["mains_present"] = True

        return (
            "Power restored! Your room has electricity again."
        )

    return None