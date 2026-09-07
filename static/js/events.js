const eventLog =
    document.getElementById(
        "event-log"
    );


function eventUtc(
    timestamp
) {

    if (!timestamp) {
        return "---";
    }

    return new Date(
        timestamp
    )
        .toISOString()
        .substring(11, 23);
}


function createEventRow(
    event
) {

    const row =
        document.createElement(
            "div"
        );

    row.className =
        "event-row";


    if (
        event.level
        === "ERROR"
    ) {
        row.classList.add(
            "event-row-error"
        );
    }

    else if (
        event.level
        === "WARN"
    ) {
        row.classList.add(
            "event-row-warn"
        );
    }


    const time =
        document.createElement(
            "span"
        );

    time.textContent =
        eventUtc(
            event.timestamp
        );


    const source =
        document.createElement(
            "span"
        );

    source.textContent =
        event.source
        || "---";


    const level =
        document.createElement(
            "span"
        );

    level.textContent =
        event.level
        || "INFO";


    const message =
        document.createElement(
            "span"
        );

    message.textContent =
        event.message
        || "";


    row.append(
        time,
        source,
        level,
        message
    );


    return row;
}


async function updateEvents() {

    if (!eventLog) {
        return;
    }


    try {

        const response =
            await fetch(
                "/api/events?limit=60",
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
            !== "ok"
        ) {
            return;
        }


        const nearBottom =
            (
                eventLog.scrollHeight
                - eventLog.scrollTop
                - eventLog.clientHeight
            )
            < 40;


        eventLog.innerHTML =
            "";


        if (
            !data.events
            || data.events.length
            === 0
        ) {

            const empty =
                document.createElement(
                    "div"
                );

            empty.className =
                "event-empty";

            empty.textContent =
                "NO EVENTS";

            eventLog.appendChild(
                empty
            );

            return;
        }


        for (
            const event
            of data.events
        ) {

            eventLog.appendChild(
                createEventRow(
                    event
                )
            );
        }


        if (nearBottom) {

            eventLog.scrollTop =
                eventLog.scrollHeight;
        }

    }

    catch (error) {
        // Event stream should not interfere
        // with the rest of Mission Control.
    }
}


updateEvents();


setInterval(
    updateEvents,
    750
);
