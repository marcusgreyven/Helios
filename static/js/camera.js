const captureButton =
    document.getElementById("capture-button");

const cameraImage =
    document.getElementById("camera-image");

const gallery =
    document.getElementById("camera-gallery");


async function captureImage() {

    captureButton.disabled = true;
    captureButton.textContent = "CAPTURING...";

    try {

        const response = await fetch(
            "/api/camera/capture",
            {
                method: "POST"
            }
        );

        const data = await response.json();

        if (data.status === "ok") {

            cameraImage.src =
                data.url + "?t=" + Date.now();

            await loadImages();
        }

    } finally {

        captureButton.disabled = false;
        captureButton.textContent = "CAPTURE";
    }
}


async function loadImages() {

    const response =
        await fetch("/api/camera/images");

    const data =
        await response.json();

    gallery.innerHTML = "";

    for (const image of data.images) {

        const element =
            document.createElement("img");

        element.src = image.url;

        element.className = "gallery-image";

        element.onclick = () => {
            cameraImage.src = image.url;
        };

        gallery.appendChild(element);
    }


    if (
        data.images.length > 0 &&
        !cameraImage.src
    ) {
        cameraImage.src =
            data.images[0].url;
    }
}


captureButton.addEventListener(
    "click",
    captureImage
);


loadImages();