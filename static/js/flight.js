const modeButtons =
    document.querySelectorAll(
        ".mode-command"
    );

const flightCommandResult =
    document.getElementById(
        "flight-command-result"
    );


async function sendModeCommand(
    mode
) {

    modeButtons.forEach(
        button => {
            button.disabled =
                true;
        }
    );


    flightCommandResult.textContent =
        `MODE.${mode} TRANSMITTING`;


    try {

        const response =
            await fetch(
                `/api/flight/mode/${mode}`,
                {
                    method:
                        "POST",

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

            flightCommandResult.textContent =
                "REJECTED / "
                + (
                    data.error
                    || "COMMAND FAILED"
                );

            flightCommandResult.className =
                "mode-command-result "
                + "mode-command-error";

            return;
        }


        flightCommandResult.textContent =
            `MODE.${mode} COMPLETED`;

        flightCommandResult.className =
            "mode-command-result "
            + "mode-command-ok";

    }

    catch (error) {

        flightCommandResult.textContent =
            "COMMAND LINK ERROR";

        flightCommandResult.className =
            "mode-command-result "
            + "mode-command-error";

    }

    finally {

        modeButtons.forEach(
            button => {
                button.disabled =
                    false;
            }
        );
    }
}


modeButtons.forEach(
    button => {

        button.addEventListener(
            "click",
            () => {

                flightCommandResult.className =
                    "mode-command-result";

                sendModeCommand(
                    button.dataset.mode
                );
            }
        );
    }
);
