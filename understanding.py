import re


class NyroUnderstanding:
    """Offline command parser for Nyro's lights/fan room prototype."""

    DEVICES = ("lights", "fan")

    def __init__(self):
        self.last_devices = []
        self.last_action = None
        self.pending_action = None

    def clean_text(self, text):
        text = str(text).lower().strip()
        text = text.replace("’", "'").replace("'", "")
        text = re.sub(r"[.!?,]+", " ", text)
        polite_phrases = (
            "could you please", "could you", "can you please", "can you",
            "would you please", "would you", "will you please", "will you",
            "please", "kindly", "for me",
        )
        for phrase in polite_phrases:
            text = re.sub(r"\b" + re.escape(phrase) + r"\b", " ", text)
        return re.sub(r"\s+", " ", text).strip()

    def find_devices(self, text):
        found = []
        if re.search(r"\blights?\b", text):
            found.append("lights")
        if re.search(r"\bfans?\b", text):
            found.append("fan")
        return found

    def handle_correction(self, text):
        matches = list(re.finditer(r"\b(actually|wait|instead|i mean|no)\b", text))
        if not matches:
            return text
        match = matches[-1]
        corrected = text[match.end():].strip()
        previous = text[:match.start()].strip()
        if not corrected or (match.group(1) == "no" and not previous):
            return text
        corrected_devices = self.find_devices(corrected)
        previous_devices = self.find_devices(previous)
        if corrected_devices:
            self.last_devices = corrected_devices
        elif previous_devices:
            self.last_devices = previous_devices
        print("Nyro understood a correction!")
        print("Final instruction:", corrected)
        return corrected

    def remember_action_devices(self, action):
        if action == "lights_on":
            self.last_devices, self.last_action = ["lights"], "on"
        elif action == "study_mode":
            self.last_devices, self.last_action = ["lights", "fan"], "on"
        elif action == "good_night":
            self.last_devices, self.last_action = ["lights", "fan"], "off"

    def resolve_reference(self, text):
        if re.search(r"\bthe other one\b", text):
            if len(self.last_devices) != 1:
                return None
            other = "fan" if self.last_devices[0] == "lights" else "lights"
            text = re.sub(r"\bthe other one\b", other, text)
            print("Nyro identified the other device:", other)

        if re.search(r"\bthem\b", text):
            if not self.last_devices:
                return None
            names = " and ".join(self.last_devices)
            text = re.sub(r"\bthem\b", names, text)
            print("Nyro remembered:", names)

        if re.search(r"\b(it|that)\b", text):
            if len(self.last_devices) != 1:
                return None
            device = self.last_devices[0]
            text = re.sub(r"\b(it|that)\b", device, text)
            print("Nyro remembered:", device)
        return text

    def is_yes(self, text):
        return text in {
            "yes", "yes please", "yeah", "yep", "sure", "go ahead",
            "do it", "of course", "absolutely", "okay", "ok",
        }

    def is_no(self, text):
        return text in {"no", "no thanks", "no thank you", "nope", "not now"}

    def is_cancel(self, text):
        return text in {
            "never mind", "nevermind", "cancel that", "cancel it",
            "dont do that", "do not do that", "forget it", "leave it",
        }

    def detect_intent(self, text):
        if re.search(r"\bits dark\b|\btoo dark\b|\bhard to see\b|\bcant see properly\b", text):
            return {
                "action": "lights_on",
                "question": "It's quite dark. Would you like me to turn on the lights?",
            }
        if re.search(r"\b(im going to sleep|i am going to sleep)\b|\bgoing to bed\b|\btime to sleep\b", text):
            return {
                "action": "good_night",
                "question": "Would you like me to activate Good Night mode?",
            }
        if re.search(r"\b(i need to|i have to|time to)\s+(study|concentrate|focus)\b|\bi need to concentrate\b|\bi need to focus\b", text):
            return {
                "action": "study_mode",
                "question": "Would you like me to activate Study mode?",
            }
        return None

    @staticmethod
    def _state_in_part(part):
        # Supports "turn on the lights", "switch the lights off", and "lights on".
        patterns = (
            (r"\b(?:turn|switch|put|keep|shut)\s+(?:the\s+)?on\b", True),
            (r"\b(?:turn|switch|put|keep|shut)\s+(?:the\s+)?off\b", False),
            (r"\b(?:turn|switch|put|keep)\s+(?:the\s+)?(?:lights?|fans?)\s+on\b", True),
            (r"\b(?:turn|switch|put|keep)\s+(?:the\s+)?(?:lights?|fans?)\s+off\b", False),
            (r"\bon\b", True),
            (r"\boff\b", False),
        )
        states = {state for pattern, state in patterns if re.search(pattern, part)}
        if len(states) == 1:
            return states.pop()
        if len(states) > 1:
            return "ambiguous"
        return None

    def detect_device_action(self, text):
        # Group commands.
        if re.search(r"\b(everything|all devices|all the devices)\b", text):
            state = self._state_in_part(text)
            if state is None or state == "ambiguous":
                return {"type": "clarification", "message": "Do you want everything on or off?"}
            self.last_devices = list(self.DEVICES)
            self.last_action = "on" if state else "off"
            return {"type": "device_action", "devices": list(self.DEVICES), "state": state}

        # Split only at conjunctions, then infer a shared state for device-only fragments.
        parts = re.split(r"\s+(?:and|but)\s+", text)
        parsed = []
        for part in parts:
            devices = self.find_devices(part)
            if devices:
                parsed.append({"devices": devices, "state": self._state_in_part(part)})

        if not parsed:
            return None

        if any(item["state"] == "ambiguous" for item in parsed):
            return {"type": "clarification", "message": "I'm not sure whether to turn that device on or off."}

        explicit_states = [item["state"] for item in parsed if item["state"] is not None]
        if not explicit_states:
            return {"type": "clarification", "message": "Would you like me to turn the devices on or off?"}

        # A command such as "turn on the lights and fan" or
        # "turn the lights and fan on" shares its one explicit state.
        if len(set(explicit_states)) == 1:
            shared_state = explicit_states[0]
            for item in parsed:
                if item["state"] is None:
                    item["state"] = shared_state
        else:
            # In mixed commands, an unlabelled fragment inherits the nearest explicit state.
            for index, item in enumerate(parsed):
                if item["state"] is None:
                    nearest = min(
                        (j for j, other in enumerate(parsed) if other["state"] is not None),
                        key=lambda j: abs(j - index),
                    )
                    item["state"] = parsed[nearest]["state"]

        actions = {}
        for item in parsed:
            for device in item["devices"]:
                actions[device] = item["state"]

        self.last_devices = list(actions)
        unique_states = set(actions.values())
        if len(unique_states) == 1:
            state = next(iter(unique_states))
            self.last_action = "on" if state else "off"
            return {"type": "device_action", "devices": list(actions), "state": state}

        self.last_action = None
        return {"type": "multiple_device_actions", "actions": actions}

    def understand(self, original_text):
        text = self.clean_text(original_text)
        if not text:
            return {"type": "unknown"}

        if self.is_cancel(text):
            if self.pending_action is not None:
                self.pending_action = None
                return {"type": "cancel", "message": "Okay, cancelled."}
            return {"type": "cancel", "message": "Nothing is pending."}

        if self.pending_action is not None:
            if self.is_yes(text):
                action = self.pending_action
                self.pending_action = None
                self.remember_action_devices(action)
                return {"type": "confirmed_action", "action": action}
            if self.is_no(text):
                self.pending_action = None
                return {"type": "cancel", "message": "Okay, I won't do that."}
            return {
                "type": "clarification",
                "message": "Please say yes or no, or say cancel.",
            }

        text = self.handle_correction(text)
        text = self.resolve_reference(text)
        if text is None:
            return {
                "type": "clarification",
                "message": "I'm not sure which device you mean. Do you mean the lights or the fan?",
            }

        if text in {"hi", "hello", "hey"}:
            return {"type": "greeting"}

        if (
            text in {
                "status", "room status", "check room status",
                "whats happening in my room", "what is happening in my room",
                "how is my room", "how are things in my room",
            }
            or re.search(
                r"\b(status|state)\b.*\b(room|lights?|fans?|devices)\b"
                r"|\b(room|lights?|fans?|devices)\b.*\b(status|state)\b",
                text,
            )
        ):
            return {"type": "status"}

        if text in {"power outage", "power off", "power restored", "power on"}:
            return {"type": "power", "command": text}

        if text in {"good night", "activate good night mode", "turn on good night mode"}:
            self.remember_action_devices("good_night")
            return {"type": "direct_mode", "action": "good_night"}

        if text in {"study mode", "activate study mode", "turn on study mode"}:
            self.remember_action_devices("study_mode")
            return {"type": "direct_mode", "action": "study_mode"}

        if text in {"exit", "shutdown", "shut down", "stop nyro"}:
            return {"type": "exit"}

        intent = self.detect_intent(text)
        if intent is not None:
            self.pending_action = intent["action"]
            return {"type": "confirmation", "message": intent["question"]}

        action = self.detect_device_action(text)
        if action is not None:
            return action

        return {"type": "unknown"}
