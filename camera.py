import json
import threading

from datetime import datetime, timezone
from pathlib import Path

from picamera2 import Picamera2


class HeliosCamera:

    def __init__(self, capture_dir):

        self.capture_dir = Path(
            capture_dir
        )

        self.capture_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.lock = threading.Lock()

        self.camera = Picamera2()

        configuration = (
            self.camera
            .create_still_configuration(
                main={
                    "size": (1920, 1080)
                }
            )
        )

        self.camera.configure(
            configuration
        )

        self.camera.start()


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


            self.camera.capture_file(
                str(image_path)
            )


            metadata = {
                "frame_id": frame_id,

                "filename":
                    image_filename,

                "captured_at":
                    now.isoformat(),

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
                    indent=2
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