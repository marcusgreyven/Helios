import math

from attitude import AttitudeEstimator
from imu import HeliosIMU


STANDARD_GRAVITY = 9.80665


imu = HeliosIMU()

attitude_estimator = (
    AttitudeEstimator(
        alpha=0.98
    )
)


def get_telemetry():

    data = imu.read()

    acceleration = (
        data["acceleration"]
    )

    angular_rate = (
        data["angular_rate"]
    )


    ax = acceleration["x"]
    ay = acceleration["y"]
    az = acceleration["z"]


    acceleration_magnitude = (
        math.sqrt(
            ax * ax
            + ay * ay
            + az * az
        )
    )


    acceleration_g = (
        acceleration_magnitude
        / STANDARD_GRAVITY
    )


    attitude = (
        attitude_estimator.update(
            acceleration,
            angular_rate
        )
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
                angular_rate,

            "magnetic_field": {
                "x": None,
                "y": None,
                "z": None
            },

            "pressure":
                data["pressure"]
        },

        "attitude":
            attitude
    }
