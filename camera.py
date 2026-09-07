import json
import threading
import time

from datetime import datetime, timezone
from pathlib import Path

from picamera2 import Picamera2


class HeliosCamera:

    def __init__(self, capture_dir):

        self.capture_dir = Path(capture_dir)

        self.capture_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.lock = threading.Lock()

        self.camera = Picamera2()

        # Максимальное нативное разрешение OV5647
        self.resolution = (2592, 1944)

        configuration = (
            self.camera
            .create_still_configuration(
                main={
                    "size": self.resolution,
                    "format": "RGB888"
                }
            )
        )

        self.camera.configure(
            configuration
        )

        # Максимальное рекомендуемое JPEG quality
        self.camera.options["quality"] = 95

        self.camera.start()

        # Даём автоэкспозиции и балансу белого стабилизироваться
        time.sleep(2)


    def capture(self, telemetry):

        with self.lock:

            now = datetime.now(
                timezone.utc
            )

            timestamp_file = (
                now.strftime(
                    "%Y%m%dT%H%M%S_%fZ"
                )
            )

            frame_id = (
                f"HLS-CAM-{timestamp_file}"
            )

            image_filename = (
                f"{frame_id}.jpg"
            )

            metadata_filename = (
                f"{frame_id}.json"
            )

            image_path = (
                self.capture_dir
                / image_filename
            )

            metadata_path = (
                self.capture_dir
                / metadata_filename
            )

            camera_metadata = (
                self.camera.capture_file(
                    str(image_path)
                )
            )

            metadata = {
                "frame_id": frame_id,

                "filename":
                    image_filename,

                "captured_at":
                    now.isoformat(),

                "camera": {
                    "sensor": "OV5647",

                    "resolution": {
                        "width":
                            self.resolution[0],

                        "height":
                            self.resolution[1]
                    },

                    "metadata":
                        camera_metadata
                },

                "telemetry":
                    telemetry
            }

            with metadata_path.open(
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    metadata,
                    file,
                    ensure_ascii=False,
                    indent=2,
                    default=str
                )

            return {
                "frame_id":
                    frame_id,

                "filename":
                    image_filename,

                "url":
                    f"/captures/{image_filename}",

                "captured_at":
                    now.isoformat(),

                "resolution": {
                    "width":
                        self.resolution[0],

                    "height":
                        self.resolution[1]
                },

                "telemetry":
                    telemetry
            }


    def list_frames(self):

        images = sorted(
            self.capture_dir.glob(
                "*.jpg"
            ),

            key=lambda image:
                image.stat().st_mtime,

            reverse=True
        )

        frames = []

        for image in images:

            metadata_path = (
                image.with_suffix(
                    ".json"
                )
            )

            metadata = None

            if metadata_path.exists():

                try:

                    with metadata_path.open(
                        "r",
                        encoding="utf-8"
                    ) as file:

                        metadata = (
                            json.load(file)
                        )

                except Exception:
                    metadata = None

            frame = {
                "frame_id":
                    image.stem,

                "filename":
                    image.name,

                "url":
                    f"/captures/{image.name}"
            }

            if metadata:
                frame.update(
                    metadata
                )

            frames.append(
                frame
            )

        return frames