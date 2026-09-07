const captureButton =
    document.getElementById(
        "capture-button"
    );

const cameraImage =
    document.getElementById(
        "camera-image"
    );

const cameraGallery =
    document.getElementById(
        "camera-gallery"
    );

const payloadStatus =
    document.getElementById(
        "payload-status"
    );

const noFrame =
    document.getElementById(
        "no-frame"
    );


function frameNumber(
    value,
    digits = 3
) {

    if (
        value === null ||
        value === undefined ||
        typeof value !== "number"
    ) {
        return "---";
    }

    return value.toFixed(
        digits
    );
}


function frameUtc(timestamp) {

    if (!timestamp) {
        return "---";
    }

    return new Date(
        timestamp
    )
        .toISOString()
        .substring(11, 23)
        + "Z";
}


function renderFrame(frame) {

    if (!frame) {
        return;
    }


    cameraImage.src =
        frame.url
        + "?t="
        + Date.now();


    cameraImage.style.display =
        "block";

    noFrame.style.display =
        "none";


    document.getElementById(
        "frame-name"
    ).textContent =
        frame.frame_id || "---";


    document.getElementById(
        "frame-time"
    ).textContent =
        frameUtc(
            frame.captured_at
        );


    const telemetry =
        frame.telemetry;


    if (!telemetry) {

        document.getElementById(
            "frame-accel"
        ).textContent = "---";

        document.getElementById(
            "frame-rate"
        ).textContent = "---";

        document.getElementById(
            "frame-pressure"
        ).textContent = "---";

        return;
    }


    const imu =
        telemetry.imu;


    document.getElementById(
        "frame-accel"
    ).textContent =
        frameNumber(
            imu.acceleration
                .magnitude,
            2
        )
        + " m/s²";


    document.getElementById(
        "frame-rate"
    ).textContent =
        frameNumber(
            imu.angular_rate.x,
            2
        )
        + " °/s";


    document.getElementById(
        "frame-pressure"
    ).textContent =
        frameNumber(
            imu.pressure,
            2
        )
        + " hPa";
}


async function captureFrame() {

    captureButton.disabled =
        true;

    captureButton.textContent =
        "ACQUIRING...";

    payloadStatus.textContent =
        "ACQUIRING";


    try {

        const response =
            await fetch(
                "/api/camera/capture",
                {
                    method: "POST"
                }
            );

        const data =
            await response.json();


        if (
            !response.ok ||
            data.status !== "ok"
        ) {

            payloadStatus.textContent =
                "FAULT";

            return;
        }


        payloadStatus.textContent =
            "FRAME ACQUIRED";


        renderFrame(
            data.frame
        );


        await loadFrames();

    }

    catch (error) {

        payloadStatus.textContent =
            "OFFLINE";
    }

    finally {

        captureButton.disabled =
            false;

        captureButton.textContent =
            "CAPTURE FRAME";
    }
}


async function loadFrames() {

    try {

        const response =
            await fetch(
                "/api/camera/images"
            );

        const data =
            await response.json();


        cameraGallery.innerHTML =
            "";


        if (
            !data.frames ||
            data.frames.length === 0
        ) {

            payloadStatus.textContent =
                "STANDBY";

            return;
        }


        for (
            const frame
            of data.frames
        ) {

            const button =
                document.createElement(
                    "button"
                );


            button.className =
                "gallery-frame";


            const image =
                document.createElement(
                    "img"
                );


            image.src =
                frame.url;


            image.alt =
                frame.frame_id
                || "Helios frame";


            button.appendChild(
                image
            );


            button.addEventListener(
                "click",
                () => {
                    renderFrame(
                        frame
                    );
                }
            );


            cameraGallery.appendChild(
                button
            );
        }


        if (
            !cameraImage.src
        ) {

            renderFrame(
                data.frames[0]
            );
        }


        payloadStatus.textContent =
            "READY";

    }

    catch (error) {

        payloadStatus.textContent =
            "OFFLINE";
    }
}


captureButton.addEventListener(
    "click",
    captureFrame
);


loadFrames();