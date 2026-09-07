function formatValue(value) {
    if (typeof value !== "number") {
        return "—";
    }

    return value.toFixed(3);
}


function setValue(id, value) {
    document.getElementById(id).textContent =
        formatValue(value);
}


async function updateTelemetry() {

    const status =
        document.getElementById("status");

    const error =
        document.getElementById("error");

    try {

        const response =
            await fetch("/api/telemetry");

        const data =
            await response.json();


        if (data.status !== "online") {

            status.textContent = "ERROR";
            status.className = "status offline";

            error.textContent =
                data.error || "Telemetry error";

            return;
        }


        status.textContent = "ONLINE";
        status.className = "status online";

        error.textContent = "";

        document.getElementById(
            "timestamp"
        ).textContent = data.timestamp;


        const imu = data.imu;


        setValue(
            "accel-x",
            imu.acceleration.x
        );

        setValue(
            "accel-y",
            imu.acceleration.y
        );

        setValue(
            "accel-z",
            imu.acceleration.z
        );


        setValue(
            "gyro-x",
            imu.gyro.x
        );

        setValue(
            "gyro-y",
            imu.gyro.y
        );

        setValue(
            "gyro-z",
            imu.gyro.z
        );


        setValue(
            "mag-x",
            imu.magnetic.x
        );

        setValue(
            "mag-y",
            imu.magnetic.y
        );

        setValue(
            "mag-z",
            imu.magnetic.z
        );


        setValue(
            "pressure",
            imu.pressure
        );

    }

    catch (err) {

        status.textContent = "OFFLINE";
        status.className = "status offline";

        error.textContent = err.toString();
    }
}


updateTelemetry();

setInterval(
    updateTelemetry,
    500
);