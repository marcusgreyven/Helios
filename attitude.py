import math
import threading
import time


class AttitudeEstimator:

    STANDARD_GRAVITY = 9.80665


    def __init__(
        self,
        alpha=0.98
    ):

        self.alpha = alpha

        self.lock = (
            threading.Lock()
        )

        self.initialized = False

        self.roll = 0.0
        self.pitch = 0.0

        self.last_time = None


    @staticmethod
    def _wrap_angle(
        angle
    ):

        while angle > 180.0:
            angle -= 360.0

        while angle < -180.0:
            angle += 360.0

        return angle


    def update(
        self,
        acceleration,
        angular_rate
    ):

        now = (
            time.monotonic()
        )

        ax = float(
            acceleration["x"]
        )

        ay = float(
            acceleration["y"]
        )

        az = float(
            acceleration["z"]
        )

        gx = float(
            angular_rate["x"]
        )

        gy = float(
            angular_rate["y"]
        )

        gz = float(
            angular_rate["z"]
        )


        acceleration_magnitude = (
            math.sqrt(
                ax * ax
                + ay * ay
                + az * az
            )
        )


        roll_acc = (
            math.degrees(
                math.atan2(
                    ay,
                    az
                )
            )
        )

        pitch_acc = (
            math.degrees(
                math.atan2(
                    -ax,
                    math.sqrt(
                        ay * ay
                        + az * az
                    )
                )
            )
        )


        rate_magnitude = (
            math.sqrt(
                gx * gx
                + gy * gy
                + gz * gz
            )
        )


        acceleration_trusted = (
            0.75
            * self.STANDARD_GRAVITY
            <= acceleration_magnitude
            <= 1.25
            * self.STANDARD_GRAVITY
        )


        with self.lock:

            if (
                not self.initialized
                or self.last_time
                is None
            ):

                self.roll = (
                    roll_acc
                )

                self.pitch = (
                    pitch_acc
                )

                self.initialized = (
                    True
                )

            else:

                dt = (
                    now
                    - self.last_time
                )

                dt = max(
                    0.001,
                    min(
                        dt,
                        0.2
                    )
                )


                roll_gyro = (
                    self.roll
                    + gx * dt
                )

                pitch_gyro = (
                    self.pitch
                    + gy * dt
                )


                if acceleration_trusted:

                    self.roll = (
                        self.alpha
                        * roll_gyro
                        + (
                            1.0
                            - self.alpha
                        )
                        * roll_acc
                    )

                    self.pitch = (
                        self.alpha
                        * pitch_gyro
                        + (
                            1.0
                            - self.alpha
                        )
                        * pitch_acc
                    )

                else:

                    self.roll = (
                        roll_gyro
                    )

                    self.pitch = (
                        pitch_gyro
                    )


                self.roll = (
                    self._wrap_angle(
                        self.roll
                    )
                )

                self.pitch = (
                    self._wrap_angle(
                        self.pitch
                    )
                )


            self.last_time = now

            roll = self.roll
            pitch = self.pitch


        stable = (
            rate_magnitude
            < 2.0
            and abs(
                acceleration_magnitude
                - self.STANDARD_GRAVITY
            )
            < 0.8
        )


        return {
            "roll": roll,
            "pitch": pitch,

            # Без магнитометра абсолютный yaw
            # сейчас не определяем.
            "yaw": None,

            "rate_magnitude":
                rate_magnitude,

            "state":
                (
                    "STABLE"
                    if stable
                    else "DYNAMIC"
                ),

            "solution":
                "ROLL/PITCH",

            "reference_frame":
                "SENSOR",

            "filter":
                "COMPLEMENTARY",

            "acceleration_trusted":
                acceleration_trusted
        }
