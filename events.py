import json
import threading

from collections import deque
from datetime import datetime, timezone
from pathlib import Path


class EventLog:

    def __init__(
        self,
        path,
        max_events=500
    ):
        self.path = Path(path)
        self.max_events = max_events

        self.path.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.lock = threading.Lock()

        self.events = deque(
            maxlen=max_events
        )

        self._load()


    def _load(self):

        if not self.path.exists():
            return

        try:
            with self.path.open(
                "r",
                encoding="utf-8"
            ) as file:

                for line in file:

                    line = line.strip()

                    if not line:
                        continue

                    try:
                        event = json.loads(
                            line
                        )

                        self.events.append(
                            event
                        )

                    except json.JSONDecodeError:
                        continue

        except OSError:
            pass


    def add(
        self,
        source,
        message,
        level="INFO"
    ):

        event = {
            "timestamp":
                datetime.now(
                    timezone.utc
                ).isoformat(),

            "source":
                source.upper(),

            "level":
                level.upper(),

            "message":
                message
        }

        with self.lock:

            self.events.append(
                event
            )

            try:
                with self.path.open(
                    "a",
                    encoding="utf-8"
                ) as file:

                    file.write(
                        json.dumps(
                            event,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

                self._compact_if_needed()

            except OSError:
                pass

        return event


    def latest(
        self,
        limit=50
    ):

        limit = max(
            1,
            min(
                int(limit),
                self.max_events
            )
        )

        with self.lock:
            events = list(
                self.events
            )

        return events[-limit:]


    def _compact_if_needed(self):

        try:
            if (
                not self.path.exists()
                or self.path.stat().st_size
                < 2_000_000
            ):
                return

            with self.path.open(
                "w",
                encoding="utf-8"
            ) as file:

                for event in self.events:
                    file.write(
                        json.dumps(
                            event,
                            ensure_ascii=False
                        )
                        + "\n"
                    )

        except OSError:
            pass
