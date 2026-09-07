let lastPacketReceivedAt = null;

let packetCounter = 0;


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
        state === "NOMINAL"
        || state === "READY"
        || state === "ACTIVE"
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


function setModeState(
    mode
) {

    const element =
        document.getElementById(
            "mode"
        );

    if (!element) {
        return;
    }

    element.textContent =
        mode;

    element.className =
        "mode-state";


    const classMap = {
        "BOOT":
            "mode-boot",

        "STANDBY":
            "mode-standby",

        "NOMINAL":
            "mode-nominal",

        "PAYLOAD":
            "mode-payload",

        "SAFE":
            "mode-safe"
    };


    const className =
        classMap[mode];

    if (className) {
        element.classList.add(
            className
        );
    }


    document
        .querySelectorAll(
            ".mode-command"
        )
        .forEach(
            button => {

                button.classList.toggle(
                    "mode-command-active",
                    button.dataset.mode
                    === mode
                );
            }
        );
}


function updateAttitude(
    attitude
) {

    if (!attitude) {
        return;
    }


    setText(
        "attitude-roll",
        formatNumber(
            attitude.roll,
            2
        )
    );

    setText(
        "attitude-pitch",
        formatNumber(
            attitude.pitch,
            2
        )
    );

    setText(
        "attitude-yaw",
        (
            typeof attitude.yaw
            === "number"
        )
            ? formatNumber(
                attitude.yaw,
                2
            ) + "°"
            : "NO SOLUTION"
    );

    setText(
        "attitude-rate",
        formatNumber(
            attitude.rate_magnitude,
            2
        )
    );

    setText(
        "attitude-solution",
        attitude.solution
        || "---"
    );

    setText(
        "attitude-frame",
        attitude.reference_frame
        || "---"
    );


    const state =
        document.getElementById(
            "attitude-state"
        );

    if (state) {

        state.textContent =
            attitude.state
            || "---";

        state.className =
            "attitude-state";

        state.classList.add(
            attitude.state
            === "STABLE"
                ? "attitude-stable"
                : "attitude-dynamic"
        );
    }


    const horizon =
        document.getElementById(
            "attitude-horizon"
        );

    if (
        horizon
        && typeof attitude.roll
        === "number"
        && typeof attitude.pitch
        === "number"
    ) {

        const pitchPixels =
            Math.max(
                -55,
                Math.min(
                    55,
                    attitude.pitch * 1.4
                )
            );


        horizon.style.transform =
            `translateY(${pitchPixels}px) `
            + `rotate(${-attitude.roll}deg)`;
    }
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
                    cache:
                        "no-store"
                }
            );


        const data =
            await response.json();


        if (
            !response.ok
            || data.status
            !== "online"
        ) {

            status.textContent =
                "● OFFLINE";

            status.className =
                "status status-offline";

            setModeState(
                data.mode
                || "SAFE"
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


        setModeState(
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
            magnetic.x !== null
            || magnetic.y !== null
            || magnetic.z !== null;


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


        updateAttitude(
            data.attitude
        );

    }

    catch (exception) {

        status.textContent =
            "● OFFLINE";

        status.className =
            "status status-offline";

        error.textContent =
            exception.toString();
    }
}


function updatePacketAge() {

    if (
        lastPacketReceivedAt
        === null
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

        setText(
            "telemetry-rate",
            packetCounter
            + " Hz"
        );

        packetCounter = 0;

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
