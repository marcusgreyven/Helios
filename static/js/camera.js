const captureButton =
    document.getElementById(
        "capture-button"
    );

const clearArchiveButton =
    document.getElementById(
        "clear-archive-button"
    );

const confirmDeleteButton =
    document.getElementById(
        "confirm-delete-button"
    );

const cancelDeleteButton =
    document.getElementById(
        "cancel-delete-button"
    );

const archiveModal =
    document.getElementById(
        "archive-modal"
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


let currentFrameCount = 0;


function setText(
    id,
    value
) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


function formatValue(
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


function formatUtc(
    timestamp
) {

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


function formatBytes(
    bytes
) {

    if (
        bytes === null ||
        bytes === undefined
    ) {
        return "---";
    }


    const units = [
        "B",
        "KB",
        "MB",
        "GB",
        "TB"
    ];


    let value = bytes;

    let unitIndex = 0;


    while (
        value >= 1024 &&
        unitIndex <
        units.length - 1
    ) {

        value /= 1024;

        unitIndex += 1;
    }


    const digits =
        value >= 100
            ? 0
            : value >= 10
                ? 1
                : 2;


    return (
        value.toFixed(digits)
        + " "
        + units[unitIndex]
    );
}


function renderFrame(
    frame
) {

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


    setText(
        "frame-name",
        frame.frame_id
        || "---"
    );


    setText(
        "frame-time",
        formatUtc(
            frame.captured_at
        )
    );


    const telemetry =
        frame.telemetry;


    if (!telemetry) {

        setText(
            "frame-accel",
            "---"
        );

        setText(
            "frame-rate",
            "---"
        );

        setText(
            "frame-pressure",
            "---"
        );

        return;
    }


    const imu =
        telemetry.imu;


    setText(
        "frame-accel",

        formatValue(
            imu.acceleration
                .magnitude,
            2
        )
        + " m/s²"
    );


    setText(
        "frame-rate",

        formatValue(
            imu.angular_rate.x,
            2
        )
        + " °/s"
    );


    setText(
        "frame-pressure",

        formatValue(
            imu.pressure,
            2
        )
        + " hPa"
    );
}


function clearFrameDisplay() {

    cameraImage.removeAttribute(
        "src"
    );

    cameraImage.style.display =
        "none";


    noFrame.style.display =
        "flex";


    setText(
        "frame-name",
        "---"
    );

    setText(
        "frame-time",
        "---"
    );

    setText(
        "frame-accel",
        "---"
    );

    setText(
        "frame-rate",
        "---"
    );

    setText(
        "frame-pressure",
        "---"
    );
}


async function updateCameraStatus() {

    try {

        const response =
            await fetch(
                "/api/camera/status",
                {
                    cache:
                        "no-store"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok ||
            data.status !== "online"
        ) {

            payloadStatus.textContent =
                "FAULT";

            setText(
                "system-optical-payload",
                "FAULT"
            );

            return;
        }


        payloadStatus.textContent =
            "READY";


        currentFrameCount =
            data.frame_count;


        setText(
            "frame-count",
            data.frame_count
        );


        setText(
            "archive-size",
            formatBytes(
                data.archive_bytes
            )
        );


        setText(
            "storage-free",
            formatBytes(
                data.disk.free_bytes
            )
        );


        setText(
            "last-frame-time",
            data.last_frame
                ? formatUtc(
                    data.last_frame
                        .timestamp
                )
                : "---"
        );


        setText(
            "modal-frame-count",
            data.frame_count
        );


        clearArchiveButton.disabled =
            data.frame_count === 0;

    }

    catch (error) {

        payloadStatus.textContent =
            "OFFLINE";
    }
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

        await updateCameraStatus();

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
                "/api/camera/images",
                {
                    cache:
                        "no-store"
                }
            );


        const data =
            await response.json();


        cameraGallery.innerHTML =
            "";


        if (
            !data.frames ||
            data.frames.length === 0
        ) {

            clearFrameDisplay();

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


        renderFrame(
            data.frames[0]
        );

    }

    catch (error) {

        payloadStatus.textContent =
            "OFFLINE";
    }
}


function openArchiveModal() {

    if (
        currentFrameCount === 0
    ) {
        return;
    }


    setText(
        "modal-frame-count",
        currentFrameCount
    );


    archiveModal.classList.add(
        "modal-visible"
    );
}


function closeArchiveModal() {

    archiveModal.classList.remove(
        "modal-visible"
    );
}


async function deleteArchive() {

    confirmDeleteButton.disabled =
        true;

    confirmDeleteButton.textContent =
        "DELETING...";


    try {

        const response =
            await fetch(
                "/api/camera/frames",
                {
                    method: "DELETE"
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


        closeArchiveModal();


        cameraGallery.innerHTML =
            "";


        clearFrameDisplay();


        payloadStatus.textContent =
            "ARCHIVE CLEARED";


        await updateCameraStatus();

    }

    catch (error) {

        payloadStatus.textContent =
            "FAULT";
    }

    finally {

        confirmDeleteButton.disabled =
            false;

        confirmDeleteButton.textContent =
            "DELETE ARCHIVE";
    }
}


captureButton.addEventListener(
    "click",
    captureFrame
);


clearArchiveButton.addEventListener(
    "click",
    openArchiveModal
);


cancelDeleteButton.addEventListener(
    "click",
    closeArchiveModal
);


confirmDeleteButton.addEventListener(
    "click",
    deleteArchive
);


archiveModal.addEventListener(
    "click",
    event => {

        if (
            event.target ===
            archiveModal
        ) {

            closeArchiveModal();
        }
    }
);


document.addEventListener(
    "keydown",
    event => {

        if (
            event.key === "Escape"
        ) {

            closeArchiveModal();
        }
    }
);


loadFrames();

updateCameraStatus();


setInterval(
    updateCameraStatus,
    2000
);