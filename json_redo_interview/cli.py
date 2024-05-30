from urllib.request import urlopen

import ijson
import typer
from loguru import logger
from pydantic import ValidationError
from rich import print

from json_redo_interview.config import EVENT_SOURCE_FILE_URL
from json_redo_interview.handlers import route_event
from json_redo_interview.schemas import EventSchema

app = typer.Typer(no_args_is_help=True)


@app.command(help="Process events from a remote JSON file.")
def json_redo() -> None:
    with urlopen(EVENT_SOURCE_FILE_URL) as f:
        events = ijson.items(f, "item")
        count = 0
        failed = 0
        for event in events:
            try:
                validated = EventSchema(**event)
            except ValidationError as e:
                logger.info("Validation error: {}", e)
                failed += 1
                continue

            route_event(validated)
            count += 1

        print(f"Successfully processed {count} events, {failed} failed.")


if __name__ == "__main__":
    app()
