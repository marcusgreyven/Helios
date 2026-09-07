from datetime import datetime
from pathlib import Path

from picamera2 import Picamera2


class HeliosCamera:

    def __init__(self, capture_dir="captures"):
        self.capture_dir = Path(capture_dir)
        self.capture_dir.mkdir(parents=True, exist_ok=True)

        self.camera = Picamera2()

        config = self.camera.create_still_configuration(
            main={"size": (1920, 1080)}
        )

        self.camera.configure(config)
        self.camera.start()

    def capture(self):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        filename = f"helios_{timestamp}.jpg"
        path = self.capture_dir / filename

        self.camera.capture_file(str(path))

        return filename