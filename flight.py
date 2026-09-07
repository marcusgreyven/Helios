import threading


class FlightController:

    VALID_MODES = {
        "BOOT",
        "STANDBY",
        "NOMINAL",
        "PAYLOAD",
        "SAFE"
    }

    TRANSITIONS = {
        "BOOT": {
            "STANDBY",
            "SAFE"
        },

        "STANDBY": {
            "NOMINAL",
            "SAFE"
        },

        "NOMINAL": {
            "STANDBY",
            "PAYLOAD",
            "SAFE"
        },

        "PAYLOAD": {
            "NOMINAL",
            "SAFE"
        },

        "SAFE": {
            "STANDBY"
        }
    }


    def __init__(
        self,
        event_log
    ):

        self.event_log = (
            event_log
        )

        self.lock = (
            threading.RLock()
        )

        self._mode = "BOOT"

        self.event_log.add(
            "FC",
            "FLIGHT COMPUTER INITIALIZED"
        )

        self.event_log.add(
            "MODE",
            "BOOT ENTERED"
        )


    @property
    def mode(self):

        with self.lock:
            return self._mode


    def set_mode(
        self,
        new_mode,
        reason=None
    ):

        new_mode = (
            str(new_mode)
            .upper()
            .strip()
        )

        if (
            new_mode
            not in self.VALID_MODES
        ):
            raise ValueError(
                f"Unknown flight mode: "
                f"{new_mode}"
            )

        with self.lock:

            current = self._mode

            if new_mode == current:
                return current

            allowed = (
                self.TRANSITIONS[
                    current
                ]
            )

            if new_mode not in allowed:
                raise ValueError(
                    f"Invalid transition: "
                    f"{current} -> {new_mode}"
                )

            self._mode = (
                new_mode
            )

        message = (
            f"{current} -> {new_mode}"
        )

        if reason:
            message += (
                f" / {reason}"
            )

        level = (
            "WARN"
            if new_mode == "SAFE"
            else "INFO"
        )

        self.event_log.add(
            "MODE",
            message,
            level
        )

        return new_mode


    def enter_safe(
        self,
        reason
    ):

        with self.lock:

            if self._mode == "SAFE":
                return "SAFE"

        return self.set_mode(
            "SAFE",
            reason=reason
        )
