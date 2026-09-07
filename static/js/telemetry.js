let lastPacketReceivedAt = null;

let packetCounter = 0;

let telemetryRate = 0;


function formatNumber(
    value,
    digits = 3
) {

    if (
        value === null ||
        value === undefined ||
        typeof value !== "number"
    ) {
        return "—";
    }

    return value.toFixed(
        digits
    );
}


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


function setSystemState(
    id,
    state
) {

    const element =
        document.getElementById(id);

    if (!element) {
        return;
    }

    element.textContent =
        state;


    element.className =
        "system-state";


    if (
        state === "NOMINAL" ||
        state === "READY"
    ) {

        element.classList.add(
            "state-nominal"
        );

        return;
    }


    if (
        state === "NO DATA"
    ) {

        element.classList.add(
            "state-no-data"
        );

        return;
    }


    element.classList.add(
        "state-fault"
    );
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
                "/api/telemetry",
                {
                    cache: "no-store"
                }
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


        lastPacketReceivedAt =
            performance.now();

        packetCounter += 1;


        status.textContent =
            "● ONLINE";

        status.className =
            "status status-online";


        setText(
            "mode",
            data.mode
        );


        setText(
            "utc-time",
            formatUtc(
                data.timestamp
            )
        );


        error.textContent =
            "";


        const systems =
            data.systems;


        setSystemState(
            "system-flight-computer",
            systems.flight_computer
        );

        setSystemState(
            "system-accelerometer",
            systems.accelerometer
        );

        setSystemState(
            "system-gyroscope",
            systems.gyroscope
        );

        setSystemState(
            "system-magnetometer",
            systems.magnetometer
        );

        setSystemState(
            "system-barometer",
            systems.barometer
        );

        setSystemState(
            "system-optical-payload",
            systems.optical_payload
        );


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
                acceleration.magnitude
            )
        );


        setText(
            "accel-g",
            formatNumber(
                acceleration.g
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


function updatePacketAge() {

    if (
        lastPacketReceivedAt === null
    ) {

        setText(
            "packet-age",
            "--- ms"
        );

        return;
    }


    const age =
        performance.now()
        - lastPacketReceivedAt;


    setText(
        "packet-age",
        Math.round(age)
        + " ms"
    );


    const status =
        document.getElementById(
            "status"
        );


    if (age > 1500) {

        status.textContent =
            "● LINK LOST";

        status.className =
            "status status-offline";
    }
}


setInterval(
    () => {

        telemetryRate =
            packetCounter;

        packetCounter = 0;


        setText(
            "telemetry-rate",
            telemetryRate
            + " Hz"
        );

    },
    1000
);


setInterval(
    updatePacketAge,
    50
);


updateTelemetry();


setInterval(
    updateTelemetry,
    50
);