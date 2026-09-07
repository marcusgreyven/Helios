function formatNumber(value, digits = 3) {

    if (
        value === null ||
        value === undefined ||
        typeof value !== "number"
    ) {
        return "—";
    }

    return value.toFixed(digits);
}


function setText(id, value) {

    const element =
        document.getElementById(id);

    if (element) {
        element.textContent = value;
    }
}


function formatUtc(timestamp) {

    if (!timestamp) {
        return "---";
    }

    const date =
        new Date(timestamp);

    return date.toISOString()
        .substring(11, 23)
        + "Z";
}


async function updateTelemetry() {

    const status =
        document.getElementById(
            "status"
        );

    const error =
        document.getElementById(
            "error"
        );


    try {

        const response =
            await fetch(
                "/api/telemetry"
            );

        const data =
            await response.json();


        if (
            !response.ok ||
            data.status !== "online"
        ) {

            status.textContent =
                "● OFFLINE";

            status.className =
                "status status-offline";

            setText(
                "mode",
                "DEGRADED"
            );

            error.textContent =
                data.error
                || "Telemetry unavailable";

            return;
        }


        status.textContent =
            "● ONLINE";

        status.className =
            "status status-online";


        setText(
            "mode",
            data.mode
        );


        setText(
            "packet-time",
            formatUtc(
                data.timestamp
            )
        );


        setText(
            "utc-time",
            formatUtc(
                data.timestamp
            )
        );


        error.textContent = "";


        const imu =
            data.imu;


        const acceleration =
            imu.acceleration;


        setText(
            "accel-x",
            formatNumber(
                acceleration.x
            )
        );

        setText(
            "accel-y",
            formatNumber(
                acceleration.y
            )
        );

        setText(
            "accel-z",
            formatNumber(
                acceleration.z
            )
        );


        setText(
            "accel-mag",
            formatNumber(
                acceleration.magnitude,
                3
            )
        );


        setText(
            "accel-g",
            formatNumber(
                acceleration.g,
                3
            )
        );


        const rate =
            imu.angular_rate;


        setText(
            "rate-x",
            formatNumber(
                rate.x
            )
        );

        setText(
            "rate-y",
            formatNumber(
                rate.y
            )
        );

        setText(
            "rate-z",
            formatNumber(
                rate.z
            )
        );


        const magnetic =
            imu.magnetic_field;


        setText(
            "mag-x",
            formatNumber(
                magnetic.x
            )
        );

        setText(
            "mag-y",
            formatNumber(
                magnetic.y
            )
        );

        setText(
            "mag-z",
            formatNumber(
                magnetic.z
            )
        );


        const magneticAvailable =
            magnetic.x !== null ||
            magnetic.y !== null ||
            magnetic.z !== null;


        setText(
            "mag-status",
            magneticAvailable
                ? "ACTIVE"
                : "NO DATA"
        );


        setText(
            "pressure",
            formatNumber(
                imu.pressure,
                2
            )
        );

    }

    catch (exception) {

        status.textContent =
            "● OFFLINE";

        status.className =
            "status status-offline";


        setText(
            "mode",
            "DEGRADED"
        );


        error.textContent =
            exception.toString();
    }
}


updateTelemetry();


setInterval(
    updateTelemetry,
    500
);