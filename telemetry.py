import math

from imu import HeliosIMU


STANDARD_GRAVITY = 9.80665

imu = HeliosIMU()


def get_telemetry():

    data = imu.read()

    acceleration = data["acceleration"]

    ax = acceleration["x"]
    ay = acceleration["y"]
    az = acceleration["z"]

    acceleration_magnitude = math.sqrt(
        ax * ax +
        ay * ay +
        az * az
    )

    acceleration_g = (
        acceleration_magnitude
        / STANDARD_GRAVITY
    )

    return {
        "imu": {

            "acceleration": {
                "x": ax,
                "y": ay,
                "z": az,

                "magnitude":
                    acceleration_magnitude,

                "g":
                    acceleration_g
            },

            "angular_rate":
                data["angular_rate"],

            "magnetic_field": {
                "x": None,
                "y": None,
                "z": None
            },

            "pressure":
                data["pressure"]
        }
    }