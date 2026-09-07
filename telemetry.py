from imu import HeliosIMU


imu = HeliosIMU()


def get_telemetry():
    data = imu.read()

    return {
        "imu": {
            "acceleration": data["acceleration"],

            "gyro": data["gyro"],

            # Магнитометр пока не определяется по I2C
            "magnetic": {
                "x": None,
                "y": None,
                "z": None
            },

            "pressure": data["pressure"]
        }
    }