from umi10dof import UMI10DOF

imu = UMI10DOF()


def get_telemetry():
    data = imu.read()

    ax, ay, az = data.accel
    gx, gy, gz = data.gyro
    mx, my, mz = data.mag

    return {
        "imu": {
            "acceleration": {
                "x": ax,
                "y": ay,
                "z": az
            },

            "gyro": {
                "x": gx,
                "y": gy,
                "z": gz
            },

            "magnetic": {
                "x": mx,
                "y": my,
                "z": mz
            },

            "pressure": data.pressure
        }
    }