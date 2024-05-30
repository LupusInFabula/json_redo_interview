from collections.abc import Iterator
from csv import DictReader, DictWriter
from inspect import Traceback
from itertools import islice
from pathlib import Path
from typing import TYPE_CHECKING, Self, TypeVar

from json_redo_interview.config import CRASH_RECOVERY_FILE_PATH

if TYPE_CHECKING:
    from json_redo_interview.db import FakeDB

T = TypeVar("T")


class CrashRecovery:
    """
    Assumes that the events in the event_source will not change order between runs.

    As the DB we are using is not persistent, we keep track of the number of already processed items
    by writing and reading to and from a file.
    This way we can resume processing from the last processed item in case of a crash.
    """

    crash_recovery_file = Path(CRASH_RECOVERY_FILE_PATH)

    def __init__(self, event_source: str, db_session: "FakeDB") -> None:
        self.event_source = event_source
        self.db_session = db_session
        self.restore_point = self._load_restore_point()

    def _load_restore_point(self) -> dict:
        restore = {}
        if self.crash_recovery_file.exists():
            with self.crash_recovery_file.open() as f:
                reader = DictReader(f)
                for row in reader:
                    restore[row["event_source"]] = int(row["tot_processed"])

        return restore

    def resume_if_needed(self, events: Iterator[T]) -> Iterator[T]:
        if processed_n := self.restore_point.get(self.event_source):
            self.db_session.tot_processed = processed_n
            return islice(events, processed_n, None)

        return events

    def save_restore_point(self) -> None:
        with self.crash_recovery_file.open("w") as f:
            writer = DictWriter(f, fieldnames=["event_source", "tot_processed"])
            writer.writeheader()
            writer.writerow({"event_source": self.event_source, "tot_processed": self.db_session.tot_processed})

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: type[Exception] | None, exc_val: Exception | None, exc_tb: Traceback | None) -> None:
        if exc_val:
            self.save_restore_point()
        elif self.crash_recovery_file.exists():
            self.crash_recovery_file.unlink()
