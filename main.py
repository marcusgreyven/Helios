from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from camera import HeliosCamera
from events import EventLog
from flight import FlightController
from telemetry import get_telemetry


BASE_DIR = Path(
    __file__
).resolve().parent

STATIC_DIR = (
    BASE_DIR
    / "static"
)

TEMPLATES_DIR = (
    BASE_DIR
    / "templates"
)

CAPTURES_DIR = (
    BASE_DIR
    / "captures"
)

RUNTIME_DIR = (
    BASE_DIR
    / "runtime"
)


CAPTURES_DIR.mkdir(
    parents=True,
    exist_ok=True
)

RUNTIME_DIR.mkdir(
    parents=True,
    exist_ok=True
)


event_log = EventLog(
    RUNTIME_DIR
    / "events.jsonl"
)

flight = FlightController(
    event_log
)


app = FastAPI(
    title="Helios Flight Control",
    version="0.4"
)


app.mount(
    "/static",
    StaticFiles(
        directory=STATIC_DIR
    ),
    name="static"
)

app.mount(
    "/captures",
    StaticFiles(
        directory=CAPTURES_DIR
    ),
    name="captures"
)


templates = (
    Jinja2Templates(
        directory=TEMPLATES_DIR
    )
)


camera = None
camera_error = None

telemetry_fault_active = False


try:

    camera = HeliosCamera(
        CAPTURES_DIR
    )

    event_log.add(
        "PAYLOAD",
        "CAM01 ONLINE / OV5647"
    )

except Exception as error:

    camera_error = str(
        error
    )

    event_log.add(
        "PAYLOAD",
        (
            "CAM01 INITIALIZATION FAULT / "
            + camera_error
        ),
        "ERROR"
    )


try:

    get_telemetry()

    event_log.add(
        "ADCS",
        "IMU TELEMETRY ONLINE"
    )

    event_log.add(
        "BARO",
        "PRESSURE TELEMETRY ONLINE"
    )

    flight.set_mode(
        "STANDBY",
        reason="initialization complete"
    )

    flight.set_mode(
        "NOMINAL",
        reason="flight systems available"
    )

except Exception as error:

    event_log.add(
        "ADCS",
        (
            "TELEMETRY INITIALIZATION FAULT / "
            + str(error)
        ),
        "ERROR"
    )

    flight.enter_safe(
        "telemetry initialization fault"
    )


def system_status():

    optical_payload = (
        "FAULT"
        if camera is None
        else (
            "ACTIVE"
            if flight.mode
            == "PAYLOAD"
            else "READY"
        )
    )

    return {
        "flight_computer":
            "NOMINAL",

        "accelerometer":
            (
                "FAULT"
                if telemetry_fault_active
                else "NOMINAL"
            ),

        "gyroscope":
            (
                "FAULT"
                if telemetry_fault_active
                else "NOMINAL"
            ),

        "magnetometer":
            "NO DATA",

        "barometer":
            (
                "FAULT"
                if telemetry_fault_active
                else "NOMINAL"
            ),

        "optical_payload":
            optical_payload
    }


@app.get(
    "/",
    response_class=HTMLResponse
)
async def index(
    request: Request
):

    return (
        templates.TemplateResponse(
            request=request,
            name="index.html"
        )
    )


@app.get(
    "/api/telemetry"
)
async def telemetry():

    global telemetry_fault_active

    timestamp = (
        datetime.now(
            timezone.utc
        ).isoformat()
    )

    try:

        data = (
            get_telemetry()
        )

        if telemetry_fault_active:

            telemetry_fault_active = (
                False
            )

            event_log.add(
                "TM",
                "TELEMETRY RECOVERED"
            )

        return {
            "status":
                "online",

            "vehicle":
                "HLS-01",

            "mode":
                flight.mode,

            "timestamp":
                timestamp,

            "systems":
                system_status(),

            **data
        }

    except Exception as error:

        if not telemetry_fault_active:

            telemetry_fault_active = (
                True
            )

            event_log.add(
                "TM",
                (
                    "TELEMETRY FAULT / "
                    + str(error)
                ),
                "ERROR"
            )

            try:
                flight.enter_safe(
                    "telemetry fault"
                )
            except ValueError:
                pass

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "error",

                "vehicle":
                    "HLS-01",

                "mode":
                    flight.mode,

                "timestamp":
                    timestamp,

                "systems":
                    system_status(),

                "error":
                    str(error)
            }
        )


@app.get(
    "/api/flight/mode"
)
def get_flight_mode():

    return {
        "status":
            "ok",

        "mode":
            flight.mode
    }


@app.post(
    "/api/flight/mode/{requested_mode}"
)
def set_flight_mode(
    requested_mode: str
):

    requested_mode = (
        requested_mode
        .upper()
        .strip()
    )

    event_log.add(
        "CMD",
        (
            "MODE."
            + requested_mode
            + " RECEIVED"
        )
    )


    if requested_mode == "PAYLOAD":

        event_log.add(
            "CMD",
            (
                "MODE.PAYLOAD REJECTED / "
                "payload mode is automatic"
            ),
            "WARN"
        )

        return JSONResponse(
            status_code=409,
            content={
                "status":
                    "error",

                "mode":
                    flight.mode,

                "error":
                    (
                        "PAYLOAD mode is "
                        "managed automatically."
                    )
            }
        )


    try:

        flight.set_mode(
            requested_mode,
            reason="ground command"
        )

        event_log.add(
            "CMD",
            (
                "MODE."
                + requested_mode
                + " COMPLETED"
            )
        )

        return {
            "status":
                "ok",

            "mode":
                flight.mode
        }

    except ValueError as error:

        event_log.add(
            "CMD",
            (
                "MODE."
                + requested_mode
                + " REJECTED / "
                + str(error)
            ),
            "WARN"
        )

        return JSONResponse(
            status_code=409,
            content={
                "status":
                    "error",

                "mode":
                    flight.mode,

                "error":
                    str(error)
            }
        )


@app.get(
    "/api/events"
)
def get_events(
    limit: int = 60
):

    return {
        "status":
            "ok",

        "events":
            event_log.latest(
                limit=limit
            )
    }


@app.get(
    "/api/camera/status"
)
async def camera_status():

    if camera is None:

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "offline",

                "error":
                    (
                        camera_error
                        or
                        "Camera unavailable"
                    )
            }
        )

    try:

        return {
            "status":
                "online",

            **camera.get_status()
        }

    except Exception as error:

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "error",

                "error":
                    str(error)
            }
        )


@app.post(
    "/api/camera/capture"
)
def capture_image():

    if camera is None:

        event_log.add(
            "CMD",
            (
                "CAM01.CAPTURE REJECTED / "
                "camera unavailable"
            ),
            "WARN"
        )

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "error",

                "error":
                    (
                        camera_error
                        or
                        "Camera unavailable"
                    )
            }
        )


    event_log.add(
        "CMD",
        "CAM01.CAPTURE RECEIVED"
    )


    if flight.mode != "NOMINAL":

        message = (
            "Capture requires NOMINAL mode. "
            f"Current mode: {flight.mode}"
        )

        event_log.add(
            "CMD",
            (
                "CAM01.CAPTURE REJECTED / "
                + message
            ),
            "WARN"
        )

        return JSONResponse(
            status_code=409,
            content={
                "status":
                    "error",

                "error":
                    message
            }
        )


    try:

        event_log.add(
            "CMD",
            "CAM01.CAPTURE ACCEPTED"
        )

        flight.set_mode(
            "PAYLOAD",
            reason="CAM01 capture"
        )

        event_log.add(
            "PAYLOAD",
            "CAM01 ACQUISITION STARTED"
        )


        telemetry_snapshot = (
            get_telemetry()
        )

        frame = (
            camera.capture(
                telemetry_snapshot
            )
        )


        event_log.add(
            "PAYLOAD",
            (
                frame["frame_id"]
                + " ACQUIRED"
            )
        )

        flight.set_mode(
            "NOMINAL",
            reason="payload operation complete"
        )

        event_log.add(
            "CMD",
            "CAM01.CAPTURE COMPLETED"
        )


        return {
            "status":
                "ok",

            "frame":
                frame
        }

    except Exception as error:

        event_log.add(
            "PAYLOAD",
            (
                "CAM01 ACQUISITION FAULT / "
                + str(error)
            ),
            "ERROR"
        )

        if flight.mode == "PAYLOAD":

            try:
                flight.set_mode(
                    "NOMINAL",
                    reason="payload operation aborted"
                )
            except ValueError:
                pass

        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "error",

                "error":
                    str(error)
            }
        )


@app.get(
    "/api/camera/images"
)
def camera_images():

    if camera is None:

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "offline",

                "frames":
                    []
            }
        )

    try:

        return {
            "status":
                "online",

            "frames":
                camera.list_frames()
        }

    except Exception as error:

        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "error",

                "frames":
                    [],

                "error":
                    str(error)
            }
        )


@app.delete(
    "/api/camera/frames"
)
def clear_camera_archive():

    if camera is None:

        return JSONResponse(
            status_code=503,
            content={
                "status":
                    "error",

                "error":
                    (
                        camera_error
                        or
                        "Camera unavailable"
                    )
            }
        )


    event_log.add(
        "CMD",
        "CAM01.CLEAR_ARCHIVE RECEIVED"
    )


    try:

        result = (
            camera.clear_archive()
        )

        event_log.add(
            "STORAGE",
            (
                "OPTICAL ARCHIVE CLEARED / "
                f"{result['deleted_frames']} "
                "frames"
            )
        )

        event_log.add(
            "CMD",
            "CAM01.CLEAR_ARCHIVE COMPLETED"
        )

        return {
            "status":
                "ok",

            **result
        }

    except Exception as error:

        event_log.add(
            "STORAGE",
            (
                "ARCHIVE CLEAR FAULT / "
                + str(error)
            ),
            "ERROR"
        )

        return JSONResponse(
            status_code=500,
            content={
                "status":
                    "error",

                "error":
                    str(error)
            }
        )


if __name__ == "__main__":

    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )
