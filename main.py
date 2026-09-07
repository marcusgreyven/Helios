from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from telemetry import get_telemetry
from camera import HeliosCamera


BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"
TEMPLATES_DIR = BASE_DIR / "templates"
CAPTURES_DIR = BASE_DIR / "captures"

CAPTURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)


app = FastAPI(
    title="Helios Flight Control",
    version="0.3"
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static"
)

app.mount(
    "/captures",
    StaticFiles(directory=CAPTURES_DIR),
    name="captures"
)


templates = Jinja2Templates(
    directory=TEMPLATES_DIR
)


camera = None
camera_error = None

try:
    camera = HeliosCamera(
        CAPTURES_DIR
    )

except Exception as error:
    camera_error = str(error)


@app.get(
    "/",
    response_class=HTMLResponse
)
async def index(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/api/telemetry")
async def telemetry():

    timestamp = datetime.now(
        timezone.utc
    ).isoformat()

    try:

        data = get_telemetry()

        return {
            "status": "online",
            "vehicle": "HLS-01",
            "mode": "NOMINAL",
            "timestamp": timestamp,

            "systems": {
                "flight_computer": "NOMINAL",
                "accelerometer": "NOMINAL",
                "gyroscope": "NOMINAL",
                "magnetometer": "NO DATA",
                "barometer": "NOMINAL",
                "optical_payload":
                    "READY"
                    if camera is not None
                    else "FAULT"
            },

            **data
        }

    except Exception as error:

        return {
            "status": "error",
            "vehicle": "HLS-01",
            "mode": "DEGRADED",
            "timestamp": timestamp,
            "error": str(error),

            "systems": {
                "flight_computer": "NOMINAL",
                "accelerometer": "FAULT",
                "gyroscope": "FAULT",
                "magnetometer": "NO DATA",
                "barometer": "FAULT",
                "optical_payload":
                    "READY"
                    if camera is not None
                    else "FAULT"
            }
        }


@app.get("/api/camera/status")
async def camera_status():

    if camera is None:

        return {
            "status": "offline",
            "error":
                camera_error
                or "Camera unavailable"
        }

    try:

        return {
            "status": "online",
            **camera.get_status()
        }

    except Exception as error:

        return {
            "status": "error",
            "error": str(error)
        }


@app.post("/api/camera/capture")
def capture_image():

    if camera is None:

        return {
            "status": "error",
            "error":
                camera_error
                or "Camera unavailable"
        }

    try:

        telemetry_snapshot = (
            get_telemetry()
        )

        frame = camera.capture(
            telemetry_snapshot
        )

        return {
            "status": "ok",
            "frame": frame
        }

    except Exception as error:

        return {
            "status": "error",
            "error": str(error)
        }


@app.get("/api/camera/images")
def camera_images():

    if camera is None:

        return {
            "status": "offline",
            "frames": []
        }

    try:

        return {
            "status": "online",
            "frames":
                camera.list_frames()
        }

    except Exception as error:

        return {
            "status": "error",
            "frames": [],
            "error": str(error)
        }


@app.delete("/api/camera/frames")
def clear_camera_archive():

    if camera is None:

        return {
            "status": "error",
            "error":
                camera_error
                or "Camera unavailable"
        }

    try:

        result = (
            camera.clear_archive()
        )

        return {
            "status": "ok",
            **result
        }

    except Exception as error:

        return {
            "status": "error",
            "error": str(error)
        }


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )