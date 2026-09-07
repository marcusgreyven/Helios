import json
import shutil
import threading
import time

from datetime import datetime, timezone
from pathlib import Path

from picamera2 import Picamera2


class HeliosCamera:

    SENSOR = "OV5647"

    RESOLUTION = (
        2592,
        1944
    )


    def __init__(
        self,
        capture_dir
    ):

        self.capture_dir = Path(
            capture_dir
        )

        self.capture_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.lock = (
            threading.Lock()
        )

        self.camera = (
            Picamera2()
        )

        configuration = (
            self.camera
            .create_still_configuration(
                main={
                    "size":
                        self.RESOLUTION,

                    "format":
                        "RGB888"
                }
            )
        )

        self.camera.configure(
            configuration
        )

        self.camera.options[
            "quality"
        ] = 95

        self.camera.start()

        # AE / AWB stabilization
        time.sleep(2)


    def capture(
        self,
        telemetry
    ):

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
                "HLS-CAM-"
                + timestamp_file
            )

            image_filename = (
                frame_id
                + ".jpg"
            )

            metadata_filename = (
                frame_id
                + ".json"
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
                "frame_id":
                    frame_id,

                "filename":
                    image_filename,

                "captured_at":
                    now.isoformat(),

                "camera": {
                    "sensor":
                        self.SENSOR,

                    "resolution": {
                        "width":
                            self.RESOLUTION[0],

                        "height":
                            self.RESOLUTION[1]
                    },

                    "jpeg_quality":
                        95
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
                **metadata,

                "url":
                    "/captures/"
                    + image_filename
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
                    "/captures/"
                    + image.name
            }


            if metadata:

                frame.update(
                    metadata
                )

                frame["url"] = (
                    "/captures/"
                    + image.name
                )


            frames.append(
                frame
            )


        return frames


    def get_status(self):

        images = list(
            self.capture_dir.glob(
                "*.jpg"
            )
        )

        metadata_files = list(
            self.capture_dir.glob(
                "*.json"
            )
        )


        archive_bytes = 0

        for file in (
            images
            + metadata_files
        ):

            try:

                archive_bytes += (
                    file.stat()
                    .st_size
                )

            except OSError:
                pass


        last_frame = None

        if images:

            newest = max(
                images,
                key=lambda image:
                    image.stat().st_mtime
            )

            last_frame = {
                "filename":
                    newest.name,

                "timestamp":
                    datetime.fromtimestamp(
                        newest.stat().st_mtime,
                        tz=timezone.utc
                    ).isoformat()
            }


        disk = shutil.disk_usage(
            self.capture_dir
        )


        return {
            "sensor":
                self.SENSOR,

            "resolution": {
                "width":
                    self.RESOLUTION[0],

                "height":
                    self.RESOLUTION[1]
            },

            "frame_count":
                len(images),

            "archive_bytes":
                archive_bytes,

            "disk": {
                "total_bytes":
                    disk.total,

                "used_bytes":
                    disk.used,

                "free_bytes":
                    disk.free
            },

            "last_frame":
                last_frame
        }


    def clear_archive(self):

        with self.lock:

            image_files = list(
                self.capture_dir.glob(
                    "*.jpg"
                )
            )

            metadata_files = list(
                self.capture_dir.glob(
                    "*.json"
                )
            )


            deleted_frames = (
                len(image_files)
            )

            deleted_files = 0
            freed_bytes = 0


            for file in (
                image_files
                + metadata_files
            ):

                try:

                    freed_bytes += (
                        file.stat()
                        .st_size
                    )

                    file.unlink()

                    deleted_files += 1

                except FileNotFoundError:
                    pass


            return {
                "deleted_frames":
                    deleted_frames,

                "deleted_files":
                    deleted_files,

                "freed_bytes":
                    freed_bytes
            }