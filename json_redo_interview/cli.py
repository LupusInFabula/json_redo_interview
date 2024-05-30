from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import islice
from typing import TypeVar
from urllib.request import urlopen

import ijson
import typer
from rich import print

from json_redo_interview.config import EVENT_SOURCE_FILE_URL, MAX_THREAD_WORKERS
from json_redo_interview.crash_recovery import CrashRecovery
from json_redo_interview.db import db_session
from json_redo_interview.handlers import process_event

T = TypeVar("T")

app = typer.Typer(no_args_is_help=True)


def _batched(iterable: Iterable[T], n: int) -> Iterable[list[T]]:
    while True:
        batch = list(islice(iterable, n))
        if not batch:
            return

        yield batch


@app.command(help="Process events from a remote JSON file.")
def json_redo() -> None:
    thread_pool = ThreadPoolExecutor(max_workers=MAX_THREAD_WORKERS)
    process_event_with_db = partial(process_event, db_session=db_session)

    with CrashRecovery(EVENT_SOURCE_FILE_URL, db_session) as cr, urlopen(EVENT_SOURCE_FILE_URL) as source:
        events = ijson.items(source, "item")
        events = cr.resume_if_needed(events)

        for batch in _batched(events, MAX_THREAD_WORKERS):
            thread_pool.map(process_event_with_db, batch)

    thread_pool.shutdown(wait=True)
    print(f"Processed {db_session.tot_processed} events, {db_session.row_count} failed.")


if __name__ == "__main__":
    app()
