from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from telemetry import get_telemetry
from datetime import datetime, timezone
from pathlib import Path
from camera import HeliosCamera

app = FastAPI(
    title="Helios",
    version="0.1"
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

BASE_DIR = Path(__file__).resolve().parent

camera = HeliosCamera(
    BASE_DIR / "captures"
)

app.mount(
    "/captures",
    StaticFiles(directory=BASE_DIR / "captures"),
    name="captures"
)

templates = Jinja2Templates(directory="templates")


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/api/telemetry")
async def telemetry():
    try:
        data = get_telemetry()

        return {
            "status": "online",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            **data
        }

    except Exception as error:
        return {
            "status": "error",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "error": str(error)
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=False
    )

@app.post("/api/camera/capture")
def capture_image():
    try:
        filename = camera.capture()

        return {
            "status": "ok",
            "filename": filename,
            "url": f"/captures/{filename}"
        }

    except Exception as error:
        return {
            "status": "error",
            "error": str(error)
        }

@app.get("/api/camera/images")
def camera_images():
    capture_dir = BASE_DIR / "captures"

    images = sorted(
        capture_dir.glob("*.jpg"),
        key=lambda image: image.stat().st_mtime,
        reverse=True
    )

    return {
        "images": [
            {
                "filename": image.name,
                "url": f"/captures/{image.name}"
            }
            for image in images
        ]
    }