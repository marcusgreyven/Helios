import struct
import time

from smbus2 import SMBus


class HeliosIMU:
    # I2C addresses
    ACCEL_ADDR = 0x18
    GYRO_ADDR = 0x68
    BARO_ADDR = 0x5C

    G = 9.80665

    def __init__(self, bus_number=1):
        self.bus = SMBus(bus_number)

        self._check_devices()
        self._configure()

    def _check_devices(self):
        accel_id = self.bus.read_byte_data(self.ACCEL_ADDR, 0x0F)
        gyro_id = self.bus.read_byte_data(self.GYRO_ADDR, 0x0F)
        baro_id = self.bus.read_byte_data(self.BARO_ADDR, 0x0F)

        if accel_id != 0x32:
            raise RuntimeError(
                f"LIS331DLH not detected correctly: 0x{accel_id:02X}"
            )

        if gyro_id != 0xD3:
            raise RuntimeError(
                f"I3G4250D not detected correctly: 0x{gyro_id:02X}"
            )

        if baro_id != 0xBD:
            raise RuntimeError(
                f"LPS25HB not detected correctly: 0x{baro_id:02X}"
            )

    def _configure(self):
        # LIS331DLH
        # Normal mode, 50 Hz, X/Y/Z enabled
        self.bus.write_byte_data(
            self.ACCEL_ADDR,
            0x20,
            0x27
        )

        # BDU enabled, ±2 g
        self.bus.write_byte_data(
            self.ACCEL_ADDR,
            0x23,
            0x80
        )

        # I3G4250D
        # Normal mode, 100 Hz, X/Y/Z enabled
        self.bus.write_byte_data(
            self.GYRO_ADDR,
            0x20,
            0x0F
        )

        # ±245 deg/s
        self.bus.write_byte_data(
            self.GYRO_ADDR,
            0x23,
            0x00
        )

        # LPS25HB
        # Active, 7 Hz, BDU enabled
        self.bus.write_byte_data(
            self.BARO_ADDR,
            0x20,
            0xA4
        )

        time.sleep(0.1)

    def read_acceleration(self):
        data = self.bus.read_i2c_block_data(
            self.ACCEL_ADDR,
            0x28 | 0x80,
            6
        )

        x, y, z = struct.unpack("<hhh", bytes(data))

        # LIS331DLH: 12-bit value stored left-aligned
        x >>= 4
        y >>= 4
        z >>= 4

        # ±2g: ~1 mg/digit
        x_g = x * 0.001
        y_g = y * 0.001
        z_g = z * 0.001

        return {
            "x": x_g * self.G,
            "y": y_g * self.G,
            "z": z_g * self.G
        }

    def read_gyro(self):
        data = self.bus.read_i2c_block_data(
            self.GYRO_ADDR,
            0x28 | 0x80,
            6
        )

        x, y, z = struct.unpack("<hhh", bytes(data))

        # ±245 dps -> 8.75 mdps/LSB
        sensitivity = 0.00875

        return {
            "x": x * sensitivity,
            "y": y * sensitivity,
            "z": z * sensitivity
        }

    def read_pressure(self):
        data = self.bus.read_i2c_block_data(
            self.BARO_ADDR,
            0x28 | 0x80,
            3
        )

        raw = (
            data[0]
            | (data[1] << 8)
            | (data[2] << 16)
        )

        if raw & 0x800000:
            raw -= 1 << 24

        return raw / 4096.0

    def read(self):
        return {
            "acceleration": self.read_acceleration(),
            "gyro": self.read_gyro(),
            "pressure": self.read_pressure()
        }

    def close(self):
        self.bus.close()